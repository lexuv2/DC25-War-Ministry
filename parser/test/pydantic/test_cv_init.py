import pytest
from datetime import date
from src import schema


def test_full_cv_init() -> None:
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

    assert cv.personal_info.full_name == "John Doe"
    assert cv.personal_info.age >= 18
    assert len(cv.education) == 1
    assert cv.skills == ["Python", "Pydantic", "Data Analysis"]
    assert len(cv.languages) == 2
    assert len(cv.military_experience) == 1
    assert cv.certifications[0].name == "AWS Certified Solutions Architect"
