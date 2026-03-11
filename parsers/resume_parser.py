import re
import pdfplumber
from utils.skills_dict import SKILLS_LOWER_MAP

# Load spaCy model for NER (used for name extraction)
nlp = None  # spaCy disabled, using regex fallback


# ─────────────────────────────────────────────
# PDF TEXT EXTRACTION
# ─────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF resume using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


# ─────────────────────────────────────────────
# NAME EXTRACTION
# ─────────────────────────────────────────────

def extract_name(text: str) -> str:
    """
    Extract candidate name using two strategies:
    1. spaCy NER - look for PERSON entity near top of resume
    2. Fallback - first clean line with 2-4 words
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    top_text = "\n".join(lines[:10])  # Only scan top 10 lines

    # Strategy 1: spaCy NER
    if nlp:
        doc = nlp(top_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                return ent.text.strip()

    # Strategy 2: Rule-based fallback
    for line in lines[:6]:
        # Skip lines with emails, phones, URLs, digits at start
        if re.search(r"[@/\\|]", line):
            continue
        if re.match(r"^\d", line):
            continue
        if re.match(r"(resume|curriculum|cv|profile|summary|objective)", line, re.I):
            continue
        if len(line) > 60 or len(line) < 3:
            continue
        words = line.split()
        if 2 <= len(words) <= 5 and all(w[0].isupper() or w[0].isalpha() for w in words):
            return line

    return "Unknown"


# ─────────────────────────────────────────────
# SALARY EXTRACTION
# ─────────────────────────────────────────────

def extract_salary(text: str):
    """
    Extract expected/current salary from resume text.
    Returns string like '12 LPA' or None.
    """
    patterns = [
        # Indian format: 12 LPA, 10 Lakhs, ₹12,00,000
        r"(?:expected|current|desired)?\s*(?:salary|ctc|package|compensation)[:\s]*(?:₹|rs\.?|inr)?\s*([\d,.]+\s*(?:lpa|lakh|lakhs|l|k)?(?:\s*per\s*annum|\s*pa)?)",
        r"(?:₹|rs\.?|inr)\s*([\d,.]+\s*(?:lpa|lakh|lakhs|l|k)?)",
        r"([\d,.]+\s*lpa)",
        # US format: $80,000
        r"\$([\d,]+(?:\.\d+)?)\s*(?:/\s*(?:yr|year|annum))?",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return None


# ─────────────────────────────────────────────
# EXPERIENCE EXTRACTION
# ─────────────────────────────────────────────

def extract_experience(text: str):
    """
    Extract years of experience.
    Strategy 1: Look for explicit mention like '3 years of experience'
    Strategy 2: Calculate from date ranges in resume
    Strategy 3: Detect fresher keywords → return 0
    """

    # Strategy 1: Explicit mention
    explicit_patterns = [
        r"(\d+\.?\d*)\s*\+?\s*years?\s+(?:of\s+)?(?:total\s+)?(?:professional\s+)?(?:work\s+)?experience",
        r"experience[:\s]+(\d+\.?\d*)\s*\+?\s*years?",
        r"(\d+\.?\d*)\s*years?\s+(?:in\s+)?(?:software|development|engineering|industry|it\s+industry)",
    ]
    for pattern in explicit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    # Strategy 2: Calculate from date ranges
    # Matches: "Jan 2020 – Mar 2022", "2020 - Present", "June 2019 to Dec 2021"
    date_pattern = re.compile(
        r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?[a-z]*\.?\s*(\d{4})"
        r"\s*[-–—to]+\s*"
        r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?(\d{4}|present|current|now)",
        re.IGNORECASE,
    )

    current_year = 2025
    ranges = []
    for match in date_pattern.finditer(text):
        start = int(match.group(1))
        end_raw = match.group(2)
        end = current_year if re.match(r"present|current|now", end_raw, re.I) else int(end_raw)
        if 1990 <= start <= current_year and end >= start:
            ranges.append((start, end))

    if ranges:
        # Merge overlapping ranges to avoid double-counting
        ranges.sort()
        merged = [list(ranges[0])]
        for start, end in ranges[1:]:
            if start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        total_years = sum(e - s for s, e in merged)
        return round(float(total_years), 1)

    # Strategy 3: Fresher detection
    if re.search(r"\b(fresher|entry.?level|no\s+experience|0\s+years?)\b", text, re.IGNORECASE):
        return 0

    return None


# ─────────────────────────────────────────────
# SKILLS EXTRACTION
# ─────────────────────────────────────────────

def extract_skills(text: str) -> list:
    """
    Extract skills from text using the skills dictionary.
    Uses word-boundary regex to avoid partial matches.
    """
    found = set()
    normalized = text.lower()

    for skill_lower, skill_original in SKILLS_LOWER_MAP.items():
        # Escape special regex chars (e.g. C++, .NET)
        escaped = re.escape(skill_lower)
        pattern = rf"(?<![a-zA-Z0-9\.\+]){escaped}(?![a-zA-Z0-9\.\+])"
        if re.search(pattern, normalized):
            found.add(skill_original)

    return sorted(found)


# ─────────────────────────────────────────────
# MAIN PARSE FUNCTION
# ─────────────────────────────────────────────

def parse_resume(file_path: str) -> dict:
    """
    Parse a resume PDF and return structured data.
    Returns: { name, salary, yearOfExperience, resumeSkills }
    """
    text = extract_text_from_pdf(file_path)

    return {
        "name": extract_name(text),
        "salary": extract_salary(text),
        "yearOfExperience": extract_experience(text),
        "resumeSkills": extract_skills(text),
        "_rawText": text,  # kept internally for matching, stripped before final output
    }
