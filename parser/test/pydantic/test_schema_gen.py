import pytest
from datetime import date
from src import schema
import json


def test_cvparser_schema_generation() -> None:

    json_schema = schema.CVParserSchema.model_json_schema()
    print(json.dumps(json_schema, indent=2))

    assert "properties" in json_schema
    assert "personal_info" in json_schema["properties"]
    assert "education" in json_schema["properties"]
    assert "work_experience" in json_schema["properties"]
    assert "skills" in json_schema["properties"]

    personal_info_props = json_schema["$defs"]["PersonalInfo"]["properties"]
    print(personal_info_props)
    assert "full_name" in personal_info_props
    assert "date_of_birth" in personal_info_props
    assert "contact" in personal_info_props
