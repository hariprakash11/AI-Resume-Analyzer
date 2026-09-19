import sys

from app.utils.resume_parser import extract_resume_text
from app.utils.ats_analyzer import analyze_resume
from app.utils.skill_extractor import extract_skills_from_sections
from app.utils.ats_score import calculate_ats_score
from app.utils.recommendation_engine import generate_recommendations


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python test_recommendations.py "
            '"path\\to\\resume.docx"'
        )
        sys.exit(1)

    path = sys.argv[1]

    print("Loading resume...")
    text = extract_resume_text(path)

    if not text.strip():
        print("ERROR: No resume text could be extracted.")
        sys.exit(1)

    print("Analyzing resume...")
    sections = analyze_resume(text)

    print("Extracting skills...")
    skills = extract_skills_from_sections(sections)

    print("Calculating ATS score...")
    ats_result = calculate_ats_score(
        resume_text=text,
        sections=sections,
        skills=skills,
    )

    print("Generating recommendations...")
    recommendations = generate_recommendations(
        sections=sections,
        skills=skills,
        ats_analysis=sections,
        ats_result=ats_result,
        resume_text=text,
    )

    print()
    print("=" * 70)
    print("ATS SCORE")
    print("=" * 70)

    print("Score:", ats_result.get("score"))

    print()
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    print("Total:", len(recommendations))
    print()

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        severity = recommendation.get(
            "severity",
            "info",
        ).upper()

        category = recommendation.get(
            "category",
            "general",
        )

        message = recommendation.get(
            "message",
            "",
        )

        print(
            f"{index}. [{severity}] "
            f"{category}: {message}"
        )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()