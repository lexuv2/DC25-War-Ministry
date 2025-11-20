from typing import List, Optional, Literal
from datetime import date
from pydantic import BaseModel, EmailStr, model_validator
from datetime import date


class Contact(BaseModel):
    email: EmailStr
    phone: str
    address: Optional[str] = None


class PersonalInfo(BaseModel):
    full_name: str
    date_of_birth: date
    nationality: str
    contact: Contact

    @property
    def age(self) -> int:
        today = date.today()

        age = today.year - self.date_of_birth.year

        has_had_birthday = (today.month, today.day) >= (
            self.date_of_birth.month,
            self.date_of_birth.day,
        )
        if not has_had_birthday:
            age -= 1

        return age

    @model_validator(mode="after")
    def check_age(self) -> "PersonalInfo":
        if self.age < 18:
            raise ValueError("Age must be at least 18")
        return self


class Education(BaseModel):
    degree: str
    institution: str
    start_date: date
    end_date: Optional[date] = None
    field_of_study: str


class WorkExperience(BaseModel):
    job_title: str
    company: str
    start_date: date
    end_date: Optional[date] = None


class Certification(BaseModel):
    name: str
    issuing_organization: str


class Language(BaseModel):
    language: str
    proficiency: Literal["basic", "conversational", "fluent", "native"]


class MilitaryExperience(BaseModel):
    rank: str
    branch: str
    start_date: date
    end_date: Optional[date] = None
    duties: List[str]


class WajchaRequired(BaseModel):
    has_higher_education: bool = False
    ten_years_experience: bool = False
    no_asking: bool = False
    color_knowledge: bool = False


class WajchaOptional(BaseModel):
    high_soft_skills: bool = False
    dead_lift_150kg: bool = False
    forklift: bool = False
    coffee_making: bool = False


class WajchaKeywords(BaseModel):
    required: WajchaRequired
    optional: WajchaOptional


class ZmecholRequired(BaseModel):
    north_south_east_west: bool = False
    fast_run: bool = False
    push_ups: bool = False
    kindergarten_graduate: bool = False


class ZmecholOptional(BaseModel):
    driving_licence: bool = False
    reading: bool = False
    unpunishability: bool = False
    grade_school_graduate: bool = False
    multiplication_table_knowledge: bool = False


class ZmecholKeywords(BaseModel):
    required: ZmecholRequired
    optional: ZmecholOptional


class Keywords(BaseModel):
    wajcha_keywords: WajchaKeywords
    zmechol_keywords: ZmecholKeywords


class CVParserSchema(BaseModel):
    personal_info: PersonalInfo
    overview: str
    education: List[Education]
    work_experience: List[WorkExperience]
    skills: List[str]
    certifications: Optional[List[Certification]] = None
    languages: List[Language]
    military_experience: Optional[List[MilitaryExperience]] = None
    keywords: Keywords
