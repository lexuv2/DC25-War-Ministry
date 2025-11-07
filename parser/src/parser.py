import spacy
from datetime import date
from typing import Optional, Any, List
import re
import unicodedata
from src import schema
import fitz
import os


class Parser:
    def __init__(self) -> None:
        self.nlp = spacy.load("pl_core_news_sm")

    def _normalize_whitespace(self, text: str) -> str:
        """
        Strip leading and trailing whitespace from the text,
        and replace sequences of spaces or tabs with a single space.
        """
        text = re.sub(r"[ \t]+", " ", text)
        text = "\n".join(line.strip() for line in text.splitlines())
        return text.strip()

    def _remove_unwanted_unicode(self, text: str) -> str:
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

    def create_mock(self) -> schema.CVParserSchema:

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

    def _extract_email(self, text: str) -> Optional[str]:
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

        emails = email_pattern.findall(text)
        occurences = list(set(emails))
        print(f"Found emails: {emails}")
        if len(occurences) > 0:
            return str(occurences[0])

        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        phone_pattern = re.compile(
            r"(?:(?:\+\d{1,3}\s*)?(?:\(?\d{2,4}\)?[\s.-]*)?\d{3}[\s.-]*\d{3,4}[\s.-]*\d{3,4})"
        )
        phones = phone_pattern.findall(text)
        occurences = list(set(phones))
        print(f"Found phones: {phones}")
        if len(occurences) > 0:
            return str(occurences[0])

        return None

    def _extract_name(self, text: str) -> Optional[str]:
        parsed_entities = self.nlp(text)
        names = []

        for ent in parsed_entities.ents:
            if ent.label_ == "persName":
                names.append(ent.text)
        print(f"Found names: {names}")
        if len(names) > 0:
            return str(names[0])
        return None

    def _apply_extractors(
        self, cv: Any, text: str, extractors: list[tuple[Any, str]]
    ) -> None:
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

    def parse_file(
        self, input: str, enable_log: bool = False, log_output: str = ""
    ) -> schema.CVParserSchema:

        file_basename = os.path.basename(input)

        doc = fitz.open(input)
        cv = self.create_mock()

        extractors = [
            (self._extract_email, "personal_info.contact.email"),
            (self._extract_phone, "personal_info.contact.phone"),
            (self._extract_name, "personal_info.full_name"),
        ]

        log_content = []

        for i, page in enumerate(doc, start=1):

            content = page.get_text(sort=True)
            normalized = self._normalize_whitespace(content)
            normalized = self._remove_unwanted_unicode(normalized)
            log_content.append(normalized)
            self._apply_extractors(cv, normalized, extractors)

        if enable_log:
            with open(
                os.path.join(log_output, f"raw-{file_basename}.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                for content in log_content:
                    f.write(content)

        return cv
