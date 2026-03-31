"""
Candidate-to-job matching engine.
Produces a match score (0-100) and breakdown across:
  - Skill match (60%)
  - Experience match (20%)
  - Education match (10%)
  - Project match (10%)
"""
from typing import List, Dict, Any, Optional, Tuple


BUCKET_THRESHOLDS = {
    "shortlist": 70,
    "hold": 40,
    "reject": 0,
}


def _skill_match_score(
    candidate_skills: List[str],
    inferred_skills: List[str],
    required_skills: List[str],
    nice_to_have_skills: List[str],
) -> Tuple[float, List[str], List[str]]:
    """Returns (score 0-100, matched_skills, missing_skills)."""
    # Use fuzzy/substring matching for heuristics
    all_candidate_raw = [s.lower() for s in candidate_skills + inferred_skills]
    all_candidate_text = " ".join(all_candidate_raw)
    
    required_lower = [s.lower() for s in required_skills]
    nice_lower = [s.lower() for s in nice_to_have_skills]

    matched_required = []
    missing = []
    
    for req in required_lower:
        # Check for exact match first
        if req in all_candidate_raw:
            matched_required.append(req)
        # Check for substring match (e.g. 'python' matches 'python developer')
        elif req in all_candidate_text or any(req in c for c in all_candidate_raw):
            matched_required.append(req)
        else:
            missing.append(req)

    matched_nice = []
    for nice in nice_lower:
        if nice in all_candidate_raw or nice in all_candidate_text:
            matched_nice.append(nice)

    # Calculate scores
    required_count = len(required_lower)
    if required_count == 0:
        required_score = 80.0
    else:
        required_score = (len(matched_required) / required_count) * 80

    nice_count = len(nice_lower)
    if nice_count == 0:
        nice_score = 20.0
    else:
        nice_score = (len(matched_nice) / nice_count) * 20

    return min(required_score + nice_score, 100), matched_required + matched_nice, [s for s in required_skills if s.lower() in missing]


def _experience_match_score(
    candidate_years: Optional[float],
    min_years: Optional[int],
    max_years: Optional[int],
) -> float:
    if candidate_years is None:
        return 65.0  # Slightly more positive baseline
    if min_years is None or min_years == 0:
        return 100.0
    
    if candidate_years >= min_years:
        if max_years and candidate_years > max_years * 2:
            return 80.0  # lighter overqualified penalty
        return 100.0
    
    # Smoother ratio
    ratio = (candidate_years + 0.5) / (min_years + 0.5)
    return max(0.0, min(95.0, ratio * 100))


def _education_match_score(education: List[Dict[str, Any]]) -> float:
    if not education:
        return 75.0  # Assume baseline relevance
    keywords = {"phd": 100, "master": 95, "m.sc": 95, "m.s": 95, "mba": 90, "bachelor": 85, "b.sc": 85, "b.s": 85, "b.tech": 85, "associate": 70, "diploma": 60}
    best = 70.0
    for edu in education:
        degree_text = (edu.get("degree") or "").lower()
        for kw, score in keywords.items():
            if kw in degree_text:
                best = max(best, score)
    return best


def _project_match_score(
    candidate_projects: List[Dict[str, Any]],
    required_projects: List[str],
) -> float:
    if not required_projects:
        return 100.0 if candidate_projects else 80.0
    if not candidate_projects:
        return 50.0  # Neutral
    project_texts = " ".join(
        (p.get("name", "") + " " + p.get("description", "")).lower()
        for p in candidate_projects
    )
    matched = sum(1 for rp in required_projects if rp.lower() in project_texts)
    return (matched / max(len(required_projects), 1)) * 100


def compute_match(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Returns a dict with:
      match_score, score_breakdown, matched_skills, missing_skills, bucket
    """
    # Weights
    SKILL_W = 0.55  # Reduced slightly to balance other signals
    EXP_W = 0.25    # Experience is key
    EDU_W = 0.10
    PROJ_W = 0.10

    skill_score, matched_skills, missing_skills = _skill_match_score(
        candidate.get("normalized_skills", []),
        candidate.get("inferred_skills", []),
        job.get("required_skills", []),
        job.get("nice_to_have_skills", []),
    )

    exp_score = _experience_match_score(
        candidate.get("total_experience_years"),
        job.get("experience_min_years"),
        job.get("experience_max_years"),
    )

    edu_score = _education_match_score(candidate.get("education", []))

    proj_score = _project_match_score(
        candidate.get("projects", []),
        job.get("required_projects", []),
    )

    total = (
        skill_score * SKILL_W
        + exp_score * EXP_W
        + edu_score * EDU_W
        + proj_score * PROJ_W
    )
    total = round(total, 2)

    # Assign bucket
    bucket = "reject"
    # Search from highest threshold down
    thresholds = sorted(BUCKET_THRESHOLDS.items(), key=lambda x: x[1], reverse=True)
    for b, threshold in thresholds:
        if total >= threshold:
            bucket = b
            break

    return {
        "match_score": total,
        "matched_skills": list(set(matched_skills)), # Dedupe
        "missing_skills": missing_skills,
        "score_breakdown": {
            "skill_match": round(skill_score, 2),
            "experience_match": round(exp_score, 2),
            "education_match": round(edu_score, 2),
            "project_match": round(proj_score, 2),
            "total": total,
        },
        "bucket": bucket,
    }
