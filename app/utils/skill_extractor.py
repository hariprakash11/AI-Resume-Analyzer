import re


# =====================================================
# SKILL DATABASE
# =====================================================

SKILL_DATABASE = {

    # Programming
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "c": ["c programming", "c language"],
    "cpp": ["c++"],
    "csharp": ["c#", "c sharp"],
    "php": ["php"],
    "ruby": ["ruby"],
    "go": ["golang", "go language"],
    "rust": ["rust"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "r": ["r programming", "r language"],

    # Databases / Data
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "oracle": ["oracle database", "oracle db"],
    "mongodb": ["mongodb", "mongo db"],
    "sqlite": ["sqlite"],
    "redis": ["redis"],
    "cassandra": ["cassandra"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scipy": ["scipy"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "plotly": ["plotly"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "microsoft excel"],
    "power query": ["power query"],
    "power pivot": ["power pivot"],

    # AI / ML
    "machine learning": [
        "machine learning",
        "machine-learning",
    ],
    "deep learning": [
        "deep learning",
        "deep-learning",
    ],
    "artificial intelligence": [
        "artificial intelligence",
    ],
    "natural language processing": [
        "natural language processing",
        "nlp",
    ],
    "computer vision": [
        "computer vision",
    ],
    "generative ai": [
        "generative ai",
        "generative artificial intelligence",
        "genai",
        "gen ai",
    ],
    "large language models": [
        "large language models",
        "large language model",
        "llm",
        "llms",
    ],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "keras": ["keras"],
    "scikit-learn": [
        "scikit-learn",
        "sklearn",
    ],
    "opencv": [
        "opencv",
        "open cv",
    ],
    "hugging face": [
        "hugging face",
        "huggingface",
    ],
    "langchain": ["langchain"],
    "mlflow": ["mlflow"],

    # Web
    "html": ["html"],
    "css": ["css"],
    "react": ["react", "react.js"],
    "angular": ["angular"],
    "vue": ["vue", "vue.js"],
    "node.js": [
        "node.js",
        "nodejs",
        "node js",
    ],
    "express.js": [
        "express.js",
        "expressjs",
        "express js",
    ],
    "flask": ["flask"],
    "django": ["django"],
    "fastapi": ["fastapi"],
    "rest api": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
    ],
    "graphql": ["graphql"],

    # Cloud / DevOps
    "aws": [
        "aws",
        "amazon web services",
    ],
    "azure": [
        "azure",
        "microsoft azure",
    ],
    "google cloud": [
        "google cloud",
        "gcp",
        "google cloud platform",
    ],
    "docker": ["docker"],
    "kubernetes": [
        "kubernetes",
        "k8s",
    ],
    "jenkins": ["jenkins"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],

    # Git / Version Control
    "git": [
        "git",
        "git basics",
    ],
    "github": ["github"],
    "gitlab": ["gitlab"],
    "bitbucket": ["bitbucket"],
    "linux": ["linux"],
    "bash": [
        "bash",
        "shell scripting",
    ],
    "ci/cd": [
        "ci/cd",
        "ci cd",
        "continuous integration",
        "continuous deployment",
    ],

    # Big Data
    "hadoop": ["hadoop"],
    "spark": [
        "spark",
        "apache spark",
    ],
    "pyspark": [
        "pyspark",
        "py spark",
    ],
    "hive": [
        "hive",
        "apache hive",
    ],
    "hdfs": ["hdfs"],
    "kafka": [
        "kafka",
        "apache kafka",
    ],
    "airflow": [
        "airflow",
        "apache airflow",
    ],
    "databricks": ["databricks"],
    "snowflake": ["snowflake"],

    # Mobile
    "android": ["android"],
    "ios": ["ios"],
    "flutter": ["flutter"],
    "react native": ["react native"],

    # Tools
    "jira": ["jira"],
    "confluence": ["confluence"],
    "figma": ["figma"],
    "powerpoint": [
        "powerpoint",
        "microsoft powerpoint",
    ],
    "word": [
        "microsoft word",
        "ms word",
    ],

    # Soft Skills
    "communication": ["communication"],
    "leadership": ["leadership"],
    "problem solving": [
        "problem solving",
        "problem-solving",
    ],
    "teamwork": [
        "teamwork",
        "team work",
        "team player",
    ],
    "time management": ["time management"],
    "critical thinking": ["critical thinking"],
    "analytical thinking": ["analytical thinking"],

    # Resume-specific technical concepts
    "prompt engineering": ["prompt engineering"],
    "rag": ["rag"],
    "embeddings": [
        "embeddings",
        "embedding",
    ],
    "function calling": [
        "function calling",
        "tool calling",
        "tool/function calling",
        "tool / function calling",
    ],
    "memory systems": ["memory systems"],
    "context management": ["context management"],
    "agentic ai": ["agentic ai"],
    "ai guardrails": ["ai guardrails"],
    "modular architecture": ["modular architecture"],
    "predictive modeling": [
        "predictive modeling",
        "predictive modeling fundamentals",
    ],
    "tinyml": ["tinyml"],
    "documentation": ["documentation"],
    "cross-functional collaboration": [
        "cross-functional collaboration",
    ],
    "team leadership": ["team leadership"],
}


# =====================================================
# SKILL CATEGORY LABELS
# =====================================================

SKILL_CATEGORY_LABELS = {
    "programming languages",
    "gen ai",
    "web & application",
    "architecture",
    "machine learning & embedded",
    "python libraries",
    "tools & platforms",
    "professional skills",
    "technical skills",
    "skills",
}


# =====================================================
# NORMALIZE TEXT
# =====================================================

def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower()

    text = text.replace("â€“", "-")
    text = text.replace("â€”", "-")
    text = text.replace("â€¢", "•")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =====================================================
# EXTRACT TEXT FROM SECTION VALUE
# =====================================================

def _section_value_to_text(value):
    """
    Convert a resume section into plain text.

    Supports:

        "Python, SQL, Flask"

    and:

        {
            "present": True,
            "word_count": 10,
            "text": "Python, SQL, Flask"
        }
    """

    if value is None:
        return ""

    if isinstance(value, dict):
        return str(
            value.get(
                "text",
                "",
            )
        )

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        return "\n".join(
            str(item)
            for item in value
        )

    return str(value)


# =====================================================
# GET ACTUAL RESUME SECTIONS
# =====================================================

def _get_resume_sections(sections):
    """
    Handle both formats:

    Direct:
        {
            "skills": {...},
            "experience": {...}
        }

    Nested:
        {
            "sections": {
                "skills": {...},
                "experience": {...}
            }
        }
    """

    if not isinstance(
        sections,
        dict,
    ):
        return {}

    nested_sections = sections.get(
        "sections"
    )

    if isinstance(
        nested_sections,
        dict,
    ):
        return nested_sections

    return sections


# =====================================================
# NORMALIZE SKILL NAME
# =====================================================

def _normalize_skill_name(skill):

    if not skill:
        return ""

    cleaned = re.sub(
        r"^[\s*\\\-•]+",
        "",
        str(skill).strip(),
    )

    cleaned = re.sub(
        r"[.,;:]+$",
        "",
        cleaned,
    ).strip()

    if not cleaned:
        return ""

    normalized = normalize_text(
        cleaned
    )

    # Remove category labels
    if normalized in SKILL_CATEGORY_LABELS:
        return ""

    # Exact canonical skill
    if normalized in SKILL_DATABASE:
        return normalized

    # Alias matching
    for canonical, aliases in SKILL_DATABASE.items():

        for alias in aliases:

            if normalized == normalize_text(
                alias
            ):
                return canonical

    # Unknown explicit skill
    return cleaned


# =====================================================
# EXPLICIT SKILLS FROM SKILLS SECTION
# =====================================================

def _extract_explicit_skills_from_section(
    skills_text,
):
    if not skills_text:
        return set()

    found = set()

    for raw_line in skills_text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        # Remove bullets
        line = re.sub(
            r"^[\s*\\\-•]+",
            "",
            line,
        ).strip()

        # Handle:
        #
        # Programming Languages: Python, SQL
        #
        if ":" in line:

            category, value = line.split(
                ":",
                1,
            )

            category_normalized = normalize_text(
                category
            )

            if (
                category_normalized
                in SKILL_CATEGORY_LABELS
            ):
                line = value.strip()

        # Split skills
        parts = re.split(
            r"[,|;\u2022]+",
            line,
        )

        for part in parts:

            skill = _normalize_skill_name(
                part
            )

            if not skill:
                continue

            # Ignore descriptions
            if len(skill) > 60:
                continue

            if len(skill.split()) > 6:
                continue

            found.add(skill)

    return found


# =====================================================
# FIND DATABASE SKILLS
# =====================================================

def _find_database_skills(text):

    normalized_text = normalize_text(
        text
    )

    found_skills = set()

    if not normalized_text:
        return found_skills

    for canonical, aliases in SKILL_DATABASE.items():

        for alias in aliases:

            alias_normalized = normalize_text(
                alias
            )

            if not alias_normalized:
                continue

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(alias_normalized)
                + r"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                normalized_text,
            ):
                found_skills.add(
                    canonical
                )
                break

    return found_skills


# =====================================================
# FIND SKILLS
# =====================================================

def extract_skills(text):

    if not text:
        return []

    found_skills = _find_database_skills(
        text
    )

    return sorted(
        found_skills,
        key=lambda value: value.lower(),
    )


# =====================================================
# EXTRACT ALL SKILLS
# =====================================================

def extract_all_skills(
    text,
    skills_section=None,
):
    if not text:
        return []

    found_skills = _find_database_skills(
        text
    )

    if skills_section:

        explicit_skills = (
            _extract_explicit_skills_from_section(
                skills_section
            )
        )

        found_skills.update(
            explicit_skills
        )

    return sorted(
        found_skills,
        key=lambda value: value.lower(),
    )


# =====================================================
# EXTRACT SKILLS FROM SECTIONS
# =====================================================

def extract_skills_from_sections(
    sections,
):
    """
    Extract skills from:

        Skills
        Experience
        Projects
        Education

    Handles the actual structure returned by
    analyze_resume():

        {
            "sections": {
                "skills": {...},
                "experience": {...},
                "projects": {...},
                "education": {...}
            }
        }
    """

    if not sections:
        return []

    resume_sections = _get_resume_sections(
        sections
    )

    skills_text = _section_value_to_text(
        resume_sections.get(
            "skills",
            "",
        )
    )

    experience_text = _section_value_to_text(
        resume_sections.get(
            "experience",
            "",
        )
    )

    projects_text = _section_value_to_text(
        resume_sections.get(
            "projects",
            "",
        )
    )

    education_text = _section_value_to_text(
        resume_sections.get(
            "education",
            "",
        )
    )

    combined_text = "\n".join(
        value
        for value in [
            skills_text,
            experience_text,
            projects_text,
            education_text,
        ]
        if value.strip()
    )

    if not combined_text.strip():
        return []

    return extract_all_skills(
        combined_text,
        skills_section=skills_text,
    )