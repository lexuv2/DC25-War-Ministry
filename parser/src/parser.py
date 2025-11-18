import spacy
from datetime import date
from typing import Optional, Any, List, Tuple
import re
import unicodedata
from src import schema
import fitz
import os
from pyparsing import Word, OneOrMore, SkipTo, Combine, pyparsing_unicode as ppu


class Parser:
    def __init__(self) -> None:
        self.nlp = spacy.load("pl_core_news_sm")
        self.base_alphas = ppu.Latin1.alphas + ppu.LatinA.alphas + ppu.LatinB.alphas
        self.name_alphas = self.base_alphas + "-"
        self.alphanum_alphas = self.base_alphas + ppu.Latin1.nums + ppu.LatinA.nums + ppu.LatinB.nums

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
        return "".join(cleaned)

    def _remove_unwanted_chars_in_fullname(self, text: str) -> str:
        """
        Keep only ASCII letters, common Latin letters and spaces
        """
        cleaned = []
        for ch in text:
            # Allow ASCII letters
            if 65 <= ord(ch) <= 90 or 97 <= ord(ch) <= 122:
                cleaned.append(ch)
                continue
            # Allow some ASCII symbols
            if ch == " " or ch == "-":
                cleaned.append(ch)
                continue
            if ch == "\n" or ch == "\t":
                cleaned.append(" ")
                continue
            # Allow Latin letters with accents (e.g., Polish, Czech, etc.)
            cat = unicodedata.name(ch, "")
            if "LATIN" in cat or "WITH" in cat:
                cleaned.append(ch)
                continue
        return "".join(cleaned).strip()

    def _text_contains_a_year(self, text: str) -> bool:
        """Return True if text contains a number between 1900 and 2100."""
        return re.search(r"\b(19\d\d|20\d\d|2100)\b", text) is not None
    
    def _return_years_in_text(self, text: str) -> List[int]:
        """Return list of years (numbers between 1900 and 2100) found in text."""
        years = re.findall(r"\b(19\d\d|20\d\d|2100)\b", text)
        return [int(year) for year in years]

    def _parse_month_years_in_text(self, text: str) -> List[Tuple[int, Optional[int]]]:
        months_map = {
            # Polish full forms and common abbreviations/stems
            "styczen": 1, "stycznia": 1, "sty": 1, "styc": 1,
            "luty": 2, "lutego": 2, "lut": 2,
            "marzec": 3, "marca": 3, "mar": 3,
            "kwiecien": 4, "kwietnia": 4, "kwi": 4,
            "maj": 5,
            "czerwiec": 6, "czerwca": 6, "cze": 6, "czerw": 6,
            "lipiec": 7, "lipca": 7, "lip": 7,
            "sierpien": 8, "sierpnia": 8, "sie": 8, "sierp": 8,
            "wrzesien": 9, "wrzesnia": 9, "wrz": 9, "wrzes": 9,
            "pazdziernik": 10, "pazdziernika": 10, "październik": 10, "paź": 10, "paz": 10,
            "listopad": 11, "listopada": 11, "lis": 11,
            "grudzien": 12, "grudnia": 12, "gru": 12,
            # English months to be tolerant
            "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
            "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
            "november": 11, "december": 12,
        }

        results: List[Tuple[int, Optional[int]]] = []

        def norm(s: str) -> str:
            return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

        norm_text = norm(text)

        # month-name + year
        for m_name, m_num in months_map.items():
            pat = rf"\b{re.escape(norm(m_name))}\b\s*(19\d\d|20\d\d|2100)"
            for m in re.finditer(pat, norm_text, flags=re.IGNORECASE):
                yr = int(m.group(1))
                results.append((yr, m_num))

        # numeric month/year
        for m in re.finditer(r"(\d{1,2})[\./-](19\d\d|20\d\d|2100)", text):
            mon = int(m.group(1))
            yr = int(m.group(2))
            if 1 <= mon <= 12:
                results.append((yr, mon))

        if not results:
            for y in self._return_years_in_text(text):
                results.append((y, None))

        return results
    
    def _text_contains_edu_institution(self, text: str) -> bool:
        """Return True if text contains common education institution keywords."""
        keywords = [
            "żłobek",
            "szkoła",
            "gimnazjum",
            "liceum",
            "technikum",
            "politechnika",
            "uniwersytet",
            "akademia",
            "kolegium",
        ]
        pattern = re.compile(r"(" + "|".join(keywords) + r")", re.IGNORECASE)
        return pattern.search(text) is not None

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

        wajcha_required = schema.WajchaRequired(
            has_higher_education=False,
            ten_years_experience=False,
            no_asking=False,
            color_knowledge=False,
        )

        wajcha_optional = schema.WajchaOptional(
            high_soft_skills=False,
            dead_lift_150kg=False,
            forklift=False,
            coffee_making=False,
        )

        wajcha_keywords = schema.WajchaKeywords(
            required=wajcha_required,
            optional=wajcha_optional,
        )

        zmechol_required = schema.ZmecholRequired(
            north_south_east_west=False,
            fast_run=False,
            push_ups=False,
            kindergarten_graduate=False,
        )

        zmechol_optional = schema.ZmecholOptional(
            driving_licence=False,
            reading=False,
            unpunishability=False,
            grade_school_graduate=False,
            multiplication_table_knowledge=False,
        )

        zmechol_keywords = schema.ZmecholKeywords(
            required=zmechol_required,
            optional=zmechol_optional,
        )

        keywords = schema.Keywords(
            wajcha_keywords=wajcha_keywords,
            zmechol_keywords=zmechol_keywords,
        )


        return schema.CVParserSchema(
            personal_info=personal_info,
            overview="",
            education=[],
            work_experience=[],
            skills=[],
            certifications=[],
            languages=[],
            military_experience=[],
            keywords=keywords,
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

    def _capitilize_fullname(self, name: str) -> str:
        words = name.split(" ")
        result = []
        for word in words:
            if "-" in word:
                capitalized = [w.capitalize() for w in word.split("-")]
                result.append("-".join(capitalized))
                continue
            result.append(word.capitalize())
        return " ".join(result)

    def _extract_name(self, text: str) -> Optional[str]:
        parsed_entities = self.nlp(text)
        names = []

        for ent in parsed_entities.ents:
            if ent.label_ == "persName" and " " in ent.label_:
                normalized = self._remove_unwanted_chars_in_fullname(ent.text)
                capitilized = self._capitilize_fullname(normalized)
                names.append(capitilized)

        if len(names) > 0:
            print(f"Found names: {names}")
            return str(names[0])

        # If fails find the first two valid words
        name_word = Word(self.name_alphas)
        tokens = [t[0] for t in name_word.searchString(text)]
        first_2_words = tokens[:2]
        capitilized = self._capitilize_fullname(" ".join(first_2_words))
        names.append(capitilized)

        print(f"Found names: {names}")
        if len(names) > 0:
            return str(names[0])
        return None

    def _extract_overview(self, text: str) -> Optional[str]:
        section_body = SkipTo("\n\n", include=False)
        section_parser = Combine(section_body + "\n\n")

        results = [res[0].strip() for res, _, _ in section_parser.scanString(text)]

        base_word = Word(self.base_alphas)

        MIN_SENTECE_AMMOUNT = 2
        MIN_WORDS_IN_SENTENCE = 4
        MIN_WORD_LENGTH = 3

        valid_sections = []
        for section in results:

            # Either an Education or Experience section
            if self._text_contains_a_year(section):
                continue

            valid_sentence_count = 0
            sentences = re.split(r"[.!?]", section)

            for sentence in sentences:
                tokens = [t[0] for t in base_word.searchString(sentence)]
                filtered = [t for t in tokens if len(t) >= MIN_WORD_LENGTH]

                if len(filtered) < MIN_WORDS_IN_SENTENCE:
                    continue

                # First letter in sentence has to be capital
                if not filtered[0][0].isupper():
                    continue

                valid_sentence_count += 1

            if valid_sentence_count < MIN_SENTECE_AMMOUNT:
                continue

            # Output only words without special chars
            filtered_section = [t[0] for t in base_word.searchString(section)]
            valid_sections.append(" ".join(filtered_section))

        if len(valid_sections) > 0:
            print(f"Found about sections:")

            for section in valid_sections:
                print(valid_sections)

            return valid_sections[0]

        return None

    def _extract_education(self, text: str) -> Optional[List[schema.Education]]:
        section_body = SkipTo("\n\n", include=False)
        section_parser = Combine(section_body + "\n\n")
        blocks = [res[0].strip() for res, _, _ in section_parser.scanString(text)]

        base_word = Word(self.alphanum_alphas)
        edu_list: List[schema.Education] = []

        for b in blocks:
            if not self._text_contains_edu_institution(b):
                continue
            if not (self._text_contains_a_year(b) or re.search(r"\b(licencjat|magister|in[żz]ynier|mgr|lic\.|bachelor|master|kierunek)\b", b, re.IGNORECASE)):
                continue

            cleaned = " ".join(line.strip() for line in b.splitlines() if line.strip())
            # remove leading section headings like 'Edukacja' that may be
            # glued to the institution name in extracted text
            cleaned = re.sub(r"^(Edukacja|EDUKACJA|Education)[:\-\s]*", "", cleaned, flags=re.IGNORECASE)

            # split by visible degree markers so multiple educations become separate items
            subblocks = re.split(r"(?=(?:licencjat|magister|in[żz]ynier|mgr|lic\.|kierunek))", cleaned, flags=re.IGNORECASE)
            if len(subblocks) == 1:
                subblocks = [cleaned]

            for sb in subblocks:
                sb = sb.strip()
                if not sb:
                    continue
                months = self._parse_month_years_in_text(sb)
                years = [y for (y, m) in months]

                degree = "UNKNOWN"
                institution = "UNKNOWN"
                field_of_study = "UNKNOWN"

                # capture field of study like 'kierunek Informatyka' keeping prefix
                # accept small misspellings like 'kiernunek' by matching kierun\w*
                k = re.search(r"(kierun\w*)\s+([A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9\s\-:]+)", sb, re.IGNORECASE)
                if k:
                    field_of_study = k.group(0).strip()

                inst_match = re.search(r"([A-Za-zĄĆĘŁŃÓŚŹŻ0-9\,\.\-\s]{2,120}(?:szko\w*|szkoła|gimnazjum|liceum|technikum|politechnika|uniwersytet|akademia|kolegium)[^\n,\.;]*)", sb, re.IGNORECASE)
                if inst_match:
                    institution = inst_match.group(1).strip()
                    # strip stray year tokens, parentheses and section words
                    institution = re.sub(r"\b(19\d\d|20\d\d|2100)\b", "", institution)
                    institution = re.sub(r"\(.*?\)", "", institution)
                    institution = re.sub(r"\b(Edukacja|edukacja|kierun\w*)\b.*$", "", institution, flags=re.IGNORECASE).strip()
                    # remove trailing month words that sometimes leak into institution
                    months_pattern_short = r"\b(styczen|stycznia|styc|sty|luty|lutego|lut|marzec|marca|mar|kwiecien|kwietnia|kwi|kwiecie[nń]|maj|czerwiec|czerwca|cze|czerw|lipiec|lipca|lip|sierpien|sierpnia|sierp|sie|wrzesie[nń]|wrzesnia|wrz|wrzes|pa[zź]dziernik|pa[zź]dziernika|pa[zź]|paz|listopad|listopada|lis|grudzie[nń]|grudnia|gru)\b"
                    institution = re.sub(months_pattern_short, "", institution, flags=re.IGNORECASE).strip()
                    # remove trailing punctuation and stray separators
                    institution = re.sub(r"[\|\-\:\,;]+$", "", institution).strip()
                    # collapse multiple spaces and strip
                    institution = re.sub(r"\s+", " ", institution).strip()

                dmatch = re.search(r"\b(licencjat|magister|in[żz]ynier|mgr|lic\.|bachelor|master)\b", sb, re.IGNORECASE)
                if dmatch:
                    degree = dmatch.group(1).capitalize()

                degree_tokens = [t[0] for t in base_word.searchString(degree)]
                institution_tokens = [t[0] for t in base_word.searchString(institution)]
                degree_clean = " ".join(degree_tokens) if degree_tokens else (degree or "UNKNOWN")
                institution_clean = " ".join(institution_tokens) if institution_tokens else (institution or "UNKNOWN")

                # compute sensible start/end dates: prefer earliest year as start,
                # latest year as end. If only one year is present, set end_date to None
                # (ongoing or unspecified) to match expected outputs.
                yrs = [y for (y, m) in months]
                if yrs:
                    start_year = min(yrs)
                    end_year = max(yrs)
                    # pick month for start if available for that year
                    start_month = next((m for (y, m) in months if y == start_year and m), 1)
                    end_month = next((m for (y, m) in reversed(months) if y == end_year and m), 1)
                    start_date = date(start_year, start_month or 1, 1)
                    end_date = None if start_year == end_year else date(end_year, end_month or 1, 1)
                else:
                    # fallback to any bare years found in the block
                    ys = self._return_years_in_text(sb)
                    if ys:
                        start_year = min(ys)
                        end_year = max(ys)
                        start_date = date(start_year, 1, 1)
                        end_date = None if start_year == end_year else date(end_year, 1, 1)
                    else:
                        start_date = date(1900, 1, 1)
                        end_date = None

                # only include entries that have a plausible institution or degree
                if (institution_clean and institution_clean != "UNKNOWN") or (degree_clean and degree_clean != "UNKNOWN"):
                    edu_list.append(schema.Education(
                        degree=degree_clean or "UNKNOWN",
                        institution=institution_clean or "UNKNOWN",
                        start_date=start_date,
                        end_date=end_date,
                        field_of_study=field_of_study or "UNKNOWN",
                    ))

        # Fallback: if pyparsing blocks didn't find education entries, look for
        # explicit 'Edukacja' (or variants) headings and capture the following
        # non-empty lines until the next blank line. This handles PDFs where
        # the extractor didn't produce a contiguous block recognized above.
        if not edu_list:
            for m in re.finditer(r"(?mi)^(edukacja|wykształcenie|education)\s*$", text):
                start = m.end()
                rest = text[start:]
                end_idx = rest.find("\n\n")
                block = rest if end_idx == -1 else rest[:end_idx]
                lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
                if not lines:
                    continue
                # Expectation: first non-empty line is institution, next may be field, final may be year
                inst = lines[0]
                fld = "UNKNOWN"
                yrs = []
                for ln in lines[1:4]:
                    ymatch = re.search(r"\b(19\d\d|20\d\d|2100)\b", ln)
                    if ymatch:
                        yrs.append(int(ymatch.group(1)))
                    k = re.search(r"(kierun\w*)\s+([A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9\s\-:]+)", ln, re.IGNORECASE)
                    if k:
                        fld = k.group(0).strip()

                start_date = date(1900, 1, 1)
                end_date = None
                if yrs:
                    start_year = min(yrs)
                    start_date = date(start_year, 1, 1)
                    end_date = None if len(yrs) == 1 else date(max(yrs), 1, 1)

                # sanitize institution similar to main flow
                institution = re.sub(r"\b(19\d\d|20\d\d|2100)\b", "", inst)
                institution = re.sub(r"\(.*?\)", "", institution).strip()
                institution = re.sub(r"\b(Edukacja|edukacja|kierun\w*)\b.*$", "", institution, flags=re.IGNORECASE).strip()
                # remove trailing separators and normalize spacing (handles cases like 'Politechnika X |')
                institution = re.sub(r"[\|\-\:\,;]+$", "", institution).strip()
                institution = re.sub(r"\s+", " ", institution).strip()

                edu_list.append(schema.Education(
                    degree="UNKNOWN",
                    institution=institution or "UNKNOWN",
                    start_date=start_date,
                    end_date=end_date,
                    field_of_study=fld or "UNKNOWN",
                ))

        # Deduplicate / merge overlapping education entries by normalized institution + start_date
        if edu_list:
            def _norm_inst(s: str) -> str:
                s = s or ""
                s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
                s = re.sub(r"[^a-z0-9 ]+", " ", s)
                s = re.sub(r"\s+", " ", s).strip()
                return s

            # First pass: merge by (normalized institution, start_date) as before
            merged_map: dict = {}
            for e in edu_list:
                sdate = None if (not e.start_date or e.start_date == date(1900, 1, 1)) else e.start_date
                key = (_norm_inst(e.institution), sdate)
                if key in merged_map:
                    existing = merged_map[key]
                    # prefer non-UNKNOWN fields
                    if existing.degree in (None, "UNKNOWN") and (e.degree and e.degree != "UNKNOWN"):
                        existing.degree = e.degree
                    if existing.field_of_study in (None, "UNKNOWN") and (e.field_of_study and e.field_of_study != "UNKNOWN"):
                        existing.field_of_study = e.field_of_study
                    if existing.institution in (None, "UNKNOWN") and (e.institution and e.institution != "UNKNOWN"):
                        existing.institution = e.institution
                    if (existing.start_date is None or (e.start_date and e.start_date < existing.start_date)):
                        existing.start_date = e.start_date
                    if existing.end_date is None and e.end_date is not None:
                        existing.end_date = e.end_date
                else:
                    merged_map[key] = schema.Education(
                        degree=e.degree,
                        institution=e.institution,
                        start_date=e.start_date,
                        end_date=e.end_date,
                        field_of_study=e.field_of_study,
                    )

            # Second pass: try to absorb entries that have UNKNOWN institution but matching field_of_study
            final_map: dict = {}
            for key, e in merged_map.items():
                # use normalized institution as primary key
                inst_norm = key[0]
                if inst_norm and inst_norm != "unknown":
                    final_map[inst_norm] = e
                else:
                    # try to merge UNKNOWN institution into any existing final_map entry that
                    # shares tokens with the field_of_study or with the original institution text.
                    fld_norm = _norm_inst(e.field_of_study or "")
                    inst_text_norm = _norm_inst(e.institution or "")
                    merged_into = None
                    for exist_key, exist_val in list(final_map.items()):
                        # if field_of_study tokens overlap or institution substring match, merge
                        if fld_norm and fld_norm in exist_key:
                            merged_into = exist_key
                            break
                        if inst_text_norm and inst_text_norm and inst_text_norm in exist_key:
                            merged_into = exist_key
                            break

                    if merged_into:
                        existing = final_map[merged_into]
                        if existing.institution in (None, "UNKNOWN") and e.institution and e.institution != "UNKNOWN":
                            existing.institution = e.institution
                        if existing.degree in (None, "UNKNOWN") and e.degree and e.degree != "UNKNOWN":
                            existing.degree = e.degree
                        if existing.field_of_study in (None, "UNKNOWN") and e.field_of_study and e.field_of_study != "UNKNOWN":
                            existing.field_of_study = e.field_of_study
                    else:
                        # create a fallback key using field_of_study or a unique placeholder
                        final_key = fld_norm or inst_text_norm or f"_inst_{len(final_map)}"
                        final_map[final_key] = e

            merged = list(final_map.values())
            # Remove UNKNOWN-institution entries when a canonical non-UNKNOWN
            # entry exists for the same start_date (conservative merge)
            final_merged = []
            for e in merged:
                inst_unknown = (not e.institution) or (e.institution and e.institution.strip().upper() == "UNKNOWN")
                has_peer = any((other is not e) and (other.start_date == e.start_date) and (other.institution and other.institution.strip().upper() != "UNKNOWN") for other in merged)
                if inst_unknown and has_peer:
                    # drop this UNKNOWN institution entry as it's absorbed by peer
                    continue
                final_merged.append(e)

            return final_merged if final_merged else None

        return None
    
    def _extract_keywords(self, text: str) -> Optional[schema.Keywords]:
        # Placeholder
        return self.create_mock().keywords

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
            (self._extract_overview, "overview"),
            (self._extract_education, "education"),
            # (self._extract_work_experience, "work_experience"),
            (self._extract_keywords, "keywords"),
        ]

        content = "\n".join([page.get_text(sort=True) for _, page in enumerate(doc, start=1)])
        log_content = []
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
