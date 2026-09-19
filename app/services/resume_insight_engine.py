"""
Resume Insight Engine

Converts raw resume analysis into honest, explainable insights.

Important:
- Never invent resume information.
- Never assume a skill is possessed just because it is common.
- Never impose an artificial keyword/skill limit.
- Separate detected information from inferred weaknesses.
- Keep recommendations evidence-based.
"""


# =====================================================
# HELPERS
# =====================================================

def _safe_dict(value):
    if isinstance(value, dict):
        return value

    return {}


def _add_item(
    collection,
    title,
    message,
    severity="medium",
    evidence=None
):
    item = {
        "title": title,
        "message": message,
        "severity": severity,
    }

    if evidence:
        item["evidence"] = evidence

    collection.append(item)


# =====================================================
# SECTION INSIGHTS
# =====================================================

def _analyze_sections(
    ats_analysis,
    strengths,
    weaknesses,
    critical
):
    sections_data = _safe_dict(
        ats_analysis.get("sections")
    )

    important = _safe_dict(
        sections_data.get("important")
    )

    if not important:
        return

    present_sections = []
    missing_sections = []

    for section, data in important.items():

        if not isinstance(data, dict):
            continue

        if data.get("present"):
            present_sections.append(section)
        else:
            missing_sections.append(section)

    # -------------------------------------------------
    # Strengths
    # -------------------------------------------------

    if present_sections:

        _add_item(
            strengths,
            "Detected resume sections",
            f"Detected sections: "
            f"{', '.join(present_sections)}.",
            "low"
        )

    # -------------------------------------------------
    # Critical core sections
    # -------------------------------------------------

    core_sections = {
        "experience",
        "education",
        "skills"
    }

    missing_core = [
        section
        for section in missing_sections
        if section in core_sections
    ]

    if missing_core:

        _add_item(
            critical,
            "Missing core sections",
            "The following core sections were not "
            f"detected: {', '.join(missing_core)}.",
            "high"
        )

    # -------------------------------------------------
    # Optional sections
    # -------------------------------------------------

    optional_missing = [
        section
        for section in missing_sections
        if section not in core_sections
    ]

    if optional_missing:

        _add_item(
            weaknesses,
            "Additional sections not detected",
            f"These sections were not detected: "
            f"{', '.join(optional_missing)}. "
            "This is not automatically a problem; "
            "whether they are needed depends on the candidate "
            "and target role.",
            "low"
        )


# =====================================================
# CONTACT INSIGHTS
# =====================================================

def _analyze_contact(
    ats_analysis,
    strengths,
    weaknesses,
    critical
):
    contact = _safe_dict(
        ats_analysis.get("contact")
    )

    if not contact:
        return

    if contact.get("email"):
        _add_item(
            strengths,
            "Email detected",
            "A valid-looking email address was detected.",
            "low"
        )
    else:
        _add_item(
            critical,
            "Email not detected",
            "No email address was detected in the extracted "
            "resume text.",
            "high"
        )

    if contact.get("phone"):
        _add_item(
            strengths,
            "Phone number detected",
            "A phone number was detected.",
            "low"
        )
    else:
        _add_item(
            critical,
            "Phone number not detected",
            "No phone number was detected in the extracted "
            "resume text.",
            "high"
        )

    if contact.get("linkedin"):
        _add_item(
            strengths,
            "LinkedIn detected",
            "A LinkedIn profile link was detected.",
            "low"
        )
    else:
        _add_item(
            weaknesses,
            "LinkedIn not detected",
            "No LinkedIn URL was detected. This is not an ATS "
            "failure, but a professional profile link can be useful.",
            "low"
        )

    if contact.get("github"):
        _add_item(
            strengths,
            "GitHub detected",
            "A GitHub profile link was detected.",
            "low"
        )

    if contact.get("portfolio_or_url"):
        _add_item(
            strengths,
            "Web link detected",
            "At least one web URL was detected.",
            "low"
        )


# =====================================================
# SKILL INSIGHTS
# =====================================================

def _analyze_skills(
    skills,
    ats_analysis,
    strengths,
    weaknesses,
    critical
):
    skills = list(
        dict.fromkeys(skills or [])
    )

    count = len(skills)

    if count == 0:

        _add_item(
            critical,
            "No recognized skills detected",
            "The analyzer did not recognize any skills from "
            "its current skill vocabulary. This does NOT prove "
            "that the resume contains no skills; it means the "
            "current detector did not recognize them.",
            "high"
        )

        return

    # -------------------------------------------------
    # Do not impose a maximum.
    # -------------------------------------------------

    _add_item(
        strengths,
        "Skills detected",
        f"{count} unique skill"
        f"{'s' if count != 1 else ''} "
        "were detected.",
        "low",
        evidence=skills
    )

    # -------------------------------------------------
    # Evidence
    # -------------------------------------------------

    experience = _safe_dict(
        ats_analysis.get("experience")
    )

    projects = _safe_dict(
        ats_analysis.get("projects")
    )

    experience_text = str(
        experience
    ).lower()

    project_text = str(
        projects
    ).lower()

    supported = []
    weak_evidence = []

    for skill in skills:

        normalized_skill = str(
            skill
        ).lower()

        in_experience = (
            normalized_skill
            in experience_text
        )

        in_projects = (
            normalized_skill
            in project_text
        )

        if in_experience or in_projects:
            supported.append(skill)
        else:
            weak_evidence.append(skill)

    if supported:

        _add_item(
            strengths,
            "Skills supported by experience/projects",
            f"{len(supported)} detected skill"
            f"{'s' if len(supported) != 1 else ''} "
            "also appeared in the analyzed experience or "
            "project content.",
            "low",
            evidence=supported
        )

    if weak_evidence:

        _add_item(
            weaknesses,
            "Skills with weak supporting evidence",
            "These detected skills were not found in the "
            "analyzed experience/project text. This does not "
            "mean the skills are false, but their practical "
            "evidence is weak in the resume.",
            "medium",
            evidence=weak_evidence
        )


# =====================================================
# ACTION VERB INSIGHTS
# =====================================================

def _analyze_action_verbs(
    ats_analysis,
    strengths,
    weaknesses
):
    action_data = _safe_dict(
        ats_analysis.get("action_verbs")
    )

    unique = action_data.get(
        "unique",
        0
    )

    total = action_data.get(
        "total",
        0
    )

    found = action_data.get(
        "found",
        {}
    )

    if unique > 0:

        _add_item(
            strengths,
            "Action verbs detected",
            f"{unique} unique action verb"
            f"{'s' if unique != 1 else ''} "
            f"were detected across {total} occurrence"
            f"{'s' if total != 1 else ''}.",
            "low",
            evidence=list(found.keys())
        )

    else:

        _add_item(
            weaknesses,
            "Weak action language",
            "No recognized action verbs were detected. "
            "Review experience and project bullets to ensure "
            "they clearly describe what you actually did.",
            "medium"
        )


# =====================================================
# TECHNICAL TERM INSIGHTS
# =====================================================

def _analyze_technical_terms(
    ats_analysis,
    strengths,
    weaknesses
):
    technical_data = _safe_dict(
        ats_analysis.get("technical_terms")
    )

    unique = technical_data.get(
        "unique",
        0
    )

    total = technical_data.get(
        "total",
        0
    )

    found = technical_data.get(
        "found",
        {}
    )

    if unique > 0:

        _add_item(
            strengths,
            "Technical terminology detected",
            f"{unique} unique technical term"
            f"{'s' if unique != 1 else ''} "
            f"were detected across {total} occurrence"
            f"{'s' if total != 1 else ''}.",
            "low",
            evidence=list(found.keys())
        )

    else:

        _add_item(
            weaknesses,
            "Limited recognized technical terminology",
            "The current analyzer detected little or no "
            "technical terminology. This may indicate weak "
            "technical detail or simply vocabulary that is "
            "not yet included in the analyzer database.",
            "medium"
        )


# =====================================================
# IMPACT INSIGHTS
# =====================================================

def _analyze_impact(
    ats_analysis,
    strengths,
    weaknesses
):
    impact = _safe_dict(
        ats_analysis.get("impact")
    )

    achievement_count = impact.get(
        "achievement_count",
        0
    )

    metrics = impact.get(
        "metrics",
        []
    )

    percentages = impact.get(
        "percentages",
        []
    )

    currency_values = impact.get(
        "currency_values",
        []
    )

    achievement_sentences = impact.get(
        "achievement_sentences",
        []
    )

    # -------------------------------------------------
    # Achievement evidence
    # -------------------------------------------------

    if achievement_count > 0:

        _add_item(
            strengths,
            "Measurable achievements detected",
            f"{achievement_count} achievement statement"
            f"{'s' if achievement_count != 1 else ''} "
            "contains both impact language and numerical "
            "evidence.",
            "low",
            evidence=achievement_sentences
        )

    else:

        _add_item(
            weaknesses,
            "No clear quantified achievements detected",
            "The analyzer did not find achievement statements "
            "that combine an impact-oriented verb with a number. "
            "This does not mean the candidate has no achievements; "
            "the resume may simply describe them without measurable evidence.",
            "medium"
        )

    # -------------------------------------------------
    # Metrics
    # -------------------------------------------------

    if metrics:

        _add_item(
            strengths,
            "Metrics detected",
            f"{len(metrics)} measurable value"
            f"{'s' if len(metrics) != 1 else ''} "
            "were detected.",
            "low",
            evidence=metrics
        )

    # -------------------------------------------------
    # Percentages
    # -------------------------------------------------

    if percentages:

        _add_item(
            strengths,
            "Percentage evidence detected",
            f"{len(percentages)} percentage value"
            f"{'s' if len(percentages) != 1 else ''} "
            "were detected.",
            "low",
            evidence=percentages
        )

    # -------------------------------------------------
    # Currency
    # -------------------------------------------------

    if currency_values:

        _add_item(
            strengths,
            "Financial metrics detected",
            "Currency-based numerical evidence was detected.",
            "low",
            evidence=currency_values
        )


# =====================================================
# EXPERIENCE INSIGHTS
# =====================================================

def _analyze_experience(
    ats_analysis,
    strengths,
    weaknesses,
    critical
):
    experience = _safe_dict(
        ats_analysis.get("experience")
    )

    if not experience.get(
        "present",
        False
    ):

        _add_item(
            weaknesses,
            "Experience section not detected",
            "No experience section was detected. For a fresher "
            "or student resume this can be acceptable, but projects, "
            "internships, coursework, or other relevant evidence "
            "should clearly demonstrate capability.",
            "medium"
        )

        return

    word_count = experience.get(
        "word_count",
        0
    )

    action_verbs = _safe_dict(
        experience.get(
            "action_verbs"
        )
    )

    unique_actions = action_verbs.get(
        "unique",
        0
    )

    if word_count >= 20:

        _add_item(
            strengths,
            "Experience content detected",
            f"The experience section contains approximately "
            f"{word_count} words.",
            "low"
        )

    else:

        _add_item(
            weaknesses,
            "Very limited experience content",
            "The detected experience section is extremely short. "
            "It may not provide enough evidence of responsibilities "
            "or results.",
            "high"
        )

    if unique_actions == 0:

        _add_item(
            weaknesses,
            "Experience lacks recognized action language",
            "Experience entries do not contain recognized action "
            "verbs. Review whether each bullet clearly begins with "
            "a meaningful action.",
            "medium"
        )


# =====================================================
# PROJECT INSIGHTS
# =====================================================

def _analyze_projects(
    ats_analysis,
    strengths,
    weaknesses
):
    projects = _safe_dict(
        ats_analysis.get("projects")
    )

    if not projects.get(
        "present",
        False
    ):

        _add_item(
            weaknesses,
            "Projects section not detected",
            "No projects section was detected. Projects can be "
            "especially useful for students and candidates with "
            "limited professional experience, although they are "
            "not mandatory for every resume.",
            "low"
        )

        return

    word_count = projects.get(
        "word_count",
        0
    )

    technical_terms = _safe_dict(
        projects.get(
            "technical_terms"
        )
    )

    if word_count > 20:

        _add_item(
            strengths,
            "Project evidence detected",
            f"The projects section contains approximately "
            f"{word_count} words.",
            "low"
        )

    if technical_terms.get(
        "unique",
        0
    ) > 0:

        _add_item(
            strengths,
            "Technical project evidence detected",
            "Projects contain recognized technical terminology.",
            "low",
            evidence=list(
                technical_terms.get(
                    "found",
                    {}
                ).keys()
            )
        )


# =====================================================
# STATISTICS
# =====================================================

def _analyze_statistics(
    ats_analysis,
    strengths,
    weaknesses
):
    statistics = _safe_dict(
        ats_analysis.get("statistics")
    )

    word_count = statistics.get(
        "word_count",
        0
    )

    sentence_count = statistics.get(
        "sentence_count",
        0
    )

    if word_count == 0:
        return

    if word_count < 150:

        _add_item(
            weaknesses,
            "Very short resume content",
            f"Only approximately {word_count} words were "
            "extracted. This may indicate missing content or "
            "a genuinely short resume.",
            "medium"
        )

    elif word_count <= 900:

        _add_item(
            strengths,
            "Resume content length",
            f"Approximately {word_count} words were extracted.",
            "low"
        )

    elif word_count <= 1300:

        _add_item(
            weaknesses,
            "Long resume content",
            f"Approximately {word_count} words were extracted. "
            "Review whether every section is relevant.",
            "medium"
        )

    else:

        _add_item(
            weaknesses,
            "Very long resume content",
            f"Approximately {word_count} words were extracted. "
            "The resume may contain unnecessary information.",
            "high"
        )

    if sentence_count:

        average_sentence_length = (
            word_count / sentence_count
        )

        if average_sentence_length > 45:

            _add_item(
                weaknesses,
                "Long sentence structure",
                "Several sentences may be difficult to scan quickly. "
                "Consider shorter, focused bullet points.",
                "medium"
            )


# =====================================================
# MAIN ENGINE
# =====================================================

def generate_resume_insights(
    resume_text,
    sections=None,
    skills=None,
    ats_analysis=None,
    ats_result=None
):
    """
    Generate a complete evidence-based insight report.
    """

    sections = sections or {}
    skills = skills or []
    ats_analysis = ats_analysis or {}
    ats_result = ats_result or {}

    strengths = []
    weaknesses = []
    critical = []

    # -------------------------------------------------
    # Analyze each dimension
    # -------------------------------------------------

    _analyze_sections(
        ats_analysis,
        strengths,
        weaknesses,
        critical
    )

    _analyze_contact(
        ats_analysis,
        strengths,
        weaknesses,
        critical
    )

    _analyze_skills(
        skills,
        ats_analysis,
        strengths,
        weaknesses,
        critical
    )

    _analyze_action_verbs(
        ats_analysis,
        strengths,
        weaknesses
    )

    _analyze_technical_terms(
        ats_analysis,
        strengths,
        weaknesses
    )

    _analyze_impact(
        ats_analysis,
        strengths,
        weaknesses
    )

    _analyze_experience(
        ats_analysis,
        strengths,
        weaknesses,
        critical
    )

    _analyze_projects(
        ats_analysis,
        strengths,
        weaknesses
    )

    _analyze_statistics(
        ats_analysis,
        strengths,
        weaknesses
    )

    # -------------------------------------------------
    # Overall assessment
    # -------------------------------------------------

    score = ats_result.get(
        "score",
        0
    )

    if score >= 85:

        overall = (
            "Strong ATS compatibility based on the evidence "
            "currently detected. This score does not guarantee "
            "a job or interview."
        )

    elif score >= 70:

        overall = (
            "Reasonable ATS compatibility, but there are "
            "specific weaknesses that should be addressed "
            "before relying on this resume."
        )

    elif score >= 50:

        overall = (
            "Moderate ATS compatibility. The resume contains "
            "useful information but has important weaknesses "
            "that may reduce its effectiveness."
        )

    elif score >= 30:

        overall = (
            "Weak ATS compatibility. Several important areas "
            "need improvement before this resume can be considered "
            "competitive."
        )

    else:

        overall = (
            "Very weak ATS compatibility based on the information "
            "that could be extracted. Major improvements are needed."
        )

    # -------------------------------------------------
    # Return complete report
    # -------------------------------------------------

    return {

        "overall": overall,

        "score": score,

        "strengths": strengths,

        "weaknesses": weaknesses,

        "critical_issues": critical,

        "summary": {

            "strength_count": len(
                strengths
            ),

            "weakness_count": len(
                weaknesses
            ),

            "critical_count": len(
                critical
            ),

            "skill_count": len(
                set(skills)
            )
        }
    }