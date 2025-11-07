import json
import pytest
from pathlib import Path
from src.parser import Parser

# Paths
BASE_DIR = Path(__file__).parent
PDF_DIR = (BASE_DIR / "../../../data").resolve()
EXPECTED_PATH = BASE_DIR / "expected_results.json"

with open(EXPECTED_PATH, "r", encoding="utf-8") as f:
    EXPECTED = json.load(f)

all_pdfs = {pdf.name: pdf for pdf in PDF_DIR.glob("*.pdf")}

test_pdfs = {name: path for name, path in all_pdfs.items() if name in EXPECTED}


@pytest.mark.parametrize(
    "pdf_name, pdf_path", list(test_pdfs.items()), ids=list(test_pdfs.keys())
)
def test_parser_results(pdf_name, pdf_path):
    parser = Parser()
    cv = parser.parse_file(pdf_path)
    expected_data = EXPECTED[pdf_name]

    result_dict = cv.model_dump(mode="json")

    print("RESULT DICT")
    print(json.dumps(result_dict, indent=2, ensure_ascii=False))
    print("EXPECTED DICT")
    print(json.dumps(expected_data, indent=2, ensure_ascii=False))
    assert_dict_recursive(result_dict, expected_data, path=pdf_name)


def assert_dict_recursive(actual: dict, expected: dict, path="root"):
    for key, expected_value in expected.items():
        assert key in actual, f"Missing key '{path}.{key}'"

        actual_value = actual[key]

        if isinstance(expected_value, dict):
            assert isinstance(
                actual_value, dict
            ), f"Expected dict at '{path}.{key}', got {type(actual_value)}"
            assert_dict_recursive(actual_value, expected_value, path=f"{path}.{key}")
        elif isinstance(expected_value, list):
            assert isinstance(
                actual_value, list
            ), f"Expected list at '{path}.{key}', got {type(actual_value)}"
            assert len(actual_value) == len(
                expected_value
            ), f"List length mismatch at '{path}.{key}'"
        else:
            assert (
                actual_value == expected_value
            ), f"Value mismatch at '{path}.{key}': expected {expected_value!r}, got {actual_value!r}"
