import re


# =====================================================
# SECTION HELPERS
# =====================================================

def _normalize(text):
    if not text:
        return ""

    text = str(text).lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _contains_term(text, term):
    """
    Safely determine whether a term appears in text.
    """

    text = _normalize(text)
    term = _normalize(term)

    if not text or not term:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(term)
        + r"(?![a-z0-9])"
    )

    return bool(
        re.search(
            pattern,
            text
        )
    )


# =====================================================
# SKILL EVIDENCE
# =====================================================

def analyze_skill_evidence(
    skills,
    sections,
    resume_text=""
):
    """
    Analyze evidence for every detected skill.

    Returns one record for every detected skill.

    Example:

    {
        "python": {
            "detected": True,
            "sections": [
                "skills",
                "projects"
            ],
            "section_count": 2,
            "evidence_strength": "strong"
        }
    }
    """

    skills = skills or []
    sections = sections or {}

    # -------------------------------------------------
    # Support both old and new section structures
    # -------------------------------------------------

    if (
        isinstance(sections, dict)
        and "important" in sections
    ):
        section_data = sections.get(
            "important",
            {}
        )
    else:
        section_data = sections

    evidence = {}

    for skill in sorted(
        set(skills),
        key=lambda value: str(value).lower()
    ):

        skill_name = str(skill)

        matched_sections = []

        # ---------------------------------------------
        # Check every section
        # ---------------------------------------------

        for section_name, content in section_data.items():

            if isinstance(content, dict):

                content = content.get(
                    "content",
                    ""
                )

                # Some analyzers only provide metadata.
                # In that case skip it.
                if not content:
                    continue

            if not content:
                continue

            if _contains_term(
                content,
                skill_name
            ):
                matched_sections.append(
                    str(section_name).lower()
                )

        # ---------------------------------------------
        # Full resume fallback
        # ---------------------------------------------

        resume_contains_skill = _contains_term(
            resume_text,
            skill_name
        )

        # ---------------------------------------------
        # Evidence strength
        # ---------------------------------------------

        section_set = set(
            matched_sections
        )

        has_skills = bool(
            section_set.intersection({
                "skills",
                "technical skills",
                "core skills"
            })
        )

        has_experience = bool(
            section_set.intersection({
                "experience",
                "work experience",
                "professional experience",
                "employment"
            })
        )

        has_projects = bool(
            section_set.intersection({
                "projects",
                "project"
            })
        )

        has_education = bool(
            section_set.intersection({
                "education",
                "academic",
                "academics"
            })
        )

        # ---------------------------------------------
        # Strength rules
        # ---------------------------------------------

        if has_experience and has_projects:

            strength = "strong"

        elif (
            has_experience
            or has_projects
        ):

            strength = "good"

        elif (
            has_skills
            and (
                has_education
                or len(section_set) >= 2
            )
        ):

            strength = "moderate"

        elif has_skills:

            strength = "weak"

        elif matched_sections:

            strength = "moderate"

        elif resume_contains_skill:

            strength = "weak"

        else:

            strength = "unverified"

        evidence[
            skill_name
        ] = {

            "detected": True,

            "sections":
                matched_sections,

            "section_count":
                len(matched_sections),

            "evidence_strength":
                strength,

            "has_skills_section":
                has_skills,

            "has_experience_evidence":
                has_experience,

            "has_project_evidence":
                has_projects,

            "has_education_evidence":
                has_education
        }

    return evidence


# =====================================================
# EVIDENCE SCORE
# =====================================================

def calculate_evidence_score(
    skill_evidence
):
    """
    Convert evidence strength into an overall
    evidence quality score.

    This score is NOT based on the number of skills.

    It measures how well the detected skills are
    supported by actual resume content.
    """

    if not skill_evidence:
        return 0

    strength_values = {

        "strong": 100,

        "good": 80,

        "moderate": 60,

        "weak": 35,

        "unverified": 15
    }

    scores = []

    for evidence in skill_evidence.values():

        strength = evidence.get(
            "evidence_strength",
            "unverified"
        )

        scores.append(
            strength_values.get(
                strength,
                15
            )
        )

    if not scores:
        return 0

    return round(
        sum(scores) / len(scores),
        2
    )


# =====================================================
# EVIDENCE SUMMARY
# =====================================================

def summarize_skill_evidence(
    skill_evidence
):
    """
    Create a simple summary for the results page.
    """

    summary = {

        "total": len(
            skill_evidence
        ),

        "strong": 0,

        "good": 0,

        "moderate": 0,

        "weak": 0,

        "unverified": 0
    }

    for evidence in skill_evidence.values():

        strength = evidence.get(
            "evidence_strength",
            "unverified"
        )

        if strength in summary:

            summary[strength] += 1

    return summary


# =====================================================
# MAIN EVIDENCE ANALYZER
# =====================================================

def analyze_skill_evidence_full(
    skills,
    sections,
    resume_text=""
):
    """
    Complete skill evidence analysis.
    """

    skill_evidence = analyze_skill_evidence(
        skills=skills,
        sections=sections,
        resume_text=resume_text
    )

    evidence_score = calculate_evidence_score(
        skill_evidence
    )

    summary = summarize_skill_evidence(
        skill_evidence
    )

    return {

        "skills": skill_evidence,

        "score": evidence_score,

        "summary": summary
    }