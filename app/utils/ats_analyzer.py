"""
ATS Resume Analyzer

Analyzes resume text for:

- Contact information
- Resume sections
- Action verbs
- Technical keywords
- Quantifiable impact
- Resume length
- Basic ATS structure

This module does NOT calculate the final ATS score.
That responsibility belongs to ats_score.py.
"""

from __future__ import annotations

import re
from typing import Any, Dict


# =====================================================
# SECTION ALIASES
# =====================================================

SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "objective",
        "career objective",
        "about me",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "technical competencies",
        "technologies",
        "skills & technologies",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "work history",
        "internship",
        "internships",
    ],

    "education": [
        "education",
        "academic",
        "academics",
        "academic background",
        "educational background",
    ],

    "projects": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "key projects",
    ],

    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "courses & certifications",
        "licenses & certifications",
    ],

    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
        "honors",
    ],

    "publications": [
        "publications",
        "research",
        "papers",
    ],

    "languages": [
        "languages",
        "language",
    ],

    "interests": [
        "interests",
        "hobbies",
    ],
}


# =====================================================
# ACTION VERBS
# =====================================================

ACTION_VERBS = [
    "achieved",
    "analyzed",
    "architected",
    "automated",
    "built",
    "collaborated",
    "configured",
    "created",
    "deployed",
    "designed",
    "developed",
    "engineered",
    "implemented",
    "improved",
    "integrated",
    "launched",
    "led",
    "managed",
    "migrated",
    "optimized",
    "programmed",
    "reduced",
    "resolved",
    "tested",
    "trained",
    "transformed",
    "maintained",
    "monitored",
    "evaluated",
    "documented",
    "delivered",
    "generated",
]


# =====================================================
# TECHNICAL TERMS
# =====================================================

TECHNICAL_TERMS = [
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "c",
    "go",
    "rust",
    "php",
    "ruby",
    "kotlin",
    "swift",

    # Web
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "nodejs",
    "flask",
    "django",
    "fastapi",

    # Data
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "pandas",
    "numpy",
    "scipy",
    "matplotlib",
    "seaborn",

    # Data Science / AI
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "natural language processing",
    "nlp",
    "computer vision",
    "tensorflow",
    "pytorch",
    "keras",
    "scikit-learn",
    "sklearn",

    # Analytics
    "power bi",
    "tableau",
    "excel",
    "data analysis",
    "data visualization",
    "statistics",

    # Cloud / DevOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "github",
    "gitlab",
    "ci/cd",

    # Big Data
    "hadoop",
    "spark",
    "hive",
    "hdfs",

    # Core CS
    "data structures",
    "algorithms",
    "data structures and algorithms",
    "object oriented programming",
    "oop",
    "dbms",
    "operating systems",
    "computer networks",

    # IoT / Embedded
    "iot",
    "tinyml",
    "esp32",
    "arduino",
    "raspberry pi",
    "gps",
    "gsm",
    "embedded systems",
    "microcontroller",
    "mqtt",

    # Tools
    "jupyter",
    "jupyter notebook",
    "visual studio code",
    "vs code",
    "postman",
    "linux",
]


# =====================================================
# IMPACT PATTERNS
# =====================================================

# These patterns are intentionally conservative.
#
# A percentage by itself is NOT enough.
# For example:
#   "HSC Percentage: 63.33%"
# must NOT count as professional impact.
#
# We only count percentages when they appear in
# achievement/project/work context.

PERCENTAGE_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*%",
    re.IGNORECASE,
)

QUANTITY_PATTERN = re.compile(
    r"\b\d+(?:,\d{3})*\+?\s+"
    r"(?:users?|customers?|clients?|records?|rows?|"
    r"transactions?|datasets?|projects?)\b",
    re.IGNORECASE,
)

TIME_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s+"
    r"(?:hours?|days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)

METRIC_PATTERN = re.compile(
    r"\b(?:accuracy|precision|recall|f1|auc)\s*"
    r"(?:of|:)?\s*\d+(?:\.\d+)?\s*%?",
    re.IGNORECASE,
)

OUTCOME_WITH_NUMBER_PATTERN = re.compile(
    r"\b(?:increased|decreased|reduced|improved|saved|"
    r"grew|boosted|achieved|optimized)\b"
    r".{0,80}?"
    r"\b\d+(?:\.\d+)?\s*%?",
    re.IGNORECASE,
)


# =====================================================
# HELPERS
# =====================================================

def _normalise_text(value: Any) -> str:
    """
    Convert arbitrary input into searchable text.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return " ".join(
            _normalise_text(item)
            for item in value.values()
        )

    if isinstance(value, (list, tuple, set)):
        return " ".join(
            _normalise_text(item)
            for item in value
        )

    return str(value)


def _clean_heading(line: str) -> str:
    """
    Normalize a possible resume section heading.
    """

    line = line.strip()

    line = re.sub(
        r"^[•●▪▸►\-–—]+\s*",
        "",
        line,
    )

    line = re.sub(
        r"[:|]+$",
        "",
        line,
    )

    return line.strip().lower()


def _find_section_name(line: str) -> str | None:
    """
    Detect a known section heading.
    """

    cleaned = _clean_heading(line)

    if not cleaned:
        return None

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if cleaned == alias:
                return section

    return None


def _count_terms(
    text: str,
    terms: list[str],
) -> Dict[str, Any]:
    """
    Count unique technical/action terms found.
    """

    lower_text = text.lower()

    found = []

    for term in terms:

        pattern = (
            r"(?<!\w)"
            + re.escape(term.lower())
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            lower_text,
        ):
            found.append(term)

    return {
        "total": len(found),
        "items": found,
    }


# =====================================================
# SECTION DETECTION
# =====================================================

def _detect_sections(
    text: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Detect resume sections and return their presence,
    word count, and extracted content.
    """

    detected: Dict[str, str] = {}

    current_section: str | None = None

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        section = _find_section_name(line)

        if section:

            current_section = section

            detected.setdefault(
                section,
                "",
            )

            continue

        if current_section:

            detected[current_section] += (
                line + "\n"
            )

    result = {}

    for section in SECTION_ALIASES:

        content = detected.get(
            section,
            "",
        ).strip()

        result[section] = {
            "present": bool(content),

            "word_count": (
                len(content.split())
                if content
                else 0
            ),

            "text": content,
        }

    return result


# =====================================================
# CONTACT ANALYSIS
# =====================================================

def _analyze_contact(
    text: str,
) -> Dict[str, Any]:
    """
    Detect common professional contact information.
    """

    email_match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        re.I,
    )

    phone_match = re.search(
        r"(?:\+?\d[\d\s().-]{8,}\d)",
        text,
    )

    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?"
        r"linkedin\.com/[^\s]+",
        text,
        re.I,
    )

    github_match = re.search(
        r"(?:https?://)?(?:www\.)?"
        r"github\.com/[^\s]+",
        text,
        re.I,
    )

    portfolio_match = re.search(
        r"\bportfolio\b",
        text,
        re.I,
    )

    return {
        "email": bool(email_match),
        "phone": bool(phone_match),
        "linkedin": bool(linkedin_match),
        "github": bool(github_match),
        "portfolio": bool(portfolio_match),
    }


# =====================================================
# IMPACT ANALYSIS
# =====================================================

def _analyze_impact(
    text: str,
) -> Dict[str, Any]:
    """
    Detect measurable professional/project impact.

    Important rules:

    1. Academic percentages are ignored.
       Example:
           HSC Percentage: 63.33%
           SSLC Percentage: 53.2%

    2. A standalone action verb such as "improved"
       does NOT count as measurable impact.

    3. Actual quantities, metrics, percentages, or
       measurable outcomes are counted.

    4. Evidence is analyzed line-by-line so that
       unrelated academic information does not affect
       professional impact scoring.
    """

    if not text:

        return {
            "total": 0,
            "items": [],
        }

    found = []

    # -------------------------------------------------
    # Lines that clearly represent academic information
    # -------------------------------------------------

    academic_context = (
        "education",
        "hsc",
        "sslc",
        "cgpa",
        "percentage",
        "school",
        "higher secondary",
        "secondary school",
        "academic",
        "semester",
        "class x",
        "class xii",
    )

    # -------------------------------------------------
    # Analyze each line independently
    # -------------------------------------------------

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        lower_line = line.lower()

        # -------------------------------------------------
        # Exclude academic/education lines
        # -------------------------------------------------

        if any(
            keyword in lower_line
            for keyword in academic_context
        ):
            continue

        # -------------------------------------------------
        # Percentage evidence
        #
        # Example:
        # "Improved accuracy from 82% to 91%"
        #
        # This is valid impact.
        # -------------------------------------------------

        percentage_matches = PERCENTAGE_PATTERN.findall(
            line
        )

        if percentage_matches:

            for match in percentage_matches:

                found.append(
                    {
                        "type": "percentage",
                        "evidence": line,
                        "match": match,
                    }
                )

        # -------------------------------------------------
        # Quantity evidence
        #
        # Example:
        # "Processed 10,000 records"
        # "Supported 500 users"
        # -------------------------------------------------

        quantity_matches = QUANTITY_PATTERN.findall(
            line
        )

        if quantity_matches:

            for match in quantity_matches:

                if isinstance(match, tuple):

                    match_value = " ".join(match)

                else:

                    match_value = str(match)

                found.append(
                    {
                        "type": "quantity",
                        "evidence": line,
                        "match": match_value,
                    }
                )

        # -------------------------------------------------
        # Time evidence
        #
        # Example:
        # "Reduced processing time by 3 hours"
        # -------------------------------------------------

        time_matches = TIME_PATTERN.findall(
            line
        )

        if time_matches:

            for match in time_matches:

                if isinstance(match, tuple):

                    match_value = " ".join(match)

                else:

                    match_value = str(match)

                found.append(
                    {
                        "type": "time",
                        "evidence": line,
                        "match": match_value,
                    }
                )

        # -------------------------------------------------
        # ML metric evidence
        #
        # Example:
        # "Achieved model accuracy of 94%"
        # -------------------------------------------------

        metric_matches = METRIC_PATTERN.findall(
            line
        )

        if metric_matches:

            for match in metric_matches:

                found.append(
                    {
                        "type": "metric",
                        "evidence": line,
                        "match": match,
                    }
                )

        # -------------------------------------------------
        # Outcome + measurable number
        #
        # Important:
        # "Improved performance"
        # alone is NOT enough.
        #
        # But:
        # "Improved performance by 25%"
        # is measurable impact.
        # -------------------------------------------------

        outcome_matches = (
            OUTCOME_WITH_NUMBER_PATTERN.findall(
                line
            )
        )

        if outcome_matches:

            for match in outcome_matches:

                found.append(
                    {
                        "type": "measurable_outcome",
                        "evidence": line,
                        "match": match.strip(),
                    }
                )

    # -------------------------------------------------
    # Remove exact duplicate evidence
    # -------------------------------------------------

    unique = []

    seen = set()

    for item in found:

        key = (
            item["type"],
            item["evidence"],
            item["match"],
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(item)

    return {
        "total": len(unique),
        "items": unique,
    }


# =====================================================
# ACTION VERB ANALYSIS
# =====================================================

def _analyze_action_verbs(
    text: str,
) -> Dict[str, Any]:
    """
    Detect strong action verbs.
    """

    return _count_terms(
        text,
        ACTION_VERBS,
    )


# =====================================================
# TECHNICAL TERM ANALYSIS
# =====================================================

def _analyze_technical_terms(
    text: str,
) -> Dict[str, Any]:
    """
    Detect technical terminology.
    """

    return _count_terms(
        text,
        TECHNICAL_TERMS,
    )


# =====================================================
# BASIC READABILITY
# =====================================================

def _analyze_readability(
    text: str,
) -> Dict[str, Any]:
    """
    Provide basic resume readability metrics.
    """

    words = text.split()

    word_count = len(words)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    line_count = len(lines)

    if word_count < 250:

        length_rating = "short"

    elif word_count <= 700:

        length_rating = "good"

    elif word_count <= 1000:

        length_rating = "long"

    else:

        length_rating = "very_long"

    return {
        "word_count": word_count,
        "line_count": line_count,
        "length_rating": length_rating,
    }


# =====================================================
# MAIN ANALYZER
# =====================================================

def analyze_resume(
    resume_text: str,
    sections: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Perform complete ATS analysis.

    Parameters
    ----------
    resume_text:
        Extracted resume text.

    sections:
        Sections already detected by resume.py.

    Returns
    -------
    dict
        Detailed ATS analysis.
    """

    text = _normalise_text(
        resume_text
    ).strip()

    # -------------------------------------------------
    # Sections
    # -------------------------------------------------

    detected_sections = _detect_sections(
        text
    )

    # -------------------------------------------------
    # Merge externally detected sections
    # -------------------------------------------------

    if isinstance(
        sections,
        dict,
    ):

        for section, value in sections.items():

            if section not in detected_sections:

                normalized_value = _normalise_text(
                    value
                )

                detected_sections[section] = {
                    "present": bool(
                        normalized_value
                    ),

                    "word_count": len(
                        normalized_value.split()
                    ),

                    "text": normalized_value,
                }

            elif value:

                existing = detected_sections[
                    section
                ]

                if not existing["text"]:

                    normalized_value = _normalise_text(
                        value
                    )

                    existing["text"] = (
                        normalized_value
                    )

                    existing["present"] = True

                    existing["word_count"] = len(
                        normalized_value.split()
                    )

    # -------------------------------------------------
    # Contact
    # -------------------------------------------------

    contact = _analyze_contact(
        text
    )

    # -------------------------------------------------
    # Action verbs
    # -------------------------------------------------

    action_verbs = _analyze_action_verbs(
        text
    )

    # -------------------------------------------------
    # Technical terms
    # -------------------------------------------------

    technical_terms = _analyze_technical_terms(
        text
    )

    # -------------------------------------------------
    # Impact
    # -------------------------------------------------

    impact = _analyze_impact(
        text
    )

    # -------------------------------------------------
    # Readability
    # -------------------------------------------------

    readability = _analyze_readability(
        text
    )

    # -------------------------------------------------
    # Overall section count
    # -------------------------------------------------

    section_count = sum(
        1
        for value in detected_sections.values()
        if value.get("present")
    )

    # -------------------------------------------------
    # Critical structural checks
    # -------------------------------------------------

    structure_issues = []

    if not contact["email"]:

        structure_issues.append(
            "Missing email address"
        )

    if not contact["phone"]:

        structure_issues.append(
            "Missing phone number"
        )

    if not detected_sections.get(
        "skills",
        {},
    ).get(
        "present",
        False,
    ):

        structure_issues.append(
            "Missing skills section"
        )

    if not detected_sections.get(
        "education",
        {},
    ).get(
        "present",
        False,
    ):

        structure_issues.append(
            "Missing education section"
        )

    # -------------------------------------------------
    # Return complete analysis
    # -------------------------------------------------

    return {
        "sections": detected_sections,

        "contact": contact,

        "action_verbs": action_verbs,

        "technical_terms": technical_terms,

        "impact": impact,

        "readability": readability,

        "section_count": section_count,

        "structure_issues": structure_issues,

        "text_length": len(text),

        "word_count": len(
            text.split()
        ),
    }