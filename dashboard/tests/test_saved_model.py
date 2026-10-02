"""Check the saved model and the app's scoring wrapper."""

import unittest

import numpy as np

from core.preprocessor import Preprocessor
from core.screening_priority_model import ScreeningPriorityModel


def example_answers():
    """The original made-up student used in the notebook."""
    return {
        **{f"MSPSS_{i}": 4 for i in [3, 4, 8, 11]},
        **{f"FSS_{i}": 3 for i in range(1, 5)},
        **{f"AI_{i}": 4 for i in range(1, 16)},
        "Age": 16,
        "Gender": 1,
        "Form": 2,
        "Religion": 1,
        "Surviving_Parents": 2,
        "Parents_Dead": 4,
        "Fathers_Education": 3,
        "Mothers_Education": 3,
        "Co_Curricular": 2,
        "Sports": 2,
        "Percieved_Academic_Abilities": 3,
    }


class SavedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = ScreeningPriorityModel()
        cls.inputs = Preprocessor.prepare_student(example_answers())

    def test_score_matches_saved_pipeline(self):
        app_score = self.model.score(self.inputs).iloc[0]
        pipeline_score = self.model.pipeline.predict_proba(self.inputs)[
            0, self.model.positive_class_index
        ]
        self.assertAlmostEqual(app_score, pipeline_score, places=12)

    def test_score_is_between_zero_and_one(self):
        score = self.model.score(self.inputs).iloc[0]
        self.assertTrue(0 <= score <= 1)

    def test_column_order_does_not_change_score(self):
        reversed_inputs = self.inputs[self.inputs.columns[::-1]]
        original = self.model.score(self.inputs).iloc[0]
        reordered = self.model.score(reversed_inputs).iloc[0]
        self.assertAlmostEqual(original, reordered, places=12)

    def test_missing_answer_can_be_scored(self):
        inputs = self.inputs.copy()
        inputs.loc[0, "Religion"] = np.nan
        score = self.model.score(inputs).iloc[0]
        self.assertTrue(np.isfinite(score))

    def test_review_rule_uses_locked_threshold(self):
        score = self.model.score(self.inputs)
        actual = bool(self.model.needs_review(score).iloc[0])
        expected = bool(score.iloc[0] >= self.model.threshold)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()