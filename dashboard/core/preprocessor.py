"""Check student answers and prepare the approved model inputs."""

import pandas as pd

from .answer_codes import answer_to_code, convert_answers, header_to_column
from .questions import APPROVED_COLUMNS, QUESTIONS


class InputValidationError(ValueError):
    """An answer sheet contains errors that the counsellor can correct."""

    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


class Preprocessor:
    """Prepare answers without fitting or changing the saved model pipeline."""

    STUDENT_ID_COLUMN = "student_id"

    @staticmethod
    def read_csv(file):
        """Read an uploaded CSV while keeping answers and IDs as text."""
        try:
            data = pd.read_csv(
                file,
                dtype=str,
                keep_default_na=False,
                na_filter=False,
                encoding="utf-8-sig",
            )
        except (pd.errors.ParserError, UnicodeError, ValueError) as exc:
            raise ValueError(
                "The answer sheet could not be read as a CSV file."
            ) from exc

        if data.empty:
            raise ValueError("The answer sheet has no student rows.")

        return data

    @classmethod
    def _rename_columns(cls, data):
        """Accept readable headers or the exact internal question names."""
        renamed = {}
        seen = set()
        problems = []

        for header in data.columns:
            if str(header).strip().casefold() in {"student id", "student_id"}:
                column = cls.STUDENT_ID_COLUMN
            else:
                try:
                    column = header_to_column(header)
                except ValueError:
                    problems.append(f"Unrecognised column: {header!r}")
                    continue

            if column in seen:
                problems.append(f"Repeated column for: {column}")
            else:
                renamed[header] = column
                seen.add(column)

        required = {cls.STUDENT_ID_COLUMN, *APPROVED_COLUMNS}
        missing = required - seen

        if missing:
            readable = [
                "Student ID" if col == cls.STUDENT_ID_COLUMN
                else QUESTIONS[col]["header"]
                for col in [cls.STUDENT_ID_COLUMN, *APPROVED_COLUMNS]
                if col in missing
            ]
            problems.append("Missing columns: " + ", ".join(readable))

        if problems:
            raise ValueError(
                "Please correct the answer-sheet columns:\n"
                + "\n".join(problems)
            )

        return data.rename(columns=renamed)

    @classmethod
    def prepare_class(cls, data):
        """Return Student IDs and a checked, ordered 34-column input table.

        Raises InputValidationError with an errors table if any row needs
        correction. No row is scored until the whole sheet is valid.
        """
        if data.empty:
            raise ValueError("The answer sheet has no student rows.")

        data = cls._rename_columns(data)
        student_ids = data[cls.STUDENT_ID_COLUMN].astype(str).str.strip()

        errors = []
        converted_rows = []
        repeated_ids = student_ids.duplicated(keep=False)

        for position, (_, row) in enumerate(data.iterrows()):
            sheet_row = position + 2  # Row 1 contains the CSV headers.
            student_id = student_ids.iloc[position]
            converted = {}
            answered = 0

            if not student_id:
                errors.append({
                    "CSV row": sheet_row,
                    "Student ID": "",
                    "Question": "Student ID",
                    "Problem": "Enter a Student ID.",
                })
            elif repeated_ids.iloc[position]:
                errors.append({
                    "CSV row": sheet_row,
                    "Student ID": student_id,
                    "Question": "Student ID",
                    "Problem": "This Student ID appears more than once.",
                })

            for column in APPROVED_COLUMNS:
                value = row[column]

                try:
                    code = answer_to_code(column, value)
                    converted[column] = code
                    if code is not None:
                        answered += 1
                except ValueError:
                    errors.append({
                        "CSV row": sheet_row,
                        "Student ID": student_id,
                        "Question": QUESTIONS[column]["header"],
                        "Problem": f"Check the answer {value!r}.",
                    })

            if answered == 0:
                errors.append({
                    "CSV row": sheet_row,
                    "Student ID": student_id,
                    "Question": "All questions",
                    "Problem": "Enter at least one answer for this student.",
                })

            converted_rows.append(converted)

        if errors:
            raise InputValidationError(
                "Some answers need correction before ranking the class.",
                pd.DataFrame(errors),
            )

        # Student IDs remain separate: the model receives only 34 inputs.
        inputs = pd.DataFrame(converted_rows, columns=APPROVED_COLUMNS)
        return student_ids.reset_index(drop=True), inputs

    @staticmethod
    def prepare_student(answers):
        """Prepare one student's form answers for scoring."""
        converted = convert_answers(answers)

        if all(value is None for value in converted.values()):
            raise ValueError(
                "Enter at least one answer before showing a review result."
            )

        return pd.DataFrame([converted], columns=APPROVED_COLUMNS)
    