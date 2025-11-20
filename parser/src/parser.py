import spacy
from datetime import date
from typing import Optional, Any, List, Tuple
import re
import unicodedata
from src import schema
import fitz
import os
from pyparsing import Word, OneOrMore, SkipTo, Combine, pyparsing_unicode as ppu
import calendar

class Parser:
    def __init__(self) -> None:
        self.nlp = spacy.load("pl_core_news_lg")
        self.base_alphas = ppu.Latin1.alphas + ppu.LatinA.alphas + ppu.LatinB.alphas
        self.name_alphas = self.base_alphas + "-"
        self.alphanum_alphas = self.base_alphas + ppu.Latin1.nums + ppu.LatinA.nums + ppu.LatinB.nums

    def _preprocess_docx(self, loc: str) -> str:
        """
        Remove mc:Fallback elements from document.xml inside a DOCX file
        """
        import zipfile
        with zipfile.ZipFile(loc, 'r') as docx:
            xml_content = docx.read('word/document.xml').decode('utf-8')
            # Remove mc:Fallback elements
            cleaned_xml = re.sub(r'<mc:Fallback>.*?</mc:Fallback>', '', xml_content, flags=re.DOTALL)
            # Write back the cleaned XML to a new DOCX file
            temp_loc = loc + '_cleaned.docx'
            with zipfile.ZipFile(temp_loc, 'w') as cleaned_docx:
                for item in docx.infolist():
                    if item.filename == 'word/document.xml':
                        cleaned_docx.writestr(item, cleaned_xml)
                    else:
                        cleaned_docx.writestr(item, docx.read(item.filename))
        return temp_loc

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
        years = re.findall(r"(19\d\d|20\d\d|2100)", text)
        return [int(year) for year in years]

    def _parse_month_years_in_text(self, text: str) -> List[Tuple[int, Optional[int]]]:
        months_map = {
            # Polish full forms and common abbreviations/stems
            "styczeń": 1, "stycznia": 1, "sty": 1, "styc": 1,
            "luty": 2, "lutego": 2, "lut": 2,
            "marzec": 3, "marca": 3, "mar": 3,
            "kwiecień": 4, "kwietnia": 4, "kwi": 4,
            "maj": 5,
            "czerwiec": 6, "czerwca": 6, "cze": 6, "czerw": 6,
            "lipiec": 7, "lipca": 7, "lip": 7,
            "sierpień": 8, "sierpnia": 8, "sie": 8, "sierp": 8,
            "wrzesień": 9, "września": 9, "wrz": 9, "wrzes": 9,
            "październik": 10, "października": 10, "paź": 10, "paz": 10,
            "listopad": 11, "listopada": 11, "lis": 11,
            "grudzień": 12, "grudnia": 12, "gru": 12,
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
    
    def _experience_str_extraction(self, text: str) -> str:
        # find line starting with experience keywords and return anything before Edukacja, Umiejętności etc.
        keywords_pattern = re.compile(r"(?:\n(Moje )?)\b(do(ś|s)wia(t|d)czenie):?\b", re.IGNORECASE)
        for match in keywords_pattern.finditer(text):
            start_idx = match.end()
            text_after = text[start_idx:]
            # cut off at next section heading if any
            section_headings = [
                "edukacja",
                "education",
                "nauczanie",
                "wykształcenie",
                "kluczowe umiejętności",
                "umiejętności",
                "umiejetnosci",
                "certyfikat",
                "certyfikaty",
                "języki",
                "jezyki",
                "doświadczenie wojskowe",
                "doswiadczenie wojskowe",
            ]
            section_pattern = re.compile(r"(?mi)^(?:" + "|".join(section_headings) + r")[:\-\s \wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]*$", re.IGNORECASE)
            sec_match = section_pattern.search(text_after)
            if sec_match:
                end_idx = sec_match.start()
                return text_after[:end_idx].strip()
            else:
                return text_after.strip()
            
    def _education_str_extraction(self, text: str) -> str:
        keywords_pattern = re.compile(r"(?:\n(Moj(?:e|a) )?)\b(edukacja|nauczanie|education|wykształcenie):?\b", re.IGNORECASE)
        for match in keywords_pattern.finditer(text):
            start_idx = match.end()
            text_after = text[start_idx:]
            # cut off at next section heading if any
            section_headings = [
                "wykształcenie",
                "kluczowe umiejętności",
                "umiejętności",
                "umiejetnosci",
                "certyfikat",
                "certyfikaty",
                "języki",
                "jezyki",
                "doświadczenie",
                "doswiadczenie",
            ]
            section_pattern = re.compile(r"(?mi)^(?:" + "|".join(section_headings) + r")[:\-\s \wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]*$", re.IGNORECASE)
            sec_match = section_pattern.search(text_after)
            if sec_match:
                end_idx = sec_match.start()
                return text_after[:end_idx].strip()
            else:
                return text_after.strip()
            
    def _calculate_years_from_txt(self, text: str) -> int:
        years = sorted(self._return_years_in_text(text))
        first_year = years[0] if years else None
        if first_year is None:
            return 0
        last_year = years[-1] if years else None
        if last_year is None:
            return 0
        
        # try to find if currently working
        now_keywords = ["teraz", "obecnie", "aktualnie", "dziś", "dzis"]
        now_pattern = re.compile(r"(" + "|".join(now_keywords) + r")", re.IGNORECASE)
        if now_pattern.search(text):
            last_year = date.today().year
        total_years = last_year - first_year + 1

        return total_years
    
    def _calculate_dead_lift_from_txt(self, text: str) -> bool:
        # find martwy ciąg and numbers
        dead_lift_pattern = re.compile(r"(\d+)(?: ?kg (?:w )?martwym? ci(?:ą|a)gu?)", re.IGNORECASE)
        match = dead_lift_pattern.search(text)
        if match:
            weight = int(match.group(1))
            return weight >= 150
        return False

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
                print(section)

            return valid_sections[0]

        return None


    def _extract_education(self, text: str) -> Optional[List[schema.Education]]:
        edu_text = self._education_str_extraction(text)
        if not edu_text:
            return None
        print(f"Extracted education section text:\n{edu_text}")

        # use NLP
        doc = self.nlp(" ".join([x.strip() for x in edu_text.split("\n")]))

        # start positions of every found entity
        entity_positions = [(ent.start_char, ent.end_char, ent.label_, ent.text) for ent in doc.ents]

        # find degrees in text and add to entity positions
        degree_pattern = re.compile(r"\b(magister|licencjat|in[żz]ynier|mgr|lic\.|bachelor|master)\b", re.IGNORECASE)
        degrees_found = degree_pattern.findall(edu_text)
        for match in degree_pattern.finditer(edu_text):
            start, end = match.span()
            degree = match.group(1).capitalize()
            entity_positions.append((start, end, "degree", degree))

        # find years or "current"-type text in text and add to entity positions
        year_pattern = re.compile(r"\b(19\d\d|20\d\d|2100|obecnie|aktualnie|do dziś|do dzisiaj|do teraz|present|current)\b", re.IGNORECASE)
        for match in year_pattern.finditer(edu_text):
            start, end = match.span()
            year_text = match.group(1)
            entity_positions.append((start, end, "year", year_text))
        entity_positions.sort(key=lambda x: x[0])  # sort by start position

        # find non-standard institution names and add to entity positions
        institution_pattern = re.compile(r"(([a-zA-ZąęółśżźćńĄĘÓŁŚŻŹĆŃ]+)(szko\w*|szkoła|gimnazjum|liceum|technikum|politechnika|uniwersytet|akademia|kolegium)( w [a-zA-ZąęółśżźćńĄĘÓŁŚŻŹĆŃ]+)?)[^\n,\.;]*", re.IGNORECASE)
        for match in institution_pattern.finditer(edu_text):
            start, end = match.span()
            institution = match.group(0).strip()
            entity_positions.append((start, end, "orgName", institution))
        entity_positions.sort(key=lambda x: x[0])  # sort by start position

        # find month names before years and add to entity positions
        month_names_pattern = r"\b(styczen|stycznia|styc|sty|luty|lutego|lut|marzec|marca|mar|kwiecien|kwietnia|kwi|kwiecie[nń]|maj|czerwiec|czerwca|cze|czerw|lipiec|lipca|lip|sierpien|sierpnia|sierp|sie|wrzesie[nń]|wrzesnia|wrz|wrzes|pa[zź]dziernik|pa[zź]dziernika|pa[zź]|paz|listopad|listopada|lis|grudzie[nń]|grudnia|gru)\b"
        for match in re.finditer(month_names_pattern, edu_text, re.IGNORECASE):
            start, end = match.span()
            month_text = match.group(0)
            # merge with adjacent year existing in entity_positions if any
            merged = False
            for i, (e_start, e_end, e_label, e_text) in enumerate(entity_positions):
                if e_label == "year" or e_label == "date" and abs(e_start - end) <= 3:
                    new_start = start
                    new_end = e_end
                    new_text = edu_text[new_start:new_end]
                    entity_positions[i] = (new_start, new_end, "date", new_text)
                    merged = True
                    break
                elif e_label == "year" or e_label == "date" and abs(start - e_end) <= 3:
                    new_start = e_start
                    new_end = end
                    new_text = edu_text[new_start:new_end]
                    entity_positions[i] = (new_start, new_end, "date", new_text)
                    merged = True
                    break
            if not merged:
                entity_positions.append((start, end, "date", month_text))

        # remove trailing years from orgName entities
        adjusted_entities = []
        for start, end, label, text in entity_positions:
            if label == "orgName":
                year_match = year_pattern.search(text)
                if year_match:
                    year_start = start + year_match.start()
                    adjusted_entities.append((start, year_start, label, text[:year_match.start()].strip()))
                    continue
            adjusted_entities.append((start, end, label, text))

        entity_positions = adjusted_entities

        # if orgName doesn't contain an edu institution keyword, count it as a field_of_study
        final_entities = []
        edu_institution_keywords = [
            "szkoła", "szkola", "gimnazjum", "liceum", "technikum",
            "politechnika", "uniwersytet", "akademia", "kolegium",
            "wyższa", "wyzsza", "uczelnia", "studia", "college", "university",
            "institute", "school", "faculty", "department", "żłobek", "przedszkole",
            "wydział", "katedra"
        ]
        for start, end, label, text in entity_positions:
            if label == "orgName":
                if not any(kw in text.lower() for kw in edu_institution_keywords):
                    final_entities.append((start, end, "field_of_study", text))
                else:
                    final_entities.append((start, end, label, text))
            else:
                final_entities.append((start, end, label, text))
        entity_positions = final_entities

        # in edu_text if has "kierunek" or "zawód" count as field_of_study and add to entity positions
        field_of_study_pattern = re.compile(r"(kierunek|zawód|zawod)(?::)?\s+([A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż \-:]+)", re.IGNORECASE)
        for match in field_of_study_pattern.finditer(edu_text):
            start, end = match.span()
            field_of_study = match.group(0).strip()
            entity_positions.append((start, end, "field_of_study", field_of_study))

        # in edu_text if between degree and institution name is anything, count as field_of_study and add to entity positions
        degree_institution_pattern = re.compile(
            r"(?P<degree>\b(magister|licencjat|in[żz]ynier|mgr|lic\.|bachelor|master)\b(?:,( )?)?)(?P<between>.*?)(?:,|\.|\n|;|$| )+(?P<institution>(?:szko\w*|szkoła|gimnazjum|liceum|technikum|politechnika|uniwersytet|akademia|kolegium)[^\n,\.;]*)",
            re.IGNORECASE | re.DOTALL
        )
        for match in degree_institution_pattern.finditer(edu_text):
            between_text = match.group("between").strip()
            if between_text:
                start = match.start("between")
                end = match.end("between")
                field_of_study = between_text
                entity_positions.append((start, end, "field_of_study", field_of_study))
        entity_positions.sort(key=lambda x: x[0])  # sort by start position

        # field_of_study also after a colon after school name
        institution_field_pattern = re.compile(
            r"(?P<institution>(?:szko\w*|szkoła|gimnazjum|liceum|technikum|politechnika|uniwersytet|akademia|kolegium)[^\n,\.;]*):\s*(?P<field_of_study>[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż\s\-:]+)",
            re.IGNORECASE | re.DOTALL
        )
        for match in institution_field_pattern.finditer(edu_text):
            field_of_study = match.group("field_of_study").strip()
            start = match.start("field_of_study")
            end = match.end("field_of_study")
            entity_positions.append((start, end, "field_of_study", field_of_study))
        entity_positions.sort(key=lambda x: x[0])  # sort by start position

        # field_of_study after degree, before endline or month name or year
        degree_field_pattern = re.compile(
            r"(?P<degree>\b(magister|licencjat|in[żz]ynier|mgr|lic\.|bachelor|master)\b(?:,( )?)?)(?P<field_of_study>[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż \-:]+?)(?=\n|$|\b(styczen|stycznia|styc|sty|luty|lutego|lut|marzec|marca|mar|kwiecien|kwietnia|kwi|kwiecie[nń]|maj|czerwiec|czerwca|cze|czerw|lipiec|lipca|lip|sierpien|sierpnia|sierp|sie|wrzesie[nń]|wrzesnia|wrz|wrzes|pa[zź]dziernik|pa[zź]dziernika|pa[zź]|paz|listopad|listopada|lis|grudzie[nń]|grudnia|gru)\b|\b(19\d\d|20\d\d|2100)\b)",
            re.IGNORECASE | re.DOTALL
        )
        for match in degree_field_pattern.finditer(edu_text):
            field_of_study = match.group("field_of_study").strip()
            start = match.start("field_of_study")
            end = match.end("field_of_study")
            entity_positions.append((start, end, "field_of_study", field_of_study))
        entity_positions.sort(key=lambda x: x[0])  # sort by start position

        # if degree or year text is part of any previous entity that is not "date", cut the previous entity to exclude degree/year
        adjusted_entities = []
        for start, end, label, text in entity_positions:
            if label in ("degree", "year", "field_of_study"):
                # check if it overlaps with any existing entity that is not "date"
                overlaps = [e for e in adjusted_entities if not (end <= e[0] or start >= e[1]) and e[2] != "date"]
                for o_start, o_end, o_label, o_text in overlaps:
                    # adjust the overlapping entity to exclude degree/year
                    if start > o_start:
                        adjusted_entities.append((o_start, start, o_label, o_text[:start - o_start].strip()))
                    if end < o_end:
                        adjusted_entities.append((end, o_end, o_label, o_text[end - o_start:].strip()))
                    adjusted_entities.remove((o_start, o_end, o_label, o_text))
            adjusted_entities.append((start, end, label, text))

        # remove duplicate adjacent date/year entries
        adjusted_entities.sort(key=lambda x: x[0])  # sort by start position
        deduped_entities = []
        prev_start, prev_end, prev_label, prev_text = None, None, None, None
        for start, end, label, text in adjusted_entities:
            if (start, end, text) != (prev_start, prev_end, prev_text):
                deduped_entities.append((start, end, label, text))
                prev_start, prev_end, prev_label, prev_text = start, end, label, text
        adjusted_entities = deduped_entities

        entity_positions = adjusted_entities

        # merge adjacent entities of the same label, together with text between it (get it from original text for speed)
        merged_entities = []
        i = 0
        while i < len(entity_positions):
            start, end, label, text = entity_positions[i]
            j = i + 1
            while j < len(entity_positions):
                next_start, next_end, next_label, next_text = entity_positions[j]
                # check if adjacent or only whitespace between
                if (next_label == label and label == "orgName") or (label == "orgName" and next_label == "placeName") or (label == "placeName" and next_label == "orgName"):
                    # merge
                    end = next_end
                    text = edu_text[start:end]
                    j += 1
                else:
                    break
            merged_entities.append((start, end, label, text.strip()))
            i = j
        entity_positions = merged_entities

        # remove overlapping entities, keep the longest match
        non_overlapping = []
        for start, end, label, text in entity_positions:
            overlap = False
            for o_start, o_end, o_label, o_text in non_overlapping:
                if not (end <= o_start or start >= o_end):
                    # overlapping
                    overlap = True
                    # keep the longer one
                    if (end - start) > (o_end - o_start):
                        non_overlapping.remove((o_start, o_end, o_label, o_text))
                        non_overlapping.append((start, end, label, text))
                    break
            if not overlap:
                non_overlapping.append((start, end, label, text))
        entity_positions = non_overlapping

        # if orgName contains " w ", split string after " w ", and then split it after a city name
        # risky approach as we assume one-word city names
        adjusted_entities = []
        for start, end, label, text in entity_positions:
            if label == "orgName" and " w " in text:
                parts = text.split(" w ")
                loc_part = f"{parts[0]} w {parts[1].split(" ")[0]}"
                study_part = " ".join(parts[1].strip().split(" ")[1:])
                adjusted_entities.append((start, start + len(loc_part), label, loc_part.strip()))
                if study_part.strip():
                    adjusted_entities.append((start + len(loc_part), end, "field_of_study", study_part.strip()))
            else:
                adjusted_entities.append((start, end, label, text))

        entity_positions = adjusted_entities

        print(f"Found entities in education section:")
        for start, end, label, text in entity_positions:
            print(f" - {text} ({label}) [{start}:{end}]")

        edu_list: List[schema.Education] = []
        first_element = ""
        for _, _, label, text in entity_positions:
            if label == first_element or first_element == "":
                edu_list.append(schema.Education(
                    degree="UNKNOWN",
                    institution="UNKNOWN",
                    field_of_study="UNKNOWN",
                    start_date=date(1900, 1, 1),
                    end_date=None,
                ))
            if label == "orgName":
                edu_list[-1].institution = text
            elif label == "degree":
                if edu_list[-1].degree != "UNKNOWN" and edu_list[-1].end_date is not None:
                    edu_list.append(schema.Education(
                        degree=text,
                        institution=edu_list[-1].institution,
                        field_of_study=edu_list[-1].field_of_study,
                        start_date=edu_list[-1].end_date,
                        end_date=None,
                    ))
                    edu_list[-2].end_date = None
                else:
                    edu_list[-1].degree = text
            elif label == "field_of_study":
                edu_list[-1].field_of_study = text
            elif label == "year" or label == "date":
                if first_element != "degree" and edu_list[-1].degree != "UNKNOWN" and edu_list[-1].start_date != date(1900, 1, 1) and edu_list[-1].end_date is not None:
                    edu_list.append(schema.Education(
                        degree="UNKNOWN",
                        institution=edu_list[-1].institution,
                        field_of_study=edu_list[-1].field_of_study,
                        start_date=date(1900, 1, 1),
                        end_date=None,
                    ))
                if re.search(r"(obecnie|aktualnie|do dziś|do dzisiaj|do teraz|present|current)", text, re.IGNORECASE):
                    if edu_list[-1].start_date == date(1900, 1, 1):
                        edu_list[-1].start_date = date.today()
                    else:
                        edu_list[-1].end_date = date.today()
                else:
                    m_y = self._parse_month_years_in_text(text)[0]
                    year = m_y[0]
                    month = m_y[1]
                if edu_list[-1].start_date == date(1900, 1, 1):
                    edu_list[-1].start_date = date(year, month or 1, 1)
                else:
                    edu_list[-1].end_date = date(year, month or 12, calendar.monthrange(year, month or 12)[1])

            if first_element == "":
                first_element = label
        return edu_list if edu_list else None
    
    
    def _extract_keywords(self, text: str) -> Optional[schema.Keywords]:
        # Placeholder
        # return self.create_mock().keywords

        # array with keywords together with regex patterns to search for
        keywords_patterns = {
            # Wajcha Required
            "has_higher_education": r"\b(wyższe wykształcenie|wyzsze wyksztalcenie|wykształcenie wyższe|wyksztalcenie wyzsze|studia magisterskie|studia inżynierskie|studia inzynierskie|licencjat|magister|inżynier|inzynier|mgr|lic\.|politechnika|politechniki|politechnikę|uniwersytet|akademia|kolegium)\b",
            "ten_years_experience": r"\b(10 lat doświadczenia|10 lat doswiadczenia|10-letnim doświadczeniem|10-letnie doświadczenie)\b", # additional naive year parsing -> TODO
            "no_asking": r"\b(nie pytam|nie zadaj(ę|e) pytań|nie zadaję głupich pytań|niezadawanie pytań|niezadawanie głupich pytań|bez zadawania pytań|nie zadając( zbędnych)? pytań)\b",
            "color_knowledge": r"\b(znajomość kolorów|znajomosc kolorow|rozróżnianie kolorów|rozroznianie kolorow|znam (wszystkie )?kolory|rozróżniam kolory)\b",
            # Wajcha Optional
            "high_soft_skills": r"\b(wysokie umiejętności miękkie|wysokie umiejetnosci miekkie)\b",
            "dead_lift_150kg": r"\b(martwy ciąg 150kg|martwy ciag 150kg|150kg w martwym ciągu)\b",
            "forklift": r"\b(wózek widłowy|wozek widlowy|wózku widłowym|wozku widlowym)\b",
            "coffee_making": r"\b(kawę|kawy)\b",
            # Zmechol Required
            "north_south_east_west": r"\b(rozróżnianie kierunków|rozróżniam kierunki|rozróżnianie stron świata|rozróżniam strony świata|orientacja w terenie|(dobrze )?orientuję (się )?w terenie)\b",
            "fast_run": r"\b(bieg(u)?|biegam|bieganie|biegi|biegać)\b",
            "push_ups": r"\b(pompki|push[- ]?ups?|robienie pompek|robię pompki)\b",
            "kindergarten_graduate": r"\b(przedszkole|przedszkola|przedszkolu|szkoła|szkołę|szkoły|szkole|gimnazjum|liceum|technikum|politechnika|politechniki|politechnikę|uniwersytet|akademia|kolegium)\b",
            # Zmechol Optional
            "driving_licence": r"\b(prawo jazdy|posiadacz prawa jazdy)\b",
            "reading": r"\b(czytanie|czytania|czytać|czytam)\b",
            "unpunishability": r"\b(niekaralność|niekaralnosc)\b",
            "grade_school_graduate": r"\b(szkoła|szkoły|szkole|szkołę|gimnazjum|liceum|technikum|politechnika|politechniki|politechnikę|uniwersytet|akademia|kolegium)\b",
            "multiplication_table_knowledge": r"\b(tabliczka mnożenia|tabliczka mnozenia|tabliczkę mnożenia)\b",
        }
        keywords = self.create_mock().keywords
        cleaned_text = " ".join([line.strip() for line in self._normalize_whitespace(text).split("\n")])
        for attr, pattern in keywords_patterns.items():
            if re.search(pattern, cleaned_text, re.IGNORECASE) or (attr == "ten_years_experience" and self._calculate_years_from_txt(self._experience_str_extraction(self._normalize_whitespace(text))) >= 10) or (attr == "dead_lift_150kg" and self._calculate_dead_lift_from_txt(self._normalize_whitespace(text))):
                print(f"Keyword matched: {attr}")
                for sub_attr in ['wajcha_keywords', 'zmechol_keywords']:
                    sub_obj = getattr(keywords, sub_attr)
                    for sub_sub_attr in ['required', 'optional']:
                        sub_sub_obj = getattr(sub_obj, sub_sub_attr)

                        if hasattr(sub_sub_obj, attr):
                            setattr(sub_sub_obj, attr, True)
                            break
        return keywords

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
        if str(input).lower().endswith(".docx"):
            input = self._preprocess_docx(input)

        doc = fitz.open(input)

        if str(input).lower().endswith(".docx"):
            os.remove(input)

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
