"""Exercise page callbacks with a small fake model, without loading artifacts."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

import pandas as pd
from core.review_session import ReviewSession


class FakeResult:
    def __init__(self, student_id, score):
        self.student_id, self.score = student_id, float(score)
        self.prioritise = self.score >= .5034

    @classmethod
    def from_score(cls, student_id, score, model):
        return cls(student_id, score)

    def to_row(self):
        return {"Student ID": self.student_id,
                "Screening priority score": round(self.score * 100, 1),
                "Review guidance": "Review"}


class FakeModel:
    def score(self, inputs):
        return inputs["score"].reset_index(drop=True)


def module(name, **attributes):
    result = types.ModuleType(name)
    result.__dict__.update(attributes)
    return result


class PageCallbackTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        fake_st = module("streamlit", session_state=self.state,
                         cache_resource=lambda function: function)
        fake_modules = {
            "streamlit": fake_st,
            "core.questions": module("core.questions", QUESTIONS={"score": {}},
                                     DISPLAY_SECTIONS=[], SECTION_INTROS={}),
            "core.prediction_result": module("core.prediction_result", PredictionResult=FakeResult,
                                             SAFEGUARDING_MESSAGE="Care"),
            "core.preprocessor": module("core.preprocessor", InputValidationError=type("InputValidationError", (ValueError,), {}),
                                        Preprocessor=object),
            "core.screening_priority_model": module("core.screening_priority_model", ScreeningPriorityModel=FakeModel),
            "ui.home": module("ui.home", go_to=lambda page: self.state.update(page=page), show_html=lambda value: None),
        }
        self.patch = patch.dict(sys.modules, fake_modules)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        root = Path(__file__).resolve().parents[1]
        self.rank = self.load("ui.rank_class", root / "ui/rank_class.py")
        self.student = self.load("ui.one_student", root / "ui/one_student.py")

    def load(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        result = importlib.util.module_from_spec(spec)
        sys.modules[name] = result
        spec.loader.exec_module(result)
        return result

    def score_individual(self, student_id="NEW", score=.7):
        self.state.update(one_student_saved_id=student_id,
                          one_student_inputs=pd.DataFrame({"score": [score]}),
                          one_student_confirmed=True)
        self.student.create_result()

    def upload_and_rank(self):
        uploaded = types.SimpleNamespace(name="class.csv", getvalue=lambda: b"class")
        self.rank.save_uploaded_file(uploaded)
        session = ReviewSession(self.state)
        self.rank.rank_students(pd.Series(["A", "B"]),
                                pd.DataFrame({"score": [.9, .4]}), session.data["file_hash"])

    def test_individual_first_is_saved_and_combined_on_upload(self):
        self.score_individual()
        self.upload_and_rank()
        self.assertEqual(ReviewSession(self.state).ranking()["Student ID"].tolist(), ["A", "NEW", "B"])

    def test_class_first_then_individual_is_combined(self):
        self.upload_and_rank()
        self.score_individual()
        self.assertEqual(len(ReviewSession(self.state).ranking()), 3)

    def test_return_to_empty_uploader_does_not_clear_saved_upload(self):
        self.upload_and_rank()
        self.rank.upload_changed()
        self.assertEqual(ReviewSession(self.state).file_bytes, b"class")
        self.assertEqual(len(ReviewSession(self.state).ranking()), 2)

    def test_duplicate_scoring_waits_for_confirmation(self):
        self.upload_and_rank()
        self.score_individual("A", .2)
        self.student.add_to_class()
        self.assertEqual(ReviewSession(self.state).ranking().iloc[0]["_score"], .9)
        self.state["one_student_replace_existing"] = True
        self.student.add_to_class()
        self.assertEqual(len(ReviewSession(self.state).ranking()), 2)
        self.assertEqual(ReviewSession(self.state).ranking().iloc[-1]["_score"], .2)

    def test_unconfirmed_answers_are_not_scored(self):
        self.state["one_student_confirmed"] = False
        self.student.create_result()
        self.assertTrue(ReviewSession(self.state).ranking().empty)
        self.assertNotIn("one_student_result", self.state)

    def test_new_student_form_does_not_clear_saved_list(self):
        self.score_individual()
        self.student.start_again()
        self.assertEqual(len(ReviewSession(self.state).ranking()), 1)


if __name__ == "__main__":
    unittest.main()
