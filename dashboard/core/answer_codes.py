"""Convert readable answers and CSV headers to the model's survey codes."""

from decimal import Decimal, InvalidOperation
import math

from .questions import APPROVED_COLUMNS, QUESTIONS, SKIPPED_LABEL


def _normalise_text(value):
    """Ignore differences in capital letters and extra spaces."""
    return " ".join(str(value).split()).casefold()


def _is_blank(value):
    """Recognise an unanswered cell without treating 'None' as blank."""
    if value is None:
        return True

    if isinstance(value, float) and math.isnan(value):
        return True

    if isinstance(value, str):
        return _normalise_text(value) in {
            "",
            "skipped",
            "no answer / unknown",
        }

    return False


def answer_to_code(column, value):
    """Convert one answer to its valid code, or return None if skipped.

    Accepts the answer label, an integer code, or a whole-number code
    written as text or a decimal, such as '4', '4.0', or 4.0.
    """
    if column not in QUESTIONS:
        raise ValueError(f"Unknown question column: {column}")

    if _is_blank(value):
        return None

    options = QUESTIONS[column]["options"]

    # A numeric answer must be a whole number and a valid option.
    # Reject booleans: Python otherwise treats True as the number 1.
    if not isinstance(value, bool):
        try:
            number = Decimal(str(value).strip())
            if number.is_finite() and number == number.to_integral_value():
                code = int(number)
                if code in options:
                    return code
        except (InvalidOperation, ValueError):
            pass

    # Match the displayed wording and any codebook aliases.
    answer = _normalise_text(value)

    for code, label in options.items():
        if answer == _normalise_text(label):
            return code

    for code, aliases in QUESTIONS[column].get("aliases", {}).items():
        if any(answer == _normalise_text(alias) for alias in aliases):
            return code

    raise ValueError(
        f"Invalid answer for '{QUESTIONS[column]['header']}': {value!r}"
    )


def code_to_answer(column, code):
    """Return readable wording for an answer review or questionnaire."""
    valid_code = answer_to_code(column, code)

    if valid_code is None:
        return SKIPPED_LABEL

    return QUESTIONS[column]["options"][valid_code]


def header_to_column(header):
    """Accept either a readable CSV header or the model's column name."""
    header_text = _normalise_text(header)

    for column, item in QUESTIONS.items():
        if header_text in {
            _normalise_text(column),
            _normalise_text(item["header"]),
        }:
            return column

    raise ValueError(f"Unrecognised answer-sheet column: {header!r}")


def convert_answers(answers):
    """Convert one student's complete set of 34 fields in model order.

    Skipped answers stay missing. The saved pipeline will fill them later.
    """
    expected = set(APPROVED_COLUMNS)
    received = set(answers)

    missing_columns = expected - received
    extra_columns = received - expected

    if missing_columns or extra_columns:
        raise ValueError(
            f"Missing columns: {sorted(missing_columns)}; "
            f"unexpected columns: {sorted(extra_columns)}"
        )

    return {
        column: answer_to_code(column, answers[column])
        for column in APPROVED_COLUMNS
    }
