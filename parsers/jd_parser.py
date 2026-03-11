import re
from utils.skills_dict import SKILLS_LOWER_MAP


# ─────────────────────────────────────────────
# SALARY EXTRACTION FROM JD
# ─────────────────────────────────────────────

def extract_salary(text: str):
    """
    Handles all salary formats seen in the sample JDs:
    - $180,000 - $220,000
    - $130,000 - $160,000 per year
    - $120,000.00 - $145,000.00/per year
    - $58.65/hour to $181,000/year
    - 61087 - 104364  (plain range near salary/compensation keyword)
    - 12 LPA / ₹10,00,000
    - Salary: $176,000.00 - $242,000.00
    """
    patterns = [
        # Explicit salary label + dollar range: Salary: $176,000 - $242,000
        r"(?:salary|pay\s+range|compensation)[^\n$]*\$\s*([\d,]+(?:\.\d+)?)\s*[-–—to]+\s*\$?\s*([\d,]+(?:\.\d+)?)",

        # Dollar range anywhere: $120,000 - $145,000
        r"\$\s*([\d,]+(?:\.\d+)?)\s*[-–—to]+\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(?:per\s+year|\/year|annually|\/yr|per\s+annum)?",

        # Hourly to annual: $58.65/hour to $181,000/year
        r"\$\s*([\d,.]+)\s*\/\s*hour\s+to\s+\$\s*([\d,]+)\s*\/\s*year",

        # Single dollar value: $120,000
        r"\$\s*([\d,]+(?:\.\d+)?)\s*(?:per\s+year|\/year|annually)?",

        # Plain number range near compensation keyword: 61087 - 104364
        r"(?:compensation|salary|pay)[^\n]*?([\d]{4,7})\s*[-–—]\s*([\d]{4,7})",

        # Indian LPA: 12 LPA / 10-15 LPA
        r"(\d+\.?\d*)\s*[-–]?\s*(\d+\.?\d*)?\s*lpa",

        # INR: ₹10,00,000
        r"(?:₹|rs\.?|inr)\s*([\d,]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return None


# ─────────────────────────────────────────────
# EXPERIENCE EXTRACTION FROM JD
# ─────────────────────────────────────────────

def extract_experience(text: str):
    """
    Handles experience patterns from all sample JDs:
    - "7 years of strong hands-on experience"
    - "5+ years of experience"
    - "3-5 years of experience"
    - "Bachelor's with 5+ years of experience"
    - "Master's with 3+ years of experience"
    - "2+ years of programming experience"
    - "Minimum of 4 years"
    - "At least 2 years"
    - Fresher / Entry-Level → 0
    Returns lowest number found (minimum requirement).
    """
    patterns = [
        # Degree + experience: Bachelor's with 5+ years
        r"(?:bachelor|master|phd|degree)[^.]*?(\d+)\s*\+?\s*years?",

        # Range: 5-7 years / 3 to 5 years of experience
        r"(\d+)\s*[-–to]+\s*(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:relevant\s+|related\s+|professional\s+|work\s+)?experience",

        # N+ years of experience
        r"(\d+)\s*\+\s*years?\s+(?:of\s+)?(?:relevant\s+|related\s+|professional\s+|hands.on\s+|work\s+)?experience",

        # N years of experience (no +)
        r"(\d+)\s*years?\s+(?:of\s+)?(?:strong\s+)?(?:hands.on\s+)?(?:relevant\s+|related\s+|professional\s+)?(?:work\s+)?experience",

        # Minimum / at least
        r"minimum\s+(?:of\s+)?(\d+)\s*years?",
        r"at\s+least\s+(\d+)\s*years?",

        # N+ years in
        r"(\d+)\s*\+?\s*years?\s+(?:in\s+)?(?:software|development|engineering|industry)",
    ]

    candidates = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = float(match.group(1))
            candidates.append(val)

    if candidates:
        return min(candidates)  # Return minimum requirement

    # Fresher / Entry-level
    if re.search(r"\b(fresher|entry.?level|0\s*\+?\s*years?|no\s+experience\s+required)\b", text, re.IGNORECASE):
        return 0

    return None


# ─────────────────────────────────────────────
# SKILLS EXTRACTION FROM JD
# ─────────────────────────────────────────────

def extract_skills(text: str) -> list:
    """
    Extract all skills mentioned in a JD using the skills dictionary.
    Uses word-boundary regex to avoid partial matches.
    """
    found = set()
    normalized = text.lower()

    for skill_lower, skill_original in SKILLS_LOWER_MAP.items():
        escaped = re.escape(skill_lower)
        pattern = rf"(?<![a-zA-Z0-9\.\+]){escaped}(?![a-zA-Z0-9\.\+])"
        if re.search(pattern, normalized):
            found.add(skill_original)

    return sorted(found)


# ─────────────────────────────────────────────
# REQUIRED vs OPTIONAL SKILLS SPLIT
# ─────────────────────────────────────────────

def split_required_optional(text: str, all_skills: list):
    """
    Split skills into required vs optional based on JD section headers.
    Handles common patterns from sample JDs:
    - "Required Qualifications / Required Skills / Must Have"
    - "Desired Qualifications / Good to have / Preferred / Nice to have / Desired Multipliers"
    """
    # Extract required section text
    req_pattern = re.compile(
        r"(?:required\s+(?:qualifications?|skills?)|must.have|minimum\s+qualifications?|basic\s+qualifications?)"
        r"[:\s]*\n(.*?)(?=\n(?:desired|preferred|optional|good\s+to\s+have|nice\s+to\s+have|bonus|\Z))",
        re.IGNORECASE | re.DOTALL,
    )

    # Extract optional/preferred section text
    opt_pattern = re.compile(
        r"(?:desired\s+(?:qualifications?|skills?|multipliers?)|preferred\s+(?:qualifications?|skills?)|"
        r"good\s+to\s+have|nice\s+to\s+have|optional|bonus\s+points?)"
        r"[:\s]*\n(.*?)(?=\n\s*\n|\Z)",
        re.IGNORECASE | re.DOTALL,
    )

    req_match = req_pattern.search(text)
    opt_match = opt_pattern.search(text)

    req_text = req_match.group(1) if req_match else ""
    opt_text = opt_match.group(1) if opt_match else ""

    required_skills = []
    optional_skills = []

    for skill in all_skills:
        skill_lower = skill.lower()
        escaped = re.escape(skill_lower)
        pattern = rf"(?<![a-zA-Z0-9\.\+]){escaped}(?![a-zA-Z0-9\.\+])"

        in_optional = bool(opt_text and re.search(pattern, opt_text.lower()))
        in_required = bool(req_text and re.search(pattern, req_text.lower()))

        if in_optional and not in_required:
            optional_skills.append(skill)
        else:
            required_skills.append(skill)

    # If no section was detected, put everything in required
    if not req_text and not opt_text:
        return all_skills, []

    return required_skills, optional_skills


# ─────────────────────────────────────────────
# JD SUMMARY EXTRACTION
# ─────────────────────────────────────────────

def extract_summary(text: str) -> str:
    """
    Extract 'About Role' summary from JD.
    Looks for common section headers used in sample JDs.
    Falls back to first 2 meaningful sentences.
    """
    section_patterns = [
        r"(?:position\s+overview|the\s+opportunity|job\s+description|about\s+the\s+role|"
        r"role\s+overview|what\s+you.ll\s+do|how\s+you.ll\s+fulfill|the\s+team)"
        r"[:\s]*\n+(.*?)(?=\n\s*\n|\Z)",
    ]

    for pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            summary = " ".join(match.group(1).split())
            return summary[:350] + ("..." if len(summary) > 350 else "")

    # Fallback: first 2 long lines
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 50]
    if lines:
        return " ".join(lines[:2])[:350]

    return "No summary available."


# ─────────────────────────────────────────────
# MAIN JD PARSE FUNCTION
# ─────────────────────────────────────────────

def parse_jd(jd_id: str, role: str, jd_text: str) -> dict:
    """
    Parse a job description and return structured data.
    """
    all_skills = extract_skills(jd_text)
    required_skills, optional_skills = split_required_optional(jd_text, all_skills)

    return {
        "jobId": jd_id,
        "role": role,
        "aboutRole": extract_summary(jd_text),
        "salary": extract_salary(jd_text),
        "experienceRequired": extract_experience(jd_text),
        "requiredSkills": required_skills,
        "optionalSkills": optional_skills,
        "allSkills": all_skills,
        "_rawText": jd_text,
    }