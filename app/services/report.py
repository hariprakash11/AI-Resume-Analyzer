"""Services for rebuilding a saved resume analysis report."""

from app.utils.ats_analyzer import analyze_resume
from app.utils.ats_score import calculate_ats_score
from app.utils.recommendation_engine import generate_recommendations
from app.utils.skill_extractor import extract_skills_from_sections
from app.routes.resume import (
    ensure_section_structure,
    extract_sections,
)


def build_report(resume):
    """
    Rebuild the analysis data for a saved resume.

    The database stores the original resume text and ATS score.
    The remaining analysis details are regenerated using the
    same analysis components used by the upload workflow.
    """

    resume_text = resume.resume_text or ""

    sections = extract_sections(
        resume_text
    )

    sections = ensure_section_structure(
        resume_text,
        sections
    )

    skills = extract_skills_from_sections(
        sections
    )

    ats_analysis = analyze_resume(
        resume_text,
        sections
    )

    ats_result = calculate_ats_score(
        resume_text=resume_text,
        sections=sections,
        skills=skills,
        ats_analysis=ats_analysis,
    )

    recommendations = generate_recommendations(
        sections,
        skills,
        ats_analysis,
        ats_result,
    )

    return {
        "resume": resume,
        "sections": sections,
        "skills": skills,
        "ats_analysis": ats_analysis,
        "ats_result": ats_result,
        "recommendations": recommendations,
    }