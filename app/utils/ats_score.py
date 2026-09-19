
"""
ATS Resume Scoring Engine

Calculates an honest ATS score based on:
- Contact information
- Experience
- Skills
- Education
- Projects
- Certifications
- Resume structure
- Measurable impact

The scoring system intentionally avoids rewarding generic wording.
Metrics and concrete evidence are required for impact-related scoring.
"""

import re
from typing import Any, Dict, List


# ============================================================
# ATS WEIGHTS
# ============================================================

WEIGHTS = {
    "contact": 10,
    "experience": 20,
    "skills": 20,
    "education": 10,
    "projects": 15,
    "certifications": 5,
    "structure": 10,
    "impact": 10,
}


# ============================================================
# SCORE BANDS
# ============================================================

RATING_BANDS = (
    (90, "Excellent", "excellent"),
    (75, "Strong", "strong"),
    (60, "Fair", "fair"),
    (40, "Needs Improvement", "needs-improvement"),
    (0, "Critical", "critical"),
)


# ============================================================
# SECTION HELPERS
# ============================================================

def _get_resume_sections(sections: Dict[str, Any]) -> Dict[str, Any]:
    """Handle both flat and nested section structures."""

    if not sections:
        return {}

    nested = sections.get("sections")

    if isinstance(nested, dict):
        return nested

    return sections


def _section_exists(
    sections: Dict[str, Any],
    section_name: str,
) -> bool:
    """Return True when a section contains meaningful content."""

    resume_sections = _get_resume_sections(sections)

    value = resume_sections.get(section_name)

    if value is None:
        return False

    if isinstance(value, dict):

        if "present" in value:
            return bool(value.get("present"))

        return bool(
            str(value.get("text", "") or "").strip()
        )

    return bool(str(value).strip())


def _section_text(
    sections: Dict[str, Any],
    section_name: str,
) -> str:
    """Safely extract text from a resume section."""

    resume_sections = _get_resume_sections(sections)

    value = resume_sections.get(section_name, "")

    if isinstance(value, dict):
        return str(value.get("text", "") or "")

    return str(value or "")


# ============================================================
# CONTACT SCORE
# ============================================================

def _score_contact(
    resume_text: str,
    sections: Dict[str, Any],
) -> float:
    """
    Contact score out of 10.

    Core contact information:
    - Email: 3
    - Phone: 3
    - LinkedIn: 2
    - Location: 1

    One additional point is available only when a clear
    professional portfolio is present.
    """

    text = resume_text or ""

    score = 0.0

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    phone_pattern = r"(?:\+?\d[\d\s().-]{8,}\d)"

    linkedin_pattern = r"linkedin\.com"

    location_pattern = (
        r"\b("
        r"chennai|bangalore|bengaluru|hyderabad|mumbai|delhi|"
        r"pune|kolkata|coimbatore|madurai|india|tamil nadu"
        r")\b"
    )

    if re.search(email_pattern, text, re.I):
        score += 3

    if re.search(phone_pattern, text):
        score += 3

    if re.search(linkedin_pattern, text, re.I):
        score += 2

    if re.search(location_pattern, text, re.I):
        score += 1

    # Do NOT count a generic "www." as a portfolio.
    # GitHub alone is useful but should not automatically make
    # an otherwise complete contact section perfect.
    if re.search(
        r"\bportfolio\b",
        text,
        re.I,
    ):
        score += 1

    return min(score, 10)


# ============================================================
# EXPERIENCE SCORE
# ============================================================

def _score_experience(
    resume_text: str,
    sections: Dict[str, Any],
) -> float:
    """
    Experience score out of 20.
    """

    text = _section_text(
        sections,
        "experience",
    )

    if not text.strip():
        return 0.0

    score = 8.0

    lower_text = text.lower()

    entry_keywords = [
        "intern",
        "developer",
        "engineer",
        "analyst",
        "software",
        "associate",
        "trainee",
        "consultant",
        "specialist",
    ]

    entry_count = sum(
        1
        for keyword in entry_keywords
        if keyword in lower_text
    )

    if entry_count >= 3:
        score += 3
    elif entry_count >= 2:
        score += 2
    elif entry_count >= 1:
        score += 1

    date_pattern = (
        r"\b("
        r"20\d{2}"
        r"|jan(?:uary)?"
        r"|feb(?:ruary)?"
        r"|mar(?:ch)?"
        r"|apr(?:il)?"
        r"|may"
        r"|jun(?:e)?"
        r"|jul(?:y)?"
        r"|aug(?:ust)?"
        r"|sep(?:tember)?"
        r"|oct(?:ober)?"
        r"|nov(?:ember)?"
        r"|dec(?:ember)?"
        r")\b"
    )

    date_matches = re.findall(
        date_pattern,
        text,
        re.I,
    )

    if len(date_matches) >= 2:
        score += 3
    elif len(date_matches) == 1:
        score += 1

    technical_keywords = [
        "python",
        "sql",
        "machine learning",
        "power bi",
        "powerbi",
        "excel",
        "flask",
        "tensorflow",
        "data analysis",
        "dashboard",
        "api",
        "database",
        "software development",
    ]

    technical_count = sum(
        1
        for keyword in technical_keywords
        if keyword in lower_text
    )

    if technical_count >= 4:
        score += 4
    elif technical_count >= 2:
        score += 2
    elif technical_count >= 1:
        score += 1

    return min(score, 20)


# ============================================================
# SKILLS SCORE
# ============================================================

def _score_skills(
    skills: List[str],
) -> float:
    """
    Skills score out of 20.

    This score is based on genuinely detected skills.
    """

    if not skills:
        return 0.0

    count = len(skills)

    if count >= 15:
        return 20.0

    if count >= 12:
        return 18.0

    if count >= 9:
        return 15.0

    if count >= 6:
        return 12.0

    if count >= 4:
        return 8.0

    if count >= 2:
        return 5.0

    return 2.0


# ============================================================
# EDUCATION SCORE
# ============================================================

def _score_education(
    resume_text: str,
    sections: Dict[str, Any],
) -> float:
    """Education score out of 10."""

    text = _section_text(
        sections,
        "education",
    )

    if not text.strip():
        return 0.0

    score = 7.0

    lower_text = text.lower()

    degree_keywords = [
        "bca",
        "b.tech",
        "btech",
        "b.e",
        "be ",
        "mca",
        "m.tech",
        "mtech",
        "msc",
        "m.sc",
        "b.sc",
        "bsc",
        "mba",
        "degree",
        "bachelor",
        "master",
        "university",
        "college",
    ]

    if any(
        keyword in lower_text
        for keyword in degree_keywords
    ):
        score += 2

    if re.search(
        r"\b(cgpa|percentage|percent|%)\b",
        lower_text,
    ):
        score += 1

    return min(score, 10)


# ============================================================
# PROJECT SCORE
# ============================================================

def _score_projects(
    resume_text: str,
    sections: Dict[str, Any],
) -> float:
    """
    Projects score out of 15.

    Base score rewards having an actual project section.
    Additional points require concrete technical detail.

    Generic verbs such as "developed", "built", "created",
    or "implemented" alone do NOT increase the score.
    """

    text = _section_text(
        sections,
        "projects",
    )

    if not text.strip():
        return 0.0

    # Project section itself
    score = 7.0

    lower_text = text.lower()

    technical_keywords = [
        "python",
        "sql",
        "machine learning",
        "flask",
        "streamlit",
        "tensorflow",
        "pandas",
        "numpy",
        "scikit-learn",
        "api",
        "database",
        "html",
        "css",
        "javascript",
        "generative ai",
        "llm",
        "rag",
    ]

    technical_count = sum(
        1
        for keyword in technical_keywords
        if keyword in lower_text
    )

    # Technical implementation detail
    if technical_count >= 5:
        score += 3
    elif technical_count >= 3:
        score += 2
    elif technical_count >= 1:
        score += 1

    # Concrete implementation concepts
    implementation_keywords = [
        "algorithm",
        "model",
        "pipeline",
        "architecture",
        "database",
        "api",
        "authentication",
        "recommendation",
        "classification",
        "prediction",
        "preprocessing",
        "deployment",
        "integration",
    ]

    implementation_count = sum(
        1
        for keyword in implementation_keywords
        if keyword in lower_text
    )

    if implementation_count >= 3:
        score += 2
    elif implementation_count >= 1:
        score += 1

    # Measurable project impact is intentionally handled
    # by _score_impact(), not duplicated here.
    return min(score, 15)


# ============================================================
# CERTIFICATION SCORE
# ============================================================

def _score_certifications(
    resume_text: str,
    sections: Dict[str, Any],
) -> float:
    """
    Certification score out of 5.

    Scoring:
    - Valid certification section: 2
    - Recognizable issuer: +1
    - Completion date: +1
    - Additional quality evidence: +1
    """

    text = _section_text(
        sections,
        "certifications",
    )

    if not text.strip():
        return 0.0

    score = 2.0

    lower_text = text.lower()

    issuers = [
        "tata",
        "forage",
        "mongodb",
        "hackerrank",
        "coursera",
        "google",
        "microsoft",
        "aws",
        "ibm",
        "udemy",
        "meta",
        "oracle",
    ]

    if any(
        issuer in lower_text
        for issuer in issuers
    ):
        score += 1

    # Completion year/date
    if re.search(
        r"\b20\d{2}\b",
        text,
    ):
        score += 1

    # Do NOT award the final point merely because
    # there are three certification lines.
    #
    # The final point requires stronger evidence such as
    # credential IDs, URLs, or clearly specified certification
    # details.
    if re.search(
        r"\b("
        r"credential|certificate id|credential id|"
        r"verify|verification|credential url"
        r")\b",
        lower_text,
    ):
        score += 1

    return min(score, 5)


# ============================================================
# STRUCTURE SCORE
# ============================================================

def _score_structure(
    resume_text: str,
    sections: Dict[str, Any],
) -> float:
    """
    Structure score out of 10.

    Six standard sections alone do not automatically mean
    perfect structure.

    Scoring:
    - 6 sections: 8
    - 5 sections: 7
    - 4 sections: 6
    - 3 sections: 4
    - 2 sections: 2
    - 1 section: 1

    The remaining 2 points are reserved for stronger structural
    evidence such as a clear summary and complete contact data.
    """

    standard_sections = [
        "summary",
        "skills",
        "experience",
        "education",
        "projects",
        "certifications",
    ]

    present_count = sum(
        1
        for section in standard_sections
        if _section_exists(
            sections,
            section,
        )
    )

    if present_count >= 6:
        score = 8.0

    elif present_count == 5:
        score = 7.0

    elif present_count == 4:
        score = 6.0

    elif present_count == 3:
        score = 4.0

    elif present_count == 2:
        score = 2.0

    elif present_count == 1:
        score = 1.0

    else:
        return 0.0

    # One point for a meaningful professional summary
    summary_text = _section_text(
        sections,
        "summary",
    )

    if len(summary_text.split()) >= 30:
        score += 1

    # One point for strong contact completeness:
    # email + phone + LinkedIn.
    contact_text = resume_text or ""

    has_email = bool(
        re.search(
            r"\b[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            contact_text,
            re.I,
        )
    )

    has_phone = bool(
        re.search(
            r"(?:\+?\d[\d\s().-]{8,}\d)",
            contact_text,
        )
    )

    has_linkedin = bool(
        re.search(
            r"linkedin\.com",
            contact_text,
            re.I,
        )
    )

    if has_email and has_phone and has_linkedin:
        score += 1

    return min(score, 10)


# ============================================================
# IMPACT HELPERS
# ============================================================

def _is_academic_line(line: str) -> bool:
    """Prevent academic information from counting as impact."""

    lower_line = line.lower()

    academic_keywords = [
        "education",
        "hsc",
        "sslc",
        "cgpa",
        "percentage",
        "school",
        "academic",
        "semester",
        "bca",
        "b.tech",
        "btech",
        "b.e",
        "degree",
        "university",
        "college",
    ]

    return any(
        keyword in lower_line
        for keyword in academic_keywords
    )


def _contains_metric(line: str) -> bool:
    """Detect real measurable evidence."""

    patterns = [
        r"\b\d+(?:\.\d+)?\s*%",
        r"\b\d+(?:\.\d+)?\s*percent\b",

        r"\b\d[\d,]*\+?\s*"
        r"(?:users?|customers?|records?|rows?|projects?|"
        r"transactions?|items?|datasets?|documents?|"
        r"files?|requests?|applications?)\b",

        r"\b\d+(?:\.\d+)?\s*"
        r"(?:hours?|days?|weeks?|months?|years?)\b",

        r"\b\d+(?:\.\d+)?x\b",

        r"\bfrom\s+\d+(?:\.\d+)?%?\s+"
        r"to\s+\d+(?:\.\d+)?%?\b",
    ]

    return any(
        re.search(
            pattern,
            line,
            re.I,
        )
        for pattern in patterns
    )


def _score_impact(
    resume_text: str,
    sections: Dict[str, Any],
) -> float:
    """
    Impact score out of 10.

    Action verbs alone do not count.

    Metric lines:
    - 0 = 0
    - 1 = 3
    - 2-3 = 5
    - 4+ = 7

    Outcome language can add up to 3 points.
    """

    experience_text = _section_text(
        sections,
        "experience",
    )

    projects_text = _section_text(
        sections,
        "projects",
    )

    combined_text = "\n".join(
        text
        for text in [
            experience_text,
            projects_text,
        ]
        if text.strip()
    )

    if not combined_text.strip():
        return 0.0

    lines = [
        line.strip()
        for line in combined_text.splitlines()
        if line.strip()
    ]

    metric_lines = []

    for line in lines:

        if _is_academic_line(line):
            continue

        if _contains_metric(line):
            metric_lines.append(line)

    metric_count = len(metric_lines)

    if metric_count == 0:
        return 0.0

    if metric_count == 1:
        score = 3.0

    elif metric_count <= 3:
        score = 5.0

    else:
        score = 7.0

    outcome_verbs = [
        "improved",
        "increased",
        "reduced",
        "decreased",
        "saved",
        "optimized",
        "accelerated",
        "achieved",
        "boosted",
        "enhanced",
        "generated",
        "supported",
        "processed",
        "automated",
        "cut",
    ]

    outcome_count = 0

    for line in metric_lines:

        lower_line = line.lower()

        if any(
            verb in lower_line
            for verb in outcome_verbs
        ):
            outcome_count += 1

    score += min(
        outcome_count,
        3,
    )

    return min(score, 10)


# ============================================================
# CATEGORY RESULT BUILDER
# ============================================================

def _build_category_results(
    breakdown: Dict[str, float],
) -> Dict[str, Dict[str, Any]]:
    """
    Convert raw category scores into frontend-friendly data.
    """

    results = {}

    for category, score in breakdown.items():

        weight = WEIGHTS.get(
            category,
            0,
        )

        percentage = (
            score / weight * 100
            if weight
            else 0
        )

        rating = "Critical"
        rating_class = "critical"

        for threshold, band, band_class in RATING_BANDS:

            if percentage >= threshold:

                rating = band
                rating_class = band_class

                break

        results[category] = {
            "score": round(score, 1),
            "maximum": weight,
            "percentage": round(
                percentage,
                1,
            ),
            "rating": rating,
            "rating_class": rating_class,
            "label": category.replace(
                "_",
                " ",
            ).title(),
        }

    return results


# ============================================================
# MAIN ATS SCORE CALCULATION
# ============================================================

def calculate_ats_score(
    resume_text: str = "",
    sections: Dict[str, Any] | None = None,
    skills: List[str] | None = None,
    *args,
    **kwargs,
) -> Dict[str, Any]:
    """Calculate the complete ATS score."""

    sections = sections or {}
    skills = skills or []

    breakdown = {
        "contact": _score_contact(
            resume_text,
            sections,
        ),

        "experience": _score_experience(
            resume_text,
            sections,
        ),

        "skills": _score_skills(
            skills,
        ),

        "education": _score_education(
            resume_text,
            sections,
        ),

        "projects": _score_projects(
            resume_text,
            sections,
        ),

        "certifications": _score_certifications(
            resume_text,
            sections,
        ),

        "structure": _score_structure(
            resume_text,
            sections,
        ),

        "impact": _score_impact(
            resume_text,
            sections,
        ),
    }

    total_score = round(
        sum(breakdown.values()),
        1,
    )

    rating = "Critical"
    rating_class = "critical"

    for threshold, band, band_class in RATING_BANDS:

        if total_score >= threshold:

            rating = band
            rating_class = band_class

            break

    categories = _build_category_results(
        breakdown
    )

    return {
        "score": total_score,
        "breakdown": breakdown,
        "rating": rating,
        "rating_class": rating_class,
        "categories": categories,
        "weights": WEIGHTS,
    }
