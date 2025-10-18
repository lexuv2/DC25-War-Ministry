from datetime import date
import pytest
from pydantic import ValidationError
from src import schema


def test_personal_info_age_under_18() -> None:
    contact = schema.Contact(
        email="young@example.com", phone="1234567890", address="123 Young St."
    )

    dob_15_years = date.today().replace(year=date.today().year - 15)

    try:
        personal_info = schema.PersonalInfo(
            full_name="Young Recruit",
            date_of_birth=dob_15_years,
            nationality="British",
            contact=contact,
        )
    except ValueError as e:
        assert "Age must be at least 18" in str(e)
    else:
        pytest.fail("Expected ValueError for underage applicant, but none was raised.")
