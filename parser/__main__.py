#!/usr/bin/env python3
import sys


def check_if_in_env() -> None:
    if sys.prefix == sys.base_prefix:
        print("❌ Please activate your virtual environment first!")
        print("   (e.g., 'source venv/bin/activate' or 'venv\\Scripts\\activate')")
        sys.exit(1)


check_if_in_env()

import fitz
import argparse
from src import schema
import json
from datetime import date
from typing import Optional, Any, List
import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """
    Strip leading and trailing whitespace from the text,
    and replace sequences of spaces or tabs with a single space.
    """
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()


def remove_unwanted_unicode(text: str) -> str:
    """
    Keep only ASCII, common Latin letters with diacritics,
    and punctuation/symbols useful in text.
    Removes control characters and emoji-like symbols.
    """
    cleaned = []
    for ch in text:
        # Remove control characters
        if ord(ch) < 32 and ch not in ("\n", "\t"):
            continue
        # Allow ASCII
        if ord(ch) < 128:
            cleaned.append(ch)
            continue
        # Allow Latin letters with accents (e.g., Polish, Czech, etc.)
        cat = unicodedata.name(ch, "")
        if "LATIN" in cat or "WITH" in cat:
            cleaned.append(ch)
            continue
        # Allow common punctuation/symbols like bullets, dashes, ©, etc.
        if ch in "•–—…«»©®°":
            cleaned.append(ch)
            continue
        # Otherwise skip (emoji, CJK, etc.)
    return "".join(cleaned)


def create_mock() -> schema.CVParserSchema:

    contact = schema.Contact(
        email="undefined@undefined.com",
        phone="+48 123458021",
        address="UNDEFINED",
    )

    personal_info = schema.PersonalInfo(
        full_name="UNDEFINED",
        date_of_birth=date(1901, 1, 1),
        nationality="UNDEFINED",
        contact=contact,
    )

    return schema.CVParserSchema(
        personal_info=personal_info,
        education=[],
        work_experience=[],
        skills=[],
        certifications=[],
        languages=[],
        military_experience=[],
    )


def extract_email(text: str) -> Optional[str]:
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    emails = email_pattern.findall(text)
    occurences = list(set(emails))

    if len(occurences) > 0:
        return str(occurences[0])

    return None


def extract_phone(text: str) -> Optional[str]:
    phone_pattern = re.compile(
        r"(?:(?:\+\d{1,3}\s*)?(?:\(?\d{2,4}\)?[\s.-]*)?\d{3}[\s.-]*\d{3,4}[\s.-]*\d{3,4})"
    )
    phones = phone_pattern.findall(text)
    occurences = list(set(phones))

    if len(occurences) > 0:
        return str(occurences[0])

    return None


def apply_extractors(cv: Any, text: str, extractors: list[tuple[Any, str]]) -> None:
    """
    Runs a list of (extractor_function, attribute_path) tuples
    and assigns results to attributes on the cv object.
    """
    for extractor_fn, attr_path in extractors:
        value = extractor_fn(text)
        if not value:
            continue
        # navigate nested attributes using dotted path, e.g. "personal_info.contact.email"
        parts = attr_path.split(".")
        target = cv
        for part in parts[:-1]:
            target = getattr(target, part)
        setattr(target, parts[-1], value)


def parse_file(input: str, output: str) -> None:
    doc = fitz.open(input)
    cv = create_mock()

    extractors = [
        (extract_email, "personal_info.contact.email"),
        (extract_phone, "personal_info.contact.phone"),
    ]

    with open(f"{output}.txt", "w", encoding="utf-8") as f:
        for i, page in enumerate(doc, start=1):

            content = page.get_text(sort=True)
            normalized = normalize_whitespace(content)
            normalized = remove_unwanted_unicode(normalized)

            apply_extractors(cv, normalized, extractors)

            f.write(normalized)

    with open(output, "w", encoding="utf-8") as f:
        f.write(cv.model_dump_json(indent=2))


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
        mock = create_mock()
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(mock.model_dump_json(indent=2))
        return

    parse_file(args.input, args.output)


if __name__ == "__main__":
    main()
