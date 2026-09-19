"""
Resume Structure Parser

Detects and separates resume sections while preserving
the original section content.

Important:
- Does not limit the number of sections.
- Supports common section-name variations.
- Preserves section text for downstream evidence analysis.
"""

import re


# =====================================================
# SECTION DEFINITIONS
# =====================================================

SECTION_ALIASES = {

    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career summary",
        "career objective",
        "objective",
        "about me",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "career history",
    ],

    "education": [
        "education",
        "academic",
        "academics",
        "academic background",
        "educational background",
        "education background",
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical skill",
        "core skills",
        "key skills",
        "professional skills",
        "competencies",
        "technical competencies",
        "core competencies",
    ],

    "projects": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "key projects",
        "selected projects",
        "project experience",
    ],

    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "certificate",
        "professional certifications",
    ],

    "achievements": [
        "achievements",
        "achievement",
        "accomplishments",
        "accomplishment",
        "awards",
        "honors",
        "honours",
    ],

    "internships": [
        "internships",
        "internship",
        "intern experience",
        "internship experience",
    ],

    "publications": [
        "publications",
        "publication",
        "research publications",
        "papers",
        "research papers",
    ],

    "languages": [
        "languages",
        "language",
        "spoken languages",
    ],

    "volunteering": [
        "volunteering",
        "volunteer experience",
        "volunteer",
        "community involvement",
    ],

    "interests": [
        "interests",
        "hobbies",
        "hobbies & interests",
        "personal interests",
    ],

    "references": [
        "references",
        "reference",
    ],

    "extracurricular": [
        "extracurricular activities",
        "extracurricular",
        "activities",
        "co-curricular activities",
    ],
}


# =====================================================
# NORMALIZATION
# =====================================================

def normalize_heading(text):
    """
    Normalize a possible section heading.
    """

    if not text:
        return ""

    text = str(text).strip().lower()

    # Remove common heading punctuation
    text = re.sub(
        r"[:\-–—]+$",
        "",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =====================================================
# HEADING LOOKUP
# =====================================================

def identify_section_heading(line):
    """
    Return the canonical section name if the line
    represents a recognized resume section heading.

    Otherwise return None.
    """

    normalized = normalize_heading(
        line
    )

    if not normalized:
        return None

    for section_name, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if normalized == normalize_heading(
                alias
            ):
                return section_name

    return None


# =====================================================
# HEADING HEURISTIC
# =====================================================

def looks_like_heading(line):
    """
    Determine whether a line is likely to be a
    section heading.

    This allows the parser to recognize headings
    that are not explicitly present in our alias list.
    """

    if not line:
        return False

    stripped = line.strip()

    if not stripped:
        return False

    # Too long to normally be a heading
    if len(stripped) > 70:
        return False

    # Full sentence is unlikely to be heading
    if stripped.endswith("."):
        return False

    words = stripped.split()

    # Avoid treating long paragraphs as headings
    if len(words) > 8:
        return False

    # Common heading formatting
    if stripped.isupper():
        return True

    # Markdown-style headings
    if stripped.startswith("#"):
        return True

    # Heading with trailing colon
    if stripped.endswith(":"):
        return True

    return False


# =====================================================
# UNKNOWN SECTION NAME
# =====================================================

def canonicalize_unknown_heading(line):
    """
    Convert an unknown heading into a safe canonical name.

    Example:

        "Technical Tools"

    becomes:

        "technical_tools"
    """

    text = normalize_heading(
        line
    )

    if not text:
        return None

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    )

    text = text.strip("_")

    if not text:
        return None

    return text


# =====================================================
# PARSE SECTIONS
# =====================================================

def parse_resume_sections(text):
    """
    Parse a resume into sections while preserving
    the actual text belonging to each section.

    Returns:

    {
        "summary": "...",
        "experience": "...",
        "skills": "...",
        ...
    }

    Unknown but clearly identifiable sections are also
    preserved rather than discarded.
    """

    if not text:
        return {}

    # -------------------------------------------------
    # Normalize line endings
    # -------------------------------------------------

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    lines = text.split("\n")

    # Remove excessive empty lines
    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if line:
            cleaned_lines.append(line)

    if not cleaned_lines:
        return {}

    sections = {}

    current_section = "header"

    sections[current_section] = []

    # -------------------------------------------------
    # Parse line by line
    # -------------------------------------------------

    for line in cleaned_lines:

        recognized_section = identify_section_heading(
            line
        )

        # ---------------------------------------------
        # Known section
        # ---------------------------------------------

        if recognized_section:

            current_section = recognized_section

            if current_section not in sections:
                sections[current_section] = []

            continue

        # ---------------------------------------------
        # Unknown heading
        # ---------------------------------------------

        if looks_like_heading(line):

            unknown_section = (
                canonicalize_unknown_heading(
                    line
                )
            )

            if unknown_section:

                current_section = unknown_section

                if current_section not in sections:
                    sections[current_section] = []

                continue

        # ---------------------------------------------
        # Normal content
        # ---------------------------------------------

        if current_section not in sections:

            sections[current_section] = []

        sections[current_section].append(
            line
        )

    # =================================================
    # Convert lists into text
    # =================================================

    result = {}

    for section_name, content_lines in sections.items():

        content = "\n".join(
            content_lines
        ).strip()

        if content:

            result[section_name] = content

    return result


# =====================================================
# SECTION METADATA
# =====================================================

def get_section_metadata(sections):
    """
    Generate metadata without destroying the original
    section text.
    """

    metadata = {}

    if not sections:
        return metadata

    for section_name, content in sections.items():

        content = content or ""

        metadata[section_name] = {

            "present": bool(
                content.strip()
            ),

            "word_count": len(
                content.split()
            ),

            "character_count": len(
                content
            ),

            "content": content
        }

    return metadata


# =====================================================
# COMPLETE STRUCTURE ANALYSIS
# =====================================================

def analyze_resume_structure(text):
    """
    Parse the resume and return both section content
    and section metadata.
    """

    sections = parse_resume_sections(
        text
    )

    metadata = get_section_metadata(
        sections
    )

    return {

        "sections": sections,

        "metadata": metadata,

        "section_count": len(
            sections
        ),

        "detected_sections": list(
            sections.keys()
        )
    }