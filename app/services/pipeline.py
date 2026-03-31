"""
Controller pipeline: orchestrates the full resume processing flow.
  1. Extract text from file
  2. Parse resume (heuristic + optional Gemini)
  3. Normalize skills
  4. Compute job match
  5. Persist candidate with audit trail
"""
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.parser_service import parse_resume
from app.services.skill_normalizer import normalize_skills
from app.services.matching_engine import compute_match
from app.services.audit_service import AuditService
from app.services.gemini_service import enrich_parse_with_gemini, enrich_match_with_gemini
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.job_repo import JobRepository
from app.config import settings


async def process_resume(
    db: AsyncSession,
    raw_text: str,
    job_id: uuid.UUID,
    recruiter_id: uuid.UUID,
    source_filename: Optional[str] = None,
    resume_bytes: Optional[bytes] = None,
    resume_mime: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full pipeline: parse → normalize → match → persist → audit.
    Returns the persisted candidate dict.
    """
    audit = AuditService(db)
    candidate_repo = CandidateRepository(db)
    job_repo = JobRepository(db)

    # Load job
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")

    job_dict = {
        "required_skills": job.required_skills or [],
        "nice_to_have_skills": job.nice_to_have_skills or [],
        "experience_min_years": job.experience_min_years,
        "experience_max_years": job.experience_max_years,
        "required_projects": job.required_projects or [],
        "title": job.title,
    }

    # Step 1: Create stub candidate
    candidate = await candidate_repo.create({
        "job_id": job_id,
        "recruiter_id": recruiter_id,
        "raw_resume_text": raw_text,
        "source_filename": source_filename,
        "resume_bytes": resume_bytes,
        "resume_mime": resume_mime,
        "parse_status": "processing",
    })
    cid = candidate.id

    try:
        # Step 2: Parse resume
        parsed = parse_resume(raw_text)
        await audit.log_ok(cid, "parse", f"Parsed {len(raw_text)} chars", {"fields_extracted": list(parsed.keys())})

        # Step 3: Gemini enrichment (optional)
        if settings.ENABLE_GEMINI:
            gemini_parsed = await enrich_parse_with_gemini(raw_text)
            if gemini_parsed:
                # Merge Gemini results into parsed (Gemini wins for non-null values)
                for k, v in gemini_parsed.items():
                    if v and (not parsed.get(k)):
                        parsed[k] = v
                await audit.log_ok(cid, "gemini_parse", "Gemini enrichment applied")
            else:
                await audit.log_warn(cid, "gemini_parse", "Gemini enrichment skipped or failed")

        # Step 4: Normalize skills
        raw_skills = parsed.get("raw_skills", [])
        normalized, explicit, inferred, ambiguous = normalize_skills(raw_skills)
        parsed["normalized_skills"] = normalized
        parsed["inferred_skills"] = inferred
        parsed["ambiguous_skills"] = ambiguous
        await audit.log_ok(
            cid, "skill_normalize",
            f"Normalized {len(normalized)}, inferred {len(inferred)}, ambiguous {len(ambiguous)}",
            {"normalized": normalized, "inferred": inferred, "ambiguous": ambiguous}
        )

        # Step 5: Compute match
        match_result = compute_match(parsed, job_dict)
        parsed.update(match_result)
        await audit.log_ok(
            cid, "matching",
            f"Score: {match_result['match_score']}, Bucket: {match_result['bucket']}",
            match_result["score_breakdown"]
        )

        # Step 6: Gemini match enrichment (optional primary scoring)
        if settings.ENABLE_GEMINI:
            gemini_match = await enrich_match_with_gemini(parsed, job_dict)
            if gemini_match:
                parsed["gemini_insights"] = gemini_match
                # Overwrite scores with Gemini assessment if available
                ai_score = gemini_match.get("match_score")
                ai_bucket = gemini_match.get("bucket")
                if ai_score is not None:
                    parsed["match_score"] = ai_score
                if ai_bucket:
                    parsed["bucket"] = ai_bucket
                
                await audit.log_ok(
                    cid, "gemini_match", 
                    f"AI Overwrite - Score: {ai_score}, Bucket: {ai_bucket}",
                    gemini_match
                )

        # Step 7: Update candidate with full parsed data
        parsed["parse_status"] = "done"
        await candidate_repo.update_parsed_data(candidate, parsed)
        await audit.log_ok(cid, "persist", "Candidate persisted successfully")

    except Exception as e:
        await audit.log_error(cid, "pipeline", str(e))
        await candidate_repo.update_parsed_data(candidate, {
            "parse_status": "failed",
            "parse_error": str(e),
        })
        raise

    return {"candidate_id": str(cid), "status": "done", "match_score": parsed.get("match_score")}
