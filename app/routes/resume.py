"""
Resume Routes

Handles:

- Resume upload
- Resume text extraction
- Section detection
- Skill detection
- ATS analysis
- ATS scoring
- Recommendations
- Results rendering
"""

import os
import re
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    session,
)

from werkzeug.utils import secure_filename

from app import db
from app.models.resume import Resume
from app.utils.helpers import login_required


# =====================================================
# PROJECT IMPORTS
# =====================================================

from app.utils.ats_analyzer import analyze_resume
from app.utils.skill_extractor import extract_skills_from_sections
from app.utils.ats_score import calculate_ats_score
from app.utils.recommendation_engine import generate_recommendations


# =====================================================
# OPTIONAL PDF SUPPORT
# =====================================================

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# =====================================================
# OPTIONAL DOCX SUPPORT
# =====================================================

try:
    from docx import Document
except ImportError:
    Document = None


# =====================================================
# BLUEPRINT
# =====================================================

resume = Blueprint(
    "resume",
    __name__,
    url_prefix="/resume",
)


# =====================================================
# ALLOWED FILE TYPES
# =====================================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt",
}


# =====================================================
# FILE VALIDATION
# =====================================================

def allowed_file(filename):
    """
    Check whether the uploaded file type is supported.
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_pdf_text(file_path):
    """
    Extract text from a PDF resume.
    """

    if PdfReader is None:
        raise RuntimeError(
            "pypdf is not installed. "
            "Install it using: pip install pypdf"
        )

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        try:
            page_text = page.extract_text()
        except Exception:
            page_text = ""

        if page_text:
            pages.append(page_text)

    return "\n".join(pages)


# =====================================================
# DOCX TEXT EXTRACTION
# =====================================================

def extract_docx_text(file_path):
    """
    Extract text from a DOCX resume.
    """

    if Document is None:
        raise RuntimeError(
            "python-docx is not installed. "
            "Install it using: pip install python-docx"
        )

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


# =====================================================
# TXT TEXT EXTRACTION
# =====================================================

def extract_txt_text(file_path):
    """
    Extract text from a TXT resume.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "latin-1",
    ]

    for encoding in encodings:

        try:

            with open(
                file_path,
                "r",
                encoding=encoding,
                errors="ignore",
            ) as file:

                return file.read()

        except Exception:
            continue

    return ""


# =====================================================
# GENERIC TEXT EXTRACTION
# =====================================================

def extract_resume_text(file_path, filename):
    """
    Extract resume text based on file extension.
    """

    if "." not in filename:
        return ""

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    if extension == "pdf":
        return extract_pdf_text(file_path)

    if extension == "docx":
        return extract_docx_text(file_path)

    if extension == "txt":
        return extract_txt_text(file_path)

    return ""


# =====================================================
# TEXT NORMALIZATION
# =====================================================

def normalize_text(text):
    """
    Normalize extracted resume text.
    """

    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


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
# CLEAN HEADING
# =====================================================

def _clean_heading(line):
    """
    Clean a possible section heading.
    """

    line = line.strip()

    line = re.sub(
        r"^[•●▪▸►\-–—]+\s*",
        "",
        line
    )

    line = re.sub(
        r"[:|]+$",
        "",
        line
    )

    return line.strip().lower()


# =====================================================
# FIND SECTION NAME
# =====================================================

def _find_section_name(line):
    """
    Determine whether a line represents
    a known resume section.
    """

    cleaned = _clean_heading(line)

    if not cleaned:
        return None

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if cleaned == alias:
                return section

    return None


# =====================================================
# EXTRACT SECTIONS
# =====================================================

def extract_sections(text):
    """
    Detect resume sections from extracted text.

    This is intentionally flexible and does not
    require every resume to contain the same sections.
    """

    sections = {}

    current_section = None

    lines = text.splitlines()

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        detected_section = _find_section_name(line)

        if detected_section:

            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = ""

            continue

        if current_section:

            sections[current_section] += (
                line + "\n"
            )

    # Clean section content
    for section in list(sections.keys()):

        sections[section] = sections[
            section
        ].strip()

    return sections


# =====================================================
# FALLBACK SECTION EXTRACTION
# =====================================================

def ensure_section_structure(text, sections):
    """
    Ensure common sections can still be analyzed
    even when PDF extraction is imperfect.
    """

    sections = sections or {}

    lower_text = text.lower()

    section_patterns = {

        "experience": [
            r"\bwork experience\b",
            r"\bprofessional experience\b",
            r"\bexperience\b",
            r"\binternship\b",
        ],

        "education": [
            r"\beducation\b",
            r"\bacademic background\b",
        ],

        "skills": [
            r"\btechnical skills\b",
            r"\bskills\b",
        ],

        "projects": [
            r"\bprojects\b",
            r"\bacademic projects\b",
        ],

        "certifications": [
            r"\bcertifications\b",
            r"\bcertificates\b",
        ],

        "summary": [
            r"\bprofessional summary\b",
            r"\bsummary\b",
            r"\bobjective\b",
        ],
    }

    for section, patterns in section_patterns.items():

        if section in sections:
            continue

        for pattern in patterns:

            if re.search(
                pattern,
                lower_text
            ):

                sections[section] = ""

                break

    return sections


def cleanup_uploaded_file(file_path):
    """
    Safely remove a temporary uploaded resume file.
    """
    if not file_path:
        return

    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception:
        current_app.logger.exception(
            "Failed to remove temporary uploaded resume."
        )


# =====================================================
# UPLOAD PAGE
# =====================================================

@resume.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload():
    """
    Resume upload and analysis route.
    """

    # =================================================
    # GET
    # =================================================

    if request.method == "GET":

        return render_template(
            "pages/upload.html"
        )

    # =================================================
    # GET UPLOADED FILE
    # =================================================

    uploaded_file = request.files.get(
        "resume"
    )

    if uploaded_file is None:

        flash(
            "Please select a resume file.",
            "error"
        )

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # SECURE FILENAME
    # =================================================

    filename = secure_filename(
        uploaded_file.filename or ""
    )

    if not filename:

        flash(
            "Invalid filename.",
            "error"
        )

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # VALIDATE FILE
    # =================================================

    if not allowed_file(filename):

        flash(
            "Unsupported file type. "
            "Please upload a PDF, DOCX, or TXT file.",
            "error"
        )

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # UPLOAD DIRECTORY
    # =================================================

    upload_folder = current_app.config.get(
        "UPLOAD_FOLDER"
    )

    if not upload_folder:

        upload_folder = os.path.join(
            current_app.root_path,
            "uploads"
        )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    # =================================================
    # FILE PATH
    # =================================================

    file_extension = os.path.splitext(filename)[1].lower()
    temporary_filename = f"{uuid.uuid4().hex}{file_extension}"

    file_path = os.path.join(
        upload_folder,
        temporary_filename
    )

    # =================================================
    # SAVE FILE
    # =================================================

    try:

        uploaded_file.save(
            file_path
        )

    except Exception as error:

        current_app.logger.exception(
            "Failed to save uploaded resume."
        )

        flash(
            f"Unable to save resume: {error}",
            "error"
        )

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # EXTRACT TEXT
    # =================================================

    try:

        resume_text = extract_resume_text(
            file_path,
            filename
        )

    except Exception as error:

        current_app.logger.exception(
            "Resume text extraction failed."
        )

        flash(
            f"Unable to read the resume: {error}",
            "error"
        )

        cleanup_uploaded_file(file_path)

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # NORMALIZE TEXT
    # =================================================

    resume_text = normalize_text(
        resume_text
    )

    # =================================================
    # EMPTY RESUME CHECK
    # =================================================

    if not resume_text:

        flash(
            "No readable text was detected in the resume. "
            "If this is a scanned PDF, OCR may be required.",
            "error"
        )

        cleanup_uploaded_file(file_path)

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # EXTRACT SECTIONS
    # =================================================

    sections = extract_sections(
        resume_text
    )

    sections = ensure_section_structure(
        resume_text,
        sections
    )

    # =================================================
    # EXTRACT SKILLS
    # =================================================

    try:

        skills = extract_skills_from_sections(
            sections
        )

    except Exception as error:

        current_app.logger.exception(
            "Skill extraction failed."
        )

        skills = []

    # =================================================
    # ATS ANALYSIS
    # =================================================

    try:

        ats_analysis = analyze_resume(
            resume_text,
            sections
        )

    except Exception as error:

        current_app.logger.exception(
            "ATS analysis failed."
        )

        flash(
            f"Resume analysis failed: {error}",
            "error"
        )

        cleanup_uploaded_file(file_path)

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # ATS SCORE
    # =================================================

    try:

        ats_result = calculate_ats_score(
            resume_text=resume_text,
            sections=sections,
            skills=skills,
            ats_analysis=ats_analysis,
        )

        print(
            "\n================ ATS RESULT ================"
        )

        print(
            "Overall Score:",
            ats_result.get("score")
        )

        print(
            "Breakdown:",
            ats_result.get("breakdown")
        )

        print(
            "Weights:",
            ats_result.get("weights")
        )

        print(
            "============================================\n"
        )

    except Exception as error:

        current_app.logger.exception(
            "ATS score calculation failed."
        )

        flash(
            f"ATS scoring failed: {error}",
            "error"
        )

        cleanup_uploaded_file(file_path)

        return redirect(
            url_for("resume.upload")
        )

    # =================================================
    # SAVE ANALYSIS HISTORY
    # =================================================

    try:

        if session.get("user_id") is not None:

            saved_resume = Resume(
                user_id=session["user_id"],
                filename=filename,
                resume_text=resume_text,
                ats_score=float(
                    ats_result.get(
                        "score",
                        0.0
                    )
                ),
            )

            db.session.add(
                saved_resume
            )

            db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Failed to save resume analysis."
        )

    # =================================================
    # RECOMMENDATIONS
    # =================================================

    try:

        recommendations = generate_recommendations(
            sections,
            skills,
            ats_analysis,
            ats_result
        )

    except Exception as error:

        current_app.logger.exception(
            "Recommendation generation failed."
        )

        # Do NOT show technical errors to the user.
        # The results page should remain clean.

        recommendations = [
            {
                "type": "critical",
                "category": "Recommendations",
                "message": (
                    "The recommendation engine could not "
                    "generate feedback for this resume."
                ),
            }
        ]

    # =================================================
    # CLEAN UP TEMPORARY UPLOAD
    # =================================================

    cleanup_uploaded_file(file_path)

    # =================================================
    # RESULTS PAGE
    # =================================================

    return render_template(
        "pages/results.html",

        ats_result=ats_result,

        ats_analysis=ats_analysis,

        skills=skills,

        filename=filename,

        recommendations=recommendations,
    )


# =====================================================
# RESULTS ROUTE
# =====================================================

@resume.route(
    "/results"
)
@login_required
def results():
    """
    Direct results access.

    Analysis results are generated during upload,
    so direct access redirects back to upload.
    """

    return redirect(
        url_for("resume.upload")
    )
