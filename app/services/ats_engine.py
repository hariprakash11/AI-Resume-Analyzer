"""
ATS Scoring Engine

Evidence-based resume scoring.

Principles:
- No artificial limit on detected skills.
- No artificial limit on detected keywords.
- Detection and scoring are separate.
- Skills listed without supporting evidence are treated cautiously.
- Experience and projects are evaluated using actual content.
- Missing information is reported honestly.
"""

import re


# =====================================================
# CONFIGURATION
# =====================================================

WEIGHTS = {
    "sections": 20,
    "skills": 20,
    "keywords": 15,
    "experience": 20,
    "contact": 10,
    "readability": 15,
}


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _safe_text(text):
    if not text:
        return ""

    return str(text).lower()


def _count_words(text):
    return len(
        re.findall(
            r"\b[\w+#.-]+\b",
            _safe_text(text)
        )
    )


def _has_content(value):

    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, dict):
        return bool(value)

    if isinstance(value, list):
        return bool(value)

    return bool(value)


# =====================================================
# SECTION SCORE
# =====================================================

def _section_score(sections):

    if not sections:
        return 0

    # New parser structure
    if (
        isinstance(sections, dict)
        and "sections" in sections
    ):
        sections = sections.get(
            "sections",
            {}
        )

    available = {
        str(key).lower()
        for key, value in sections.items()
        if _has_content(value)
    }

    aliases = {

        "experience": [
            "experience",
            "work_experience",
            "professional_experience",
            "employment",
            "employment_history",
            "work_history",
        ],

        "education": [
            "education",
            "academic",
            "academics",
            "academic_background",
        ],

        "skills": [
            "skills",
            "technical_skills",
            "core_skills",
            "key_skills",
            "competencies",
        ],

        "summary": [
            "summary",
            "profile",
            "professional_summary",
            "objective",
            "career_objective",
        ],

        "projects": [
            "projects",
            "project",
            "academic_projects",
            "personal_projects",
        ],

        "certifications": [
            "certifications",
            "certification",
            "certificates",
            "certificate",
        ],
    }

    core = [
        "experience",
        "education",
        "skills",
    ]

    additional = [
        "summary",
        "projects",
        "certifications",
    ]

    core_found = 0

    for section in core:

        if any(
            alias in available
            for alias in aliases[section]
        ):
            core_found += 1

    additional_found = 0

    for section in additional:

        if any(
            alias in available
            for alias in aliases[section]
        ):
            additional_found += 1

    core_score = (
        core_found / len(core)
    ) * 70

    additional_score = (
        additional_found / len(additional)
    ) * 30

    return round(
        core_score + additional_score,
        2
    )


# =====================================================
# SKILLS SCORE
# =====================================================

def _skills_score(
    skills,
    evidence_data=None
):
    """
    Evaluate skill coverage AND evidence.

    Number of skills is not enough.

    Example:

    20 skills + weak evidence
        !=
    20 skills + strong evidence
    """

    if not skills:
        return 0

    skill_count = len(
        set(skills)
    )

    # -------------------------------------------------
    # Skill coverage
    # -------------------------------------------------

    if skill_count <= 3:

        coverage = (
            skill_count / 3
        ) * 40

    elif skill_count <= 8:

        coverage = (
            40
            + (
                (skill_count - 3)
                / 5
            ) * 25
        )

    elif skill_count <= 15:

        coverage = (
            65
            + (
                (skill_count - 8)
                / 7
            ) * 15
        )

    else:

        coverage = min(
            80
            + (
                (skill_count - 15)
                * 0.4
            ),
            90
        )

    # -------------------------------------------------
    # Evidence quality
    # -------------------------------------------------

    evidence_score = 0

    if evidence_data:

        evidence_score = evidence_data.get(
            "score",
            0
        )

    # -------------------------------------------------
    # Combine coverage + evidence
    # -------------------------------------------------

    score = (
        coverage * 0.60
        + evidence_score * 0.40
    )

    return round(
        min(score, 100),
        2
    )


# =====================================================
# KEYWORD SCORE
# =====================================================

def _keyword_score(
    resume_text,
    skills,
    ats_analysis=None
):

    if not resume_text:
        return 0

    technical_unique = 0
    action_unique = 0
    technical_total = 0
    action_total = 0

    if ats_analysis:

        technical = ats_analysis.get(
            "technical_terms",
            {}
        )

        action = ats_analysis.get(
            "action_verbs",
            {}
        )

        technical_unique = technical.get(
            "unique",
            0
        )

        technical_total = technical.get(
            "total",
            0
        )

        action_unique = action.get(
            "unique",
            0
        )

        action_total = action.get(
            "total",
            0
        )

    # -------------------------------------------------
    # Technical diversity
    # -------------------------------------------------

    technical_score = min(
        technical_unique * 3,
        45
    )

    # -------------------------------------------------
    # Action vocabulary
    # -------------------------------------------------

    action_score = min(
        action_unique * 2,
        25
    )

    # -------------------------------------------------
    # Skill diversity
    # -------------------------------------------------

    skill_score = min(
        len(set(skills or [])) * 1.5,
        20
    )

    # -------------------------------------------------
    # Natural usage
    # -------------------------------------------------

    usage_bonus = 0

    if technical_total > technical_unique:
        usage_bonus += 5

    if action_total > action_unique:
        usage_bonus += 5

    score = (
        technical_score
        + action_score
        + skill_score
        + usage_bonus
    )

    return round(
        min(score, 100),
        2
    )


# =====================================================
# EXPERIENCE SCORE
# =====================================================

def _experience_score(
    resume_text,
    ats_analysis=None
):

    if not resume_text:
        return 0

    experience = {}

    if ats_analysis:

        experience = ats_analysis.get(
            "experience",
            {}
        )

    # -------------------------------------------------
    # No experience section
    # -------------------------------------------------

    if not experience.get(
        "present",
        False
    ):

        return 35

    score = 35

    # -------------------------------------------------
    # Content depth
    # -------------------------------------------------

    word_count = experience.get(
        "word_count",
        0
    )

    if word_count >= 150:
        score += 20

    elif word_count >= 100:
        score += 15

    elif word_count >= 50:
        score += 10

    elif word_count >= 20:
        score += 5

    # -------------------------------------------------
    # Action verbs
    # -------------------------------------------------

    action_data = experience.get(
        "action_verbs",
        {}
    )

    unique_actions = action_data.get(
        "unique",
        0
    )

    score += min(
        unique_actions * 2,
        15
    )

    # -------------------------------------------------
    # Metrics
    # -------------------------------------------------

    metrics = experience.get(
        "metrics",
        []
    )

    score += min(
        len(metrics) * 3,
        15
    )

    # -------------------------------------------------
    # Achievement evidence
    # -------------------------------------------------

    achievement_count = experience.get(
        "achievement_count",
        0
    )

    score += min(
        achievement_count * 5,
        20
    )

    return round(
        min(score, 100),
        2
    )


# =====================================================
# CONTACT SCORE
# =====================================================

def _contact_score(
    resume_text,
    ats_analysis=None
):

    if not resume_text:
        return 0

    contact = {}

    if ats_analysis:

        contact = ats_analysis.get(
            "contact",
            {}
        )

    if contact:

        score = 0

        if contact.get(
            "email",
            False
        ):
            score += 35

        if contact.get(
            "phone",
            False
        ):
            score += 35

        if contact.get(
            "linkedin",
            False
        ):
            score += 15

        if contact.get(
            "github",
            False
        ):
            score += 10

        if contact.get(
            "portfolio_or_url",
            False
        ):
            score += 5

        return min(
            score,
            100
        )

    return 0


# =====================================================
# READABILITY SCORE
# =====================================================

def _readability_score(
    resume_text,
    ats_analysis=None
):

    word_count = _count_words(
        resume_text
    )

    if word_count == 0:
        return 0

    # -------------------------------------------------
    # Length
    # -------------------------------------------------

    if word_count < 150:

        score = 65

    elif word_count <= 900:

        score = 100

    elif word_count <= 1300:

        score = 85

    else:

        score = 70

    # -------------------------------------------------
    # Sentence density
    # -------------------------------------------------

    if ats_analysis:

        statistics = ats_analysis.get(
            "statistics",
            {}
        )

        sentence_count = statistics.get(
            "sentence_count",
            0
        )

        if (
            sentence_count
            and
            word_count / sentence_count > 45
        ):

            score -= 10

    return round(
        max(score, 0),
        2
    )


# =====================================================
# MAIN ATS CALCULATOR
# =====================================================

def calculate_ats_score(
    resume_text,
    sections=None,
    skills=None,
    ats_analysis=None,
    evidence_data=None,
):

    sections = sections or {}
    skills = skills or []

    # -------------------------------------------------
    # Calculate components
    # -------------------------------------------------

    sections_score = _section_score(
        sections
    )

    skills_score = _skills_score(
        skills,
        evidence_data
    )

    keywords_score = _keyword_score(
        resume_text,
        skills,
        ats_analysis
    )

    experience_score = _experience_score(
        resume_text,
        ats_analysis
    )

    contact_score = _contact_score(
        resume_text,
        ats_analysis
    )

    readability_score = _readability_score(
        resume_text,
        ats_analysis
    )

    # -------------------------------------------------
    # Weighted scores
    # -------------------------------------------------

    weighted_sections = (
        sections_score
        * WEIGHTS["sections"]
        / 100
    )

    weighted_skills = (
        skills_score
        * WEIGHTS["skills"]
        / 100
    )

    weighted_keywords = (
        keywords_score
        * WEIGHTS["keywords"]
        / 100
    )

    weighted_experience = (
        experience_score
        * WEIGHTS["experience"]
        / 100
    )

    weighted_contact = (
        contact_score
        * WEIGHTS["contact"]
        / 100
    )

    weighted_readability = (
        readability_score
        * WEIGHTS["readability"]
        / 100
    )

    # -------------------------------------------------
    # Final score
    # -------------------------------------------------

    final_score = (
        weighted_sections
        + weighted_skills
        + weighted_keywords
        + weighted_experience
        + weighted_contact
        + weighted_readability
    )

    final_score = round(
        min(
            max(final_score, 0),
            100
        ),
        1
    )

    # -------------------------------------------------
    # Return
    # -------------------------------------------------

    return {

        "score": final_score,

        "breakdown": {

            "sections": round(
                weighted_sections,
                1
            ),

            "skills": round(
                weighted_skills,
                1
            ),

            "keywords": round(
                weighted_keywords,
                1
            ),

            "experience": round(
                weighted_experience,
                1
            ),

            "contact": round(
                weighted_contact,
                1
            ),

            "readability": round(
                weighted_readability,
                1
            ),
        },

        "component_scores": {

            "sections": round(
                sections_score,
                1
            ),

            "skills": round(
                skills_score,
                1
            ),

            "keywords": round(
                keywords_score,
                1
            ),

            "experience": round(
                experience_score,
                1
            ),

            "contact": round(
                contact_score,
                1
            ),

            "readability": round(
                readability_score,
                1
            ),
        },

        "metadata": {

            "skill_count": len(
                set(skills)
            ),

            "word_count": _count_words(
                resume_text
            ),

            "evidence_score": (
                evidence_data.get(
                    "score",
                    0
                )
                if evidence_data
                else 0
            ),
        }
    }