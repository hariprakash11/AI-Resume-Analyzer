import re

from app.utils.skill_extractor import (
    extract_skills
)


# =====================================================
# JOB DESCRIPTION ANALYZER
# =====================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =====================================================
# EXTRACT JOB SKILLS
# =====================================================

def extract_job_skills(job_description):

    if not job_description:
        return []

    return extract_skills(
        job_description
    )


# =====================================================
# COMPARE SKILLS
# =====================================================

def compare_skills(
    resume_skills,
    job_skills
):

    resume_set = set(
        skill.lower()
        for skill in resume_skills
    )

    job_set = set(
        skill.lower()
        for skill in job_skills
    )

    matched_skills = sorted(
        resume_set.intersection(
            job_set
        )
    )

    missing_skills = sorted(
        job_set.difference(
            resume_set
        )
    )

    return {
        "matched": matched_skills,
        "missing": missing_skills
    }


# =====================================================
# JOB MATCH SCORE
# =====================================================

def calculate_job_match_score(
    resume_skills,
    job_skills
):

    if not job_skills:

        return 0.0

    comparison = compare_skills(
        resume_skills,
        job_skills
    )

    matched = len(
        comparison["matched"]
    )

    total = len(
        job_skills
    )

    score = (
        matched / total
    ) * 100

    return round(
        score,
        1
    )


# =====================================================
# COMPLETE JOB ANALYSIS
# =====================================================

def analyze_job_match(
    resume_skills,
    job_description
):

    job_skills = extract_job_skills(
        job_description
    )

    comparison = compare_skills(
        resume_skills,
        job_skills
    )

    score = calculate_job_match_score(
        resume_skills,
        job_skills
    )

    return {
        "job_skills": job_skills,
        "matched_skills": comparison["matched"],
        "missing_skills": comparison["missing"],
        "score": score
    }