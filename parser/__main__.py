import fitz
import argparse
from src import schema
import json
from datetime import date


def parse_file(input: str, output: str) -> None:
    doc = fitz.open(input)
    with open(output, "w", encoding="utf-8") as f:
        for i, page in enumerate(doc, start=1):
            f.write(f"--- Page {i} ---\n")
            f.write(page.get_text())


def create_mock(input: str, output: str) -> None:
    contact = schema.Contact(
        email="john.doe@example.com",
        phone="+1234567890",
        address="123 Main Street, London",
    )

    personal_info = schema.PersonalInfo(
        full_name="John Doe",
        date_of_birth=date(1990, 5, 20),
        nationality="British",
        contact=contact,
    )

    education = [
        schema.Education(
            degree="BSc Computer Science",
            institution="University of London",
            start_date=date(2008, 9, 1),
            end_date=date(2012, 6, 30),
            field_of_study="Computer Science",
        )
    ]

    work_experience = [
        schema.WorkExperience(
            job_title="Software Engineer",
            company="Tech Corp",
            start_date=date(2012, 7, 1),
            end_date=date(2018, 12, 31),
        )
    ]

    certifications = [
        schema.Certification(
            name="AWS Certified Solutions Architect", issuing_organization="Amazon"
        )
    ]

    languages = [
        schema.Language(language="English", proficiency="native"),
        schema.Language(language="French", proficiency="fluent"),
    ]

    military_experience = [
        schema.MilitaryExperience(
            rank="Lieutenant",
            branch="Army",
            start_date=date(2010, 1, 1),
            end_date=date(2012, 12, 31),
            duties=["Leadership", "Training", "Operations"],
        )
    ]

    skills = ["Python", "Pydantic", "Data Analysis"]

    cv = schema.CVParserSchema(
        personal_info=personal_info,
        education=education,
        work_experience=work_experience,
        skills=skills,
        certifications=certifications,
        languages=languages,
        military_experience=military_experience,
    )
    json_schema = schema.CVParserSchema.model_json_schema()
    with open(output, "w", encoding="utf-8") as f:
        json.dump(json_schema, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF using PyMuPDF."
    )
    parser.add_argument(
        "--api-mock",
        action="store_true",
        help="Run in API mock mode (no real processing).",
    )
    parser.add_argument(
        "--input", default="test/pdf/basic-sample.pdf", help="Path to input PDF file."
    )
    parser.add_argument(
        "--output", default="output.txt", help="Path to output text file."
    )
    args = parser.parse_args()

    if args.api_mock:
        create_mock(args.input, args.output)
        return

    parse_file(args.input, args.output)


if __name__ == "__main__":
    main()
