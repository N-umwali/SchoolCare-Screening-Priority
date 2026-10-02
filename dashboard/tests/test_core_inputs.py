"""Checks for questionnaire answers and class CSV preparation."""

from io import StringIO
import unittest

import pandas as pd

from core.answer_codes import answer_to_code
from core.preprocessor import InputValidationError, Preprocessor
from core.questions import APPROVED_COLUMNS, QUESTIONS


def example_answers():
    """One valid answer for every approved question."""
    answers = {
        column: next(iter(item["options"]))
        for column, item in QUESTIONS.items()
    }
    answers["Age"] = 16
    return answers


class AnswerCodeTests(unittest.TestCase):
    def test_numeric_and_written_answers_match(self):
        for answer in ("Often", "often", "4", "4.0", 4.0):
            self.assertEqual(answer_to_code("FSS_1", answer), 4)

    def test_codebook_alias(self):
        self.assertEqual(answer_to_code("MSPSS_3", "Strong agree"), 6)
        self.assertEqual(answer_to_code("MSPSS_3", "Strongly agree"), 6)

    def test_none_is_a_valid_parent_answer(self):
        self.assertEqual(answer_to_code("Parents_Dead", "None"), 4)

    def test_blank_answer_stays_missing(self):
        self.assertIsNone(answer_to_code("Parents_Dead", ""))

    def test_invalid_age_is_rejected(self):
        with self.assertRaises(ValueError):
            answer_to_code("Age", 22)


class PreprocessorTests(unittest.TestCase):
    def test_one_student_has_only_approved_inputs(self):
        inputs = Preprocessor.prepare_student(example_answers())

        self.assertEqual(inputs.shape, (1, 34))
        self.assertEqual(inputs.columns.tolist(), APPROVED_COLUMNS)
        self.assertNotIn("student_id", inputs.columns)

    def test_all_skipped_answers_are_rejected(self):
        with self.assertRaises(ValueError):
            Preprocessor.prepare_student({
                column: None for column in APPROVED_COLUMNS
            })

    def test_readable_csv_headers_and_none_answer(self):
        row = {
            "Student ID": "S001",
            **{
                item["header"]: code
                for column, item in QUESTIONS.items()
                for code in [example_answers()[column]]
            },
        }
        row[QUESTIONS["Parents_Dead"]["header"]] = "None"
        row[QUESTIONS["FSS_1"]["header"]] = "often"

        csv_text = pd.DataFrame([row]).to_csv(index=False)
        data = Preprocessor.read_csv(StringIO(csv_text))
        ids, inputs = Preprocessor.prepare_class(data)

        self.assertEqual(ids.tolist(), ["S001"])
        self.assertEqual(inputs.loc[0, "Parents_Dead"], 4)
        self.assertEqual(inputs.loc[0, "FSS_1"], 4)
        self.assertEqual(inputs.columns.tolist(), APPROVED_COLUMNS)

    def test_repeated_ids_are_reported(self):
        answers = example_answers()
        data = pd.DataFrame([
            {"Student ID": "S001", **answers},
            {"Student ID": "S001", **answers},
        ])

        with self.assertRaises(InputValidationError) as caught:
            Preprocessor.prepare_class(data)

        self.assertIn(
            "appears more than once",
            " ".join(caught.exception.errors["Problem"]),
        )

    def test_invalid_answer_is_reported(self):
        data = pd.DataFrame([{
            "Student ID": "S002",
            **example_answers(),
            "Age": 22,
        }])

        with self.assertRaises(InputValidationError) as caught:
            Preprocessor.prepare_class(data)

        self.assertIn(
            "Age",
            caught.exception.errors["Question"].tolist(),
        )


if __name__ == "__main__":
    unittest.main()