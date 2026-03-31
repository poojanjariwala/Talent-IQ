"""
Heuristic-based resume parser.
Extracts structured data from raw text without requiring an LLM.
Falls back gracefully if sections are not found.
"""
import re
from typing import Optional, List, Dict, Any
from datetime import datetime


SECTION_HEADERS = {
    "summary": ["summary", "objective", "profile", "about me", "about", "professional summary"],
    "experience": ["experience", "work experience", "employment", "work history", "professional experience", "career history"],
    "education": ["education", "academic background", "qualifications", "academic qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "competencies", "key skills", "technologies", "tech stack"],
    "projects": ["projects", "personal projects", "key projects", "notable projects", "side projects"],
    "certifications": ["certifications", "certificates", "licenses", "accreditations"],
    "languages": ["languages", "spoken languages"],
}

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_PATTERN = re.compile(r"[\+\(]?[0-9][0-9 \-\(\)]{7,}[0-9]")
LINKEDIN_PATTERN = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s]+")

DEGREE_KEYWORDS = ["b.sc", "b.s", "bachelor", "m.sc", "m.s", "master", "phd", "ph.d", "mba", "b.tech", "m.tech", "be", "me", "b.e", "m.e", "associate", "diploma", "hnd"]
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
DURATION_PATTERN = re.compile(r"\b(\d+)\+?\s*(?:years?|yrs?)\b", re.IGNORECASE)


def _split_into_sections(text: str) -> Dict[str, str]:
    """Split resume text into sections based on known headers."""
    lines = text.split("\n")
    sections: Dict[str, List[str]] = {"header": []}
    current_section = "header"

    header_map = {}
    for key, synonyms in SECTION_HEADERS.items():
        for syn in synonyms:
            header_map[syn.lower()] = key

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower().rstrip(":").strip()
        if lower in header_map and len(stripped) < 80:
            current_section = header_map[lower]
            sections.setdefault(current_section, [])
        else:
            sections.setdefault(current_section, []).append(stripped)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def _extract_name(header_text: str) -> Optional[str]:
    """Attempt to extract candidate name from the first meaningful line."""
    for line in header_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip lines that look like contact info
        if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line):
            continue
        if len(line.split()) <= 5 and len(line) < 60 and not any(c.isdigit() for c in line):
            return line
    return None


def _extract_email(text: str) -> Optional[str]:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    match = PHONE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def _extract_linkedin(text: str) -> Optional[str]:
    match = LINKEDIN_PATTERN.search(text)
    return "https://" + match.group(0) if match else None


def _extract_github(text: str) -> Optional[str]:
    match = GITHUB_PATTERN.search(text)
    return "https://" + match.group(0) if match else None


def _extract_location(header_text: str) -> Optional[str]:
    """Heuristic: look for City, State or City, Country patterns."""
    loc_pattern = re.compile(r"[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+")
    lines = header_text.split("\n")
    for line in lines:
        match = loc_pattern.search(line)
        if match and len(match.group(0)) < 50:
            return match.group(0).strip()
    return None


def _extract_skills(skills_text: str) -> List[str]:
    """Extract skills from the skills section."""
    if not skills_text:
        return []
    # Split on common delimiters: comma, pipe, bullet, newline
    skills_raw = re.split(r"[,|\•\n\t•·]+", skills_text)
    skills = []
    for s in skills_raw:
        s = s.strip().strip("–-•*►▪").strip()
        if 1 < len(s) < 60 and s:
            skills.append(s)
    return list(dict.fromkeys(skills))  # deduplicate preserving order


def _estimate_experience_years(experience_text: str, full_text: str) -> Optional[float]:
    """Estimate total years by extracting year ranges or explicit duration mentions."""
    # Try explicit "X years" mentions
    duration_matches = DURATION_PATTERN.findall(experience_text or full_text)
    if duration_matches:
        return float(max(int(d) for d in duration_matches))

    # Try year ranges: 2019 - 2023 or 2019 – Present
    year_ranges = re.findall(r"(20\d{2}|19\d{2})\s*[-–to]+\s*(20\d{2}|19\d{2}|present|current|now)", experience_text or full_text, re.IGNORECASE)
    if not year_ranges:
        return None
    total_months = 0
    current_year = datetime.utcnow().year
    for start, end in year_ranges:
        try:
            start_yr = int(start)
            end_yr = current_year if end.lower() in ("present", "current", "now") else int(end)
            total_months += max(0, (end_yr - start_yr) * 12)
        except Exception:
            pass
    return round(total_months / 12, 1) if total_months > 0 else None


def _parse_education(education_text: str) -> List[Dict[str, Any]]:
    """Extract education entries."""
    if not education_text:
        return []
    entries = []
    blocks = re.split(r"\n\s*\n", education_text)
    for block in blocks:
        if not block.strip():
            continue
        degree = None
        institution = None
        year = None
        for kw in DEGREE_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", block, re.IGNORECASE):
                lines = block.strip().split("\n")
                degree = lines[0].strip() if lines else block[:100]
                institution = lines[1].strip() if len(lines) > 1 else None
                year_match = YEAR_PATTERN.search(block)
                year = int(year_match.group(0)) if year_match else None
                break
        if degree:
            entries.append({"degree": degree, "institution": institution, "year": year, "raw": block.strip()})
    return entries


def _parse_projects(projects_text: str) -> List[Dict[str, Any]]:
    """Extract project entries."""
    if not projects_text:
        return []
    # Split on double newlines or numbered list
    blocks = re.split(r"\n{2,}|\n(?=\d+\.|\•|-)", projects_text)
    projects = []
    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        projects.append({
            "name": lines[0],
            "description": " ".join(lines[1:]) if len(lines) > 1 else "",
        })
    return projects[:10]  # cap at 10


def _parse_work_experience(experience_text: str) -> List[Dict[str, Any]]:
    """Parse work experience blocks."""
    if not experience_text:
        return []
    entries = []
    blocks = re.split(r"\n{2,}", experience_text)
    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        years = YEAR_PATTERN.findall(block)
        entries.append({
            "title": lines[0],
            "company": lines[1] if len(lines) > 1 else None,
            "duration": f"{years[0]} - {years[1]}" if len(years) >= 2 else None,
            "description": " ".join(lines[2:]) if len(lines) > 2 else "",
        })
    return entries[:10]


def _parse_certifications(cert_text: str) -> List[str]:
    if not cert_text:
        return []
    certs = []
    for line in cert_text.split("\n"):
        line = line.strip().strip("•-*►▪").strip()
        if line and len(line) > 3:
            certs.append(line)
    return certs[:20]


def _parse_languages(lang_text: str) -> List[str]:
    if not lang_text:
        return []
    langs = re.split(r"[,\n•|]+", lang_text)
    return [l.strip() for l in langs if l.strip() and len(l.strip()) > 1][:10]


def parse_resume(raw_text: str) -> Dict[str, Any]:
    """
    Main entry point. Returns a structured dict of parsed resume data.
    """
    text = raw_text.strip()
    sections = _split_into_sections(text)
    header_text = sections.get("header", text[:500])

    result = {
        "full_name": _extract_name(header_text),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "linkedin_url": _extract_linkedin(text),
        "github_url": _extract_github(text),
        "location": _extract_location(header_text),
        "summary": sections.get("summary", "")[:1000] or None,
        "raw_skills": _extract_skills(sections.get("skills", "")),
        "education": _parse_education(sections.get("education", "")),
        "work_experience": _parse_work_experience(sections.get("experience", "")),
        "certifications": _parse_certifications(sections.get("certifications", "")),
        "projects": _parse_projects(sections.get("projects", "")),
        "languages": _parse_languages(sections.get("languages", "")),
        "total_experience_years": _estimate_experience_years(
            sections.get("experience", ""), text
        ),
        "parse_status": "done",
    }
    return result
