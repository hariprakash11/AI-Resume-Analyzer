# AI Resume Analyzer

A Flask-based resume analysis application that evaluates resumes using ATS-oriented rules, extracts skills, identifies resume sections, generates evidence-based recommendations, and stores analysis history for authenticated users.

## Features

- User registration and login
- Secure password hashing
- Session-based authentication
- Resume upload and text extraction
- Support for PDF and DOCX resumes
- ATS-oriented resume scoring
- Resume section analysis
- Technical and soft-skill extraction
- Evidence-based resume recommendations
- Resume analysis history
- Individual resume reports
- User-specific dashboard
- Temporary upload cleanup
- File size protection
- Custom 404 and 500 error pages
- SQLite database storage
- Responsive web interface

## ATS Analysis

The application evaluates a resume across the following categories:

| Category | Weight |
|---|---:|
| Contact Information | 10 |
| Experience | 20 |
| Skills | 20 |
| Education | 10 |
| Projects | 15 |
| Certifications | 5 |
| Structure | 10 |
| Impact | 10 |
| **Total** | **100** |

The scoring system is rule-based and designed to provide transparent feedback rather than artificially inflate scores.

Recommendations are generated from evidence found in the resume. The system does not invent achievements, metrics, or results.

## Technology Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Werkzeug

### Resume Processing

- pypdf
- python-docx

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2 templates

## Project Structure

```text
AI-Resume-Analyzer/
│
├── app/
│   ├── models/
│   │   ├── resume.py
│   │   ├── user.py
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── home.py
│   │   ├── report.py
│   │   ├── resume.py
│   │   └── upload.py
│   │
│   ├── services/
│   │   ├── ai.py
│   │   ├── ats.py
│   │   ├── ats_engine.py
│   │   ├── parser.py
│   │   ├── recommendation_engine.py
│   │   └── report.py
│   │
│   ├── utils/
│   │   ├── ats_analyzer.py
│   │   ├── ats_score.py
│   │   ├── helpers.py
│   │   ├── job_analyzer.py
│   │   ├── recommendation_engine.py
│   │   ├── resume_parser.py
│   │   ├── resume_structure.py
│   │   ├── skill_extractor.py
│   │   └── ...
│   │
│   ├── static/
│   └── templates/
│
├── instance/
├── uploads/
├── config.py
├── requirements.txt
├── run.py
├── test_recommendations.py
├── .gitignore
└── README.md
