"""
Resume Recommendation Engine

Generates actionable, evidence-based recommendations from ATS analysis.

Design goals:
- Honest recommendations
- No fabricated metrics
- Works with flat and nested section structures
- Handles section dictionaries and plain strings safely
- Avoids duplicate recommendations
- Prioritizes the most important issues
"""

import re


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add(
    recommendations,
    severity,
    category,
    message,
):
    """
    Add a recommendation if the same message does not already exist.
    """

    if not message:
        return

    for item in recommendations:
        if item.get("message") == message:
            return

    recommendations.append(
        {
            "severity": severity,
            "category": category,
            "message": message,
        }
    )


def _word_count(text):
    """
    Return the number of words in text.
    """

    if not text:
        return 0

    return len(
        str(text).split()
    )


def _get_resume_sections(sections):
    """
    Return the actual resume section dictionary.

    Supports both:

    1. Flat structure:
       {
           "experience": {...},
           "projects": {...}
       }

    2. Nested structure returned by analyze_resume():
       {
           "sections": {
               "experience": {...},
               "projects": {...}
           }
       }
    """

    if not isinstance(sections, dict):
        return {}

    nested = sections.get("sections")

    if isinstance(nested, dict):
        return nested

    return sections


def _section_value(sections, *names):
    """
    Return the first matching section value.

    The returned value may be:
    - a dictionary
    - a string
    - another simple value
    """

    resume_sections = _get_resume_sections(
        sections
    )

    for name in names:

        if name not in resume_sections:
            continue

        value = resume_sections.get(name)

        if value is None:
            continue

        return value

    return None


def _section_text(sections, *names):
    """
    Return clean text from the first non-empty matching section.

    Supports section values stored as:
    - {"text": "...", "present": True}
    - plain strings
    """

    value = _section_value(
        sections,
        *names,
    )

    if isinstance(value, dict):

        text = value.get(
            "text",
            "",
        )

        return str(
            text or ""
        ).strip()

    if value is None:
        return ""

    return str(
        value
    ).strip()


def _section_present(sections, *names):
    """
    Safely determine whether a resume section is actually present.

    Rules:

    1. Explicit present=True means present.
    2. If present is False but meaningful text exists,
       treat the section as present because the content exists.
    3. Non-empty plain strings count as present.
    4. Empty, None, or missing values count as absent.
    """

    value = _section_value(
        sections,
        *names,
    )

    if value is None:
        return False

    if isinstance(value, dict):

        if value.get(
            "present",
            False,
        ):
            return True

        text = value.get(
            "text",
            "",
        )

        return bool(
            str(
                text or ""
            ).strip()
        )

    return bool(
        str(
            value
        ).strip()
    )


def _has_any(text, keywords):
    """
    Check whether any keyword exists in text.
    """

    if not text:
        return False

    text_lower = str(
        text
    ).lower()

    return any(
        keyword.lower() in text_lower
        for keyword in keywords
    )


def _has_date_information(text):
    """
    Detect real date information.

    This intentionally does NOT treat a generic hyphen as a date.

    Examples that are considered valid:
        2025
        June 2025
        Jun 2025
        2025 - 2026
        2025 - Present
        Jun 2025 - Aug 2025
        Present

    Examples that are NOT considered valid:
        On-site
        Cross-functional
        Git/GitHub
        Python-based
    """

    if not text:
        return False

    text = str(text)

    date_patterns = [

        # Four-digit year.
        r"\b(?:19|20)\d{2}\b",

        # Month + year.
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
        r"\s+(?:19|20)\d{2}\b",

        # Year - year.
        r"\b(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}\b",

        # Year - Present.
        r"\b(?:19|20)\d{2}\s*[-–]\s*present\b",

        # Month year - month year.
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
        r"\s+(?:19|20)\d{2}"
        r"\s*[-–]\s*"
        r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
        r"\s+(?:19|20)\d{2}\b",

        # Present by itself.
        r"\bpresent\b",
    ]

    return any(
        re.search(
            pattern,
            text,
            re.IGNORECASE,
        )
        for pattern in date_patterns
    )


def _has_measurable_impact(text):
    """
    Detect actual measurable evidence.

    A keyword such as:
        accuracy
        dataset
        performance
        users

    is NOT considered measurable by itself.

    Examples that ARE considered measurable:
        95% accuracy
        10,000 records
        500 users
        30% faster
        reduced processing time by 20%
        processed 50,000 rows
        saved 5 hours
        improved response time by 2 seconds

    The goal is to detect actual evidence rather than merely
    detecting words associated with measurements.
    """

    if not text:
        return False

    text = str(text)

    # -----------------------------------------------------------------------
    # Percentage
    # -----------------------------------------------------------------------

    percentage_pattern = re.compile(
        r"\b\d+(?:\.\d+)?\s*%"
    )

    if percentage_pattern.search(text):
        return True

    # -----------------------------------------------------------------------
    # Number + measurable unit
    # -----------------------------------------------------------------------

    number_unit_pattern = re.compile(
        r"\b\d+(?:,\d{3})*(?:\.\d+)?\s*"
        r"(?:"
        r"users?|"
        r"records?|"
        r"rows?|"
        r"datasets?|"
        r"transactions?|"
        r"customers?|"
        r"clients?|"
        r"requests?|"
        r"hours?|"
        r"minutes?|"
        r"seconds?|"
        r"days?|"
        r"months?|"
        r"years?|"
        r"projects?|"
        r"models?|"
        r"files?|"
        r"applications?|"
        r"systems?|"
        r"queries?|"
        r"entries?|"
        r"items?"
        r")\b",
        re.IGNORECASE,
    )

    if number_unit_pattern.search(text):
        return True

    # -----------------------------------------------------------------------
    # Number + accuracy / performance metrics
    # -----------------------------------------------------------------------

    metric_pattern = re.compile(
        r"\b(?:"
        r"accuracy|"
        r"precision|"
        r"recall|"
        r"f1(?:-score)?|"
        r"auc|"
        r"latency|"
        r"throughput|"
        r"performance"
        r")"
        r"\s*(?:of|at|:)?\s*"
        r"\d+(?:\.\d+)?\s*%?",
        re.IGNORECASE,
    )

    if metric_pattern.search(text):
        return True

    # Also support:
    # 95% accuracy
    # 200ms latency
    # 500 requests/sec

    reverse_metric_pattern = re.compile(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:"
        r"ms|"
        r"milliseconds?|"
        r"seconds?|"
        r"requests?/s|"
        r"requests?/sec"
        r")"
        r"(?:\s+\w+){0,3}\s+"
        r"(?:"
        r"latency|"
        r"throughput|"
        r"response\s*time|"
        r"processing\s*time"
        r")?",
        re.IGNORECASE,
    )

    if reverse_metric_pattern.search(text):
        return True

    # -----------------------------------------------------------------------
    # Number + improvement/result wording
    # -----------------------------------------------------------------------

    improvement_pattern = re.compile(
        r"\b(?:"
        r"reduced|"
        r"increased|"
        r"improved|"
        r"decreased|"
        r"saved|"
        r"cut|"
        r"boosted|"
        r"accelerated|"
        r"optimized"
        r")"
        r"\b"
        r"(?:"
        r"\s+\w+"
        r"){0,8}"
        r"\s+"
        r"(?:"
        r"by|"
        r"to|"
        r"from"
        r")"
        r"\s+"
        r"\d+(?:\.\d+)?\s*%?",
        re.IGNORECASE,
    )

    if improvement_pattern.search(text):
        return True

    # -----------------------------------------------------------------------
    # Generic number + result wording
    # -----------------------------------------------------------------------

    result_pattern = re.compile(
        r"\b(?:"
        r"processed|"
        r"handled|"
        r"analyzed|"
        r"served|"
        r"supported|"
        r"trained|"
        r"tested|"
        r"deployed|"
        r"completed"
        r")"
        r"\s+"
        r"(?:"
        r"\d+(?:,\d{3})*(?:\.\d+)?"
        r"|"
        r"\d+(?:\.\d+)?\s*%"
        r")",
        re.IGNORECASE,
    )

    if result_pattern.search(text):
        return True

    return False


# ---------------------------------------------------------------------------
# Main recommendation engine
# ---------------------------------------------------------------------------

def generate_recommendations(
    sections=None,
    skills=None,
    ats_analysis=None,
    ats_result=None,
    resume_text="",
):
    """
    Generate actionable resume recommendations.

    Parameters:
        sections:
            Resume sections returned by analyze_resume().

        skills:
            Extracted skills.

        ats_analysis:
            Detailed ATS analysis.

        ats_result:
            ATS scoring result.

        resume_text:
            Full extracted resume text.

    Returns:
        List of recommendation dictionaries.
    """

    sections = (
        sections
        if isinstance(sections, dict)
        else {}
    )

    skills = (
        skills
        if isinstance(skills, (list, tuple, set))
        else []
    )

    ats_analysis = (
        ats_analysis
        if isinstance(ats_analysis, dict)
        else {}
    )

    ats_result = (
        ats_result
        if isinstance(ats_result, dict)
        else {}
    )

    recommendations = []

    # -----------------------------------------------------------------------
    # Get normalized section data
    # -----------------------------------------------------------------------

    resume_sections = _get_resume_sections(
        sections
    )

    analysis_sections = ats_analysis.get(
        "sections",
        {}
    )

    if not isinstance(
        analysis_sections,
        dict,
    ):
        analysis_sections = {}

    # -----------------------------------------------------------------------
    # Section presence
    # -----------------------------------------------------------------------

    section_messages = {
        "summary": (
            "Add a professional summary that clearly explains "
            "your background, strongest skills, and target role."
        ),

        "skills": (
            "Add a dedicated Skills section containing the technical "
            "skills that are relevant to your target role."
        ),

        "experience": (
            "Add relevant work experience, internships, or practical "
            "experience where applicable."
        ),

        "education": (
            "Add your education details, including degree, institution, "
            "and relevant academic information."
        ),

        "projects": (
            "Add relevant projects that demonstrate your technical "
            "skills and practical experience."
        ),

        "certifications": (
            "Add relevant certifications, courses, or credentials "
            "that support your target role."
        ),
    }

    for section, message in section_messages.items():

        analysis_section = analysis_sections.get(
            section
        )

        if isinstance(
            analysis_section,
            dict,
        ):

            analysis_present = bool(
                analysis_section.get(
                    "present",
                    False,
                )
            )

            analysis_text = str(
                analysis_section.get(
                    "text",
                    "",
                )
                or ""
            ).strip()

            present = (
                analysis_present
                or bool(analysis_text)
                or _section_present(
                    sections,
                    section,
                )
            )

        else:

            present = _section_present(
                sections,
                section,
            )

        if not present:

            _add(
                recommendations,
                "warning",
                section,
                message,
            )

    # -----------------------------------------------------------------------
    # Extract section text
    # -----------------------------------------------------------------------

    summary_text = _section_text(
        sections,
        "summary",
        "professional_summary",
        "profile",
    )

    skills_text = _section_text(
        sections,
        "skills",
        "core_skills",
        "technical_skills",
    )

    experience_text = _section_text(
        sections,
        "experience",
        "work_experience",
        "employment",
    )

    education_text = _section_text(
        sections,
        "education",
        "academic",
    )

    projects_text = _section_text(
        sections,
        "projects",
        "project",
    )

    certifications_text = _section_text(
        sections,
        "certifications",
        "certification",
        "courses",
    )

    # -----------------------------------------------------------------------
    # Skills quality
    # -----------------------------------------------------------------------

    skill_count = len(
        {
            str(skill).strip().lower()
            for skill in skills
            if str(skill).strip()
        }
    )

    if skill_count == 0 and _section_present(
        sections,
        "skills",
        "core_skills",
        "technical_skills",
    ):

        _add(
            recommendations,
            "warning",
            "skills",
            "Your Skills section was detected, but no clearly recognized skills were extracted. Use standard skill names and avoid placing important skills only inside graphics or images.",
        )

    elif 1 <= skill_count < 5:

        _add(
            recommendations,
            "warning",
            "skills",
            "Your resume contains only a small number of clearly detected skills. Add more relevant technical skills that you genuinely know and can discuss in an interview.",
        )

    elif skill_count < 10:

        _add(
            recommendations,
            "info",
            "skills",
            "Consider adding more relevant technical skills if you have genuinely used them in projects, coursework, internships, or other practical work.",
        )

    # -----------------------------------------------------------------------
    # Action verbs
    # -----------------------------------------------------------------------

    action_verbs = [
        "built",
        "developed",
        "implemented",
        "created",
        "designed",
        "analyzed",
        "optimized",
        "automated",
        "engineered",
        "integrated",
        "deployed",
        "tested",
        "configured",
        "processed",
        "managed",
        "led",
        "improved",
    ]

    experience_and_projects = (
        f"{experience_text}\n"
        f"{projects_text}"
    )

    if (
        experience_and_projects.strip()
        and not _has_any(
            experience_and_projects,
            action_verbs,
        )
    ):

        _add(
            recommendations,
            "info",
            "experience",
            "Use stronger action verbs such as built, developed, implemented, analyzed, automated, optimized, or integrated to describe your actual contributions.",
        )

    # -----------------------------------------------------------------------
    # Technical keywords in experience
    # -----------------------------------------------------------------------

    technical_keywords = [
        "python",
        "sql",
        "pandas",
        "numpy",
        "power bi",
        "excel",
        "flask",
        "streamlit",
        "tensorflow",
        "scikit-learn",
        "mongodb",
        "sqlite",
        "javascript",
        "html",
        "css",
        "machine learning",
        "generative ai",
        "llm",
        "rag",
        "api",
    ]

    if experience_text:

        experience_has_technical = _has_any(
            experience_text,
            technical_keywords,
        )

        if not experience_has_technical:

            _add(
                recommendations,
                "info",
                "experience",
                "Where applicable, mention the technologies you actually used in each experience entry. This makes your practical experience easier for recruiters and ATS systems to understand.",
            )

    # -----------------------------------------------------------------------
    # Experience dates
    # -----------------------------------------------------------------------

    if experience_text:

        has_date_information = _has_date_information(
            experience_text
        )

        if not has_date_information:

            _add(
                recommendations,
                "warning",
                "experience",
                "Add the start and end date for each internship or work experience entry. Dates help recruiters understand their timeline and allow the ATS to properly interpret their experience.",
            )

    # -----------------------------------------------------------------------
    # Experience detail quality
    # -----------------------------------------------------------------------

    if experience_text:

        experience_lines = [
            line.strip()
            for line in experience_text.splitlines()
            if line.strip()
        ]

        generic_experience_phrases = [
            "worked on",
            "responsible for",
            "helped with",
            "involved in",
            "participated in",
            "worked with",
        ]

        generic_count = sum(
            1
            for line in experience_lines
            if _has_any(
                line,
                generic_experience_phrases,
            )
        )

        if (
            len(experience_lines) <= 3
            or generic_count >= 2
        ):

            _add(
                recommendations,
                "info",
                "experience",
                "Some experience bullets describe activities in broad terms without showing the specific work you performed. Replace generic descriptions with concrete responsibilities, technologies used, deliverables, and outcomes.",
            )

    # -----------------------------------------------------------------------
    # Education quality
    # -----------------------------------------------------------------------

    if education_text:

        degree_keywords = [
            "bca",
            "b.sc",
            "bsc",
            "b.e",
            "be",
            "b.tech",
            "btech",
            "mca",
            "m.sc",
            "msc",
            "m.e",
            "me",
            "m.tech",
            "mba",
            "degree",
            "bachelor",
            "master",
            "diploma",
        ]

        if not _has_any(
            education_text,
            degree_keywords,
        ):

            _add(
                recommendations,
                "warning",
                "education",
                "Clearly state your degree or qualification in the Education section so recruiters and ATS systems can identify your academic level.",
            )

    # -----------------------------------------------------------------------
    # Contact information
    # -----------------------------------------------------------------------

    contact_text = str(
        resume_text or ""
    )

    if not contact_text.strip():

        contact_text = "\n".join(
            [
                summary_text,
                skills_text,
                experience_text,
                education_text,
                projects_text,
                certifications_text,
            ]
        )

    # -----------------------------------------------------------------------
    # Email detection
    # -----------------------------------------------------------------------

    has_email = bool(
        re.search(
            r"\b[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            contact_text,
            re.IGNORECASE,
        )
    )

    # -----------------------------------------------------------------------
    # Phone detection
    # -----------------------------------------------------------------------

    has_phone = bool(
        re.search(
            r"(?:\+?\d[\d\s().-]{8,}\d)",
            contact_text,
        )
    )

    # -----------------------------------------------------------------------
    # LinkedIn detection
    # -----------------------------------------------------------------------

    has_linkedin = bool(
        re.search(
            r"(?:https?://)?(?:www\.)?"
            r"linkedin\.com/[^\s]+",
            contact_text,
            re.IGNORECASE,
        )
    )

    # -----------------------------------------------------------------------
    # GitHub detection
    # -----------------------------------------------------------------------

    has_github = bool(
        re.search(
            r"(?:https?://)?(?:www\.)?"
            r"github\.com/[^\s]+",
            contact_text,
            re.IGNORECASE,
        )
    )

    # -----------------------------------------------------------------------
    # Portfolio detection
    # -----------------------------------------------------------------------

    has_portfolio = bool(
        re.search(
            r"\bportfolio\b",
            contact_text,
            re.IGNORECASE,
        )
    )

    # -----------------------------------------------------------------------
    # Contact recommendations
    # -----------------------------------------------------------------------

    if not has_email:

        _add(
            recommendations,
            "critical",
            "contact",
            "Add a professional email address to your resume header.",
        )

    if not has_phone:

        _add(
            recommendations,
            "warning",
            "contact",
            "Add a reachable phone number to your resume header.",
        )

    if not has_linkedin:

        _add(
            recommendations,
            "info",
            "contact",
            "Add your LinkedIn profile if you have one, using a clean and professional profile URL.",
        )

    # GitHub and portfolio are optional supporting links.
    # Give one combined recommendation only when neither is detected.
    if not has_github and not has_portfolio:

        _add(
            recommendations,
            "info",
            "contact",
            "Your resume does not include a GitHub or portfolio link. If you have one, consider adding it to showcase your projects and technical work.",
        )

    # -----------------------------------------------------------------------
    # Impact / measurable evidence
    # -----------------------------------------------------------------------

    impact_source = (
        f"{experience_text}\n"
        f"{projects_text}"
    )

    has_impact = _has_measurable_impact(
        impact_source
    )

    if (
        impact_source.strip()
        and not has_impact
    ):

        _add(
            recommendations,
            "warning",
            "impact",
            "Your resume explains what you did, but it doesn't clearly show the results of your work. Add real numbers where possible, such as model accuracy, records processed, users supported, time saved, or performance improvements. Do not add numbers unless you can support them.",
        )

    # -----------------------------------------------------------------------
    # Project quality
    # -----------------------------------------------------------------------

    if projects_text:

        project_technical_keywords = [
            "python",
            "sql",
            "pandas",
            "numpy",
            "flask",
            "streamlit",
            "tensorflow",
            "scikit-learn",
            "power bi",
            "excel",
            "mongodb",
            "sqlite",
            "javascript",
            "html",
            "css",
            "machine learning",
            "generative ai",
            "llm",
            "rag",
            "api",
        ]

        implementation_keywords = [
            "built",
            "developed",
            "implemented",
            "created",
            "designed",
            "integrated",
            "trained",
            "deployed",
            "tested",
            "processed",
            "analyzed",
            "automated",
        ]

        has_project_technology = _has_any(
            projects_text,
            project_technical_keywords,
        )

        has_implementation = _has_any(
            projects_text,
            implementation_keywords,
        )

        if not has_project_technology:

            _add(
                recommendations,
                "info",
                "projects",
                "Mention the technologies and tools actually used in each project. This gives recruiters clearer evidence of your technical experience.",
            )

        if not has_implementation:

            _add(
                recommendations,
                "info",
                "projects",
                "Describe what you actually built or implemented in each project instead of only describing the project objective.",
            )

        if not has_impact:

            _add(
                recommendations,
                "info",
                "projects",
                "Your projects explain what you built, but they don't show the results you achieved. If you have real results, mention them—for example, model accuracy, dataset size, number of users, processing time, or performance improvements. Do not make up results.",
            )

    # -----------------------------------------------------------------------
    # Certifications
    # -----------------------------------------------------------------------

    if certifications_text:

        certification_issuer_keywords = [
            "coursera",
            "udemy",
            "forage",
            "tata",
            "hackerank",
            "hackerrank",
            "mongodb",
            "microsoft",
            "google",
            "aws",
            "ibm",
            "oracle",
            "nptel",
            "simplilearn",
            "linkedin",
            "accenture",
            "cognizant",
            "infosys",
        ]

        if not _has_any(
            certifications_text,
            certification_issuer_keywords,
        ):

            _add(
                recommendations,
                "info",
                "certifications",
                "Where available, include the issuing organization for each certification so recruiters can better understand the credential.",
            )

        certification_date_keywords = [
            "2020",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
            "2026",
            "2027",
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]

        if not _has_any(
            certifications_text,
            certification_date_keywords,
        ):

            _add(
                recommendations,
                "info",
                "certifications",
                "Add completion dates to your certifications where available. This gives recruiters clearer evidence of when the credential was earned.",
            )

    # -----------------------------------------------------------------------
    # Summary quality
    # -----------------------------------------------------------------------

    summary_words = _word_count(
        summary_text
    )

    if summary_text:

        if summary_words < 20:

            _add(
                recommendations,
                "info",
                "summary",
                "Your professional summary is quite short. Add a concise description of your background, strongest relevant skills, practical experience, and target role.",
            )

        elif summary_words > 100:

            _add(
                recommendations,
                "info",
                "summary",
                "Your professional summary is lengthy. Keep it concise and focused on your strongest qualifications and target role.",
            )

    # -----------------------------------------------------------------------
    # Overall ATS score assessment
    # -----------------------------------------------------------------------

    overall_score = None

    if isinstance(
        ats_result.get("score"),
        (int, float),
    ):

        overall_score = float(
            ats_result.get("score")
        )

    elif isinstance(
        ats_result.get("total"),
        (int, float),
    ):

        overall_score = float(
            ats_result.get("total")
        )

    if overall_score is not None:

        if overall_score < 60:

            _add(
                recommendations,
                "critical",
                "overall",
                "Your ATS score indicates several important resume weaknesses. Prioritize missing sections, contact information, relevant skills, experience detail, project evidence, and measurable impact before focusing on visual formatting.",
            )

        elif overall_score < 75:

            _add(
                recommendations,
                "warning",
                "overall",
                "Your resume has a reasonable ATS foundation but still has areas that can be strengthened. Focus first on measurable impact, specific experience details, relevant skills, and project evidence.",
            )

        elif overall_score < 90:

            _add(
                recommendations,
                "info",
                "overall",
                "Your resume has a solid ATS foundation, but a good score does not mean the resume is recruiter-ready. Prioritize the categories where points were lost, especially measurable impact and evidence of results.",
            )

        else:

            _add(
                recommendations,
                "info",
                "overall",
                "Your resume has a strong ATS foundation. Continue improving it by tailoring keywords and achievements to each target job description while keeping all claims truthful.",
            )

    # -----------------------------------------------------------------------
    # Remove duplicate messages
    # -----------------------------------------------------------------------

    unique_recommendations = []

    seen_messages = set()

    for recommendation in recommendations:

        message = recommendation.get(
            "message",
            "",
        ).strip()

        if not message:
            continue

        message_key = message.lower()

        if message_key in seen_messages:
            continue

        seen_messages.add(
            message_key
        )

        unique_recommendations.append(
            recommendation
        )

    # -----------------------------------------------------------------------
    # Priority sorting
    # -----------------------------------------------------------------------

    severity_priority = {
        "critical": 0,
        "warning": 1,
        "info": 2,
        "success": 3,
    }

    category_priority = {
        "contact": 0,
        "experience": 1,
        "skills": 2,
        "education": 3,
        "projects": 4,
        "certifications": 5,
        "impact": 6,
        "summary": 7,
        "overall": 8,
    }

    unique_recommendations.sort(
        key=lambda item: (
            severity_priority.get(
                item.get(
                    "severity",
                    "info",
                ),
                99,
            ),
            category_priority.get(
                item.get(
                    "category",
                    "overall",
                ),
                99,
            ),
        )
    )

    return unique_recommendations