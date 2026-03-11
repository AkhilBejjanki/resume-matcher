from parsers.jd_parser import parse_jd


# ─────────────────────────────────────────────
# SKILL ANALYSIS
# ─────────────────────────────────────────────

def analyze_skills(jd_skills: list, resume_skills: list) -> list:
    """
    For each JD skill, check if it exists in the resume.
    Returns list of { skill, presentInResume } dicts.
    """
    resume_lower = {s.lower() for s in resume_skills}
    return [
        {
            "skill": skill,
            "presentInResume": skill.lower() in resume_lower,
        }
        for skill in jd_skills
    ]


# ─────────────────────────────────────────────
# MATCHING SCORE
# ─────────────────────────────────────────────

def calculate_score(skills_analysis: list) -> float:
    """
    Matching Score = (Matched JD Skills / Total JD Skills) × 100
    Returns float between 0 and 100, rounded to 2 decimal places.
    """
    if not skills_analysis:
        return 0.0

    total = len(skills_analysis)
    matched = sum(1 for s in skills_analysis if s["presentInResume"])
    return round((matched / total) * 100, 2)


# ─────────────────────────────────────────────
# MAIN MATCH FUNCTION
# ─────────────────────────────────────────────

def match_resume_to_jobs(resume_data: dict, jd_list: list) -> dict:
    """
    Match a parsed resume against a list of JDs.

    Args:
        resume_data: output from parse_resume()
        jd_list: list of dicts with keys { id, role, text }

    Returns:
        Final output JSON as per assignment spec
    """
    resume_skills = resume_data.get("resumeSkills", [])
    matching_jobs = []

    for jd in jd_list:
        parsed_jd = parse_jd(
            jd_id=jd.get("id", "JD001"),
            role=jd.get("role", "Unknown Role"),
            jd_text=jd.get("text", ""),
        )

        skills_analysis = analyze_skills(parsed_jd["allSkills"], resume_skills)
        score = calculate_score(skills_analysis)

        matching_jobs.append({
            "jobId": parsed_jd["jobId"],
            "role": parsed_jd["role"],
            "aboutRole": parsed_jd["aboutRole"],
            "salary": parsed_jd["salary"],
            "experienceRequired": parsed_jd["experienceRequired"],
            "requiredSkills": parsed_jd["requiredSkills"],
            "optionalSkills": parsed_jd["optionalSkills"],
            "skillsAnalysis": skills_analysis,
            "matchingScore": score,
        })

    # Sort by matchingScore descending
    matching_jobs.sort(key=lambda x: x["matchingScore"], reverse=True)

    return {
        "name": resume_data.get("name", "Unknown"),
        "salary": resume_data.get("salary"),
        "yearOfExperience": resume_data.get("yearOfExperience"),
        "resumeSkills": resume_skills,
        "matchingJobs": matching_jobs,
    }
