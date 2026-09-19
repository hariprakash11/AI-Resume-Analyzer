"""
Resume Recommendation Engine

Generates brutally honest, evidence-based recommendations.

Rules:
- Never praise a resume without evidence.
- Never penalize a candidate merely for being a fresher.
- Do not recommend adding skills the candidate does not have.
- Distinguish missing information from weak information.
- Use actual analyzer evidence whenever available.
"""


# =====================================================
# HELPERS
# =====================================================

def _add(
    recommendations,
    rec_type,
    category,
    message,
    severity="medium"
):
    recommendations.append({
        "type": rec_type,
        "category": category,
        "severity": severity,
        "message": message
    })


# =====================================================
# MAIN FUNCTION
# =====================================================

def generate_recommendations(
    ats_result,
    skills=None
):
    """
    Generate evidence-based resume recommendations.
    """

    recommendations = []

    skills = skills or []

    ats_result = ats_result or {}

    score = ats_result.get(
        "score",
        0
    )

    breakdown = ats_result.get(
        "breakdown",
        {}
    )

    component_scores = ats_result.get(
        "component_scores",
        {}
    )

    evidence = ats_result.get(
        "evidence",
        {}
    )


    # =================================================
    # SECTIONS
    # =================================================

    section_score = component_scores.get(
        "sections",
        0
    )

    if section_score < 50:

        _add(
            recommendations,
            "critical",
            "sections",
            "Your resume is missing several important "
            "structural sections. This can make the document "
            "harder for ATS systems and recruiters to interpret.",
            "high"
        )

    elif section_score < 75:

        _add(
            recommendations,
            "improvement",
            "sections",
            "Your resume structure is incomplete. "
            "Review the missing sections before applying.",
            "medium"
        )


    # =================================================
    # SKILLS
    # =================================================

    skill_score = component_scores.get(
        "skills",
        0
    )

    skill_count = len(
        set(skills)
    )

    if skill_count == 0:

        _add(
            recommendations,
            "critical",
            "skills",
            "No recognized skills were detected. "
            "If you have technical or professional skills, "
            "they need to be explicitly stated in the resume.",
            "high"
        )

    elif skill_score < 45:

        _add(
            recommendations,
            "warning",
            "skills",
            f"Only {skill_count} skill"
            f"{'s' if skill_count != 1 else ''} "
            "were detected and the supporting evidence is weak. "
            "Do not simply add more keywords. Clearly demonstrate "
            "where you actually used these skills.",
            "high"
        )


    # =================================================
    # SKILL EVIDENCE
    # =================================================

    if evidence:

        unsupported = evidence.get(
            "unsupported_skills",
            []
        )

        supported = evidence.get(
            "supported_skills",
            []
        )

        if unsupported:

            preview = ", ".join(
                str(skill)
                for skill in unsupported[:10]
            )

            if len(unsupported) > 10:
                preview += ", ..."

            _add(
                recommendations,
                "evidence",
                "skill_evidence",
                "These skills are listed but were not "
                "adequately supported by project or experience "
                f"evidence: {preview}.",
                "high"
            )

        if supported:

            _add(
                recommendations,
                "positive",
                "skill_evidence",
                f"{len(supported)} detected skill"
                f"{'s' if len(supported) != 1 else ''} "
                "had supporting evidence in your resume.",
                "low"
            )


    # =================================================
    # KEYWORDS
    # =================================================

    keyword_score = component_scores.get(
        "keywords",
        0
    )

    if keyword_score < 40:

        _add(
            recommendations,
            "critical",
            "keywords",
            "Your resume has weak keyword coverage. "
            "Important technical and role-related terminology "
            "may not be visible enough to an ATS.",
            "high"
        )

    elif keyword_score < 65:

        _add(
            recommendations,
            "improvement",
            "keywords",
            "Keyword coverage is moderate. "
            "Use precise terminology naturally inside your "
            "experience and project descriptions instead of "
            "creating a keyword list.",
            "medium"
        )


    # =================================================
    # EXPERIENCE
    # =================================================

    experience_score = component_scores.get(
        "experience",
        0
    )

    experience = {}

    if evidence:
        experience = evidence.get(
            "experience",
            {}
        )

    if experience_score < 45:

        _add(
            recommendations,
            "warning",
            "experience",
            "Your experience evidence is weak. "
            "Responsibilities are not enough by themselves. "
            "Explain what you did, what technology you used, "
            "and what result you achieved.",
            "high"
        )

    elif experience_score < 70:

        _add(
            recommendations,
            "improvement",
            "experience",
            "Your experience section has useful content, "
            "but several descriptions could be stronger with "
            "specific actions, technologies, and measurable outcomes.",
            "medium"
        )


    # =================================================
    # ACHIEVEMENTS / METRICS
    # =================================================

    achievement_count = experience.get(
        "achievement_count",
        0
    )

    metrics = experience.get(
        "metrics",
        []
    )

    if experience.get(
        "present",
        False
    ):

        if achievement_count == 0:

            _add(
                recommendations,
                "warning",
                "achievements",
                "No clear achievement statements were detected "
                "in your experience. Your bullets mainly describe "
                "activities rather than measurable outcomes.",
                "high"
            )

        if not metrics:

            _add(
                recommendations,
                "improvement",
                "metrics",
                "No measurable evidence was detected in your "
                "experience section. Where truthful, include "
                "numbers such as users, records, time saved, "
                "accuracy, scale, or percentage improvements.",
                "medium"
            )


    # =================================================
    # CONTACT
    # =================================================

    contact_score = component_scores.get(
        "contact",
        0
    )

    if contact_score < 50:

        _add(
            recommendations,
            "critical",
            "contact",
            "Your contact information appears incomplete. "
            "A professional resume should clearly provide "
            "a valid email address and phone number.",
            "high"
        )

    elif contact_score < 80:

        _add(
            recommendations,
            "improvement",
            "contact",
            "Your basic contact information is present, "
            "but adding professional links such as LinkedIn, "
            "GitHub, or a portfolio may improve your profile.",
            "low"
        )


    # =================================================
    # READABILITY
    # =================================================

    readability_score = component_scores.get(
        "readability",
        0
    )

    if readability_score < 60:

        _add(
            recommendations,
            "warning",
            "readability",
            "The resume content length or sentence structure "
            "may make it harder to scan efficiently. "
            "Remove unnecessary text and keep bullet points focused.",
            "medium"
        )


    # =================================================
    # OVERALL SCORE
    # =================================================

    if score < 40:

        _add(
            recommendations,
            "critical",
            "overall",
            "Brutally honest assessment: this resume is not "
            "currently competitive for ATS screening. "
            "Fix the structural and evidence problems before "
            "focusing on cosmetic improvements.",
            "high"
        )

    elif score < 60:

        _add(
            recommendations,
            "warning",
            "overall",
            "This resume has a weak ATS foundation. "
            "It may pass basic parsing, but the current evidence "
            "is not strong enough to make it competitive.",
            "high"
        )

    elif score < 75:

        _add(
            recommendations,
            "improvement",
            "overall",
            "This resume is usable but not highly competitive. "
            "The weaker scoring categories should be improved "
            "before relying on it for serious applications.",
            "medium"
        )

    elif score < 85:

        _add(
            recommendations,
            "positive",
            "overall",
            "This resume has a solid ATS foundation. "
            "However, the score does not guarantee interview "
            "success. Tailoring the resume to each job remains important.",
            "low"
        )

    else:

        _add(
            recommendations,
            "positive",
            "overall",
            "The resume demonstrates strong ATS compatibility "
            "based on the available evidence. Keep the claims "
            "truthful and tailor the resume to each target role.",
            "low"
        )


    # =================================================
    # FINAL PRIORITY ORDER
    # =================================================

    severity_order = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    recommendations.sort(
        key=lambda item:
            severity_order.get(
                item.get("severity"),
                2
            )
    )

    return recommendations