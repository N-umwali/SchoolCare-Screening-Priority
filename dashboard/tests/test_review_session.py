"""Check combining, replacement and page-independent session storage."""

import unittest
from core.review_session import ReviewSession


def row(student_id, score):
    return {"Student ID": student_id, "Screening priority score": round(score * 100, 1),
            "Review guidance": "Review", "Skipped answers": 0,
            "_score": score, "_prioritise": score >= 0.5034}


class ReviewSessionTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        self.session = ReviewSession(self.state)

    def test_individual_first_then_class(self):
        self.session.save_individual(row("NEW", .7))
        self.session.remember_upload(b"class", "class.csv")
        self.session.set_class([row("A", .9), row("B", .4)])
        self.assertEqual(self.session.ranking()["Student ID"].tolist(), ["A", "NEW", "B"])

    def test_class_first_then_individual(self):
        self.session.set_class([row("A", .9), row("B", .4)])
        self.session.save_individual(row("NEW", .7))
        self.assertEqual(self.session.ranking()["Rank"].tolist(), [1, 2, 3])

    def test_reranking_preserves_individuals(self):
        self.session.set_class([row("A", .5)])
        self.session.save_individual(row("NEW", .7))
        self.session.set_class([row("A", .6)])
        self.assertEqual(len(self.session.ranking()), 2)

    def test_navigation_widget_cleanup_keeps_file_and_students(self):
        self.session.remember_upload(b"class", "class.csv")
        self.session.set_class([row("A", .8)])
        self.state[self.session.upload_key] = object()
        del self.state[self.session.upload_key]
        returned = ReviewSession(self.state)
        self.assertEqual(returned.file_bytes, b"class")
        self.assertEqual(len(returned.ranking()), 1)

    def test_new_upload_removes_previous_class_only(self):
        self.session.remember_upload(b"old", "old.csv")
        self.session.set_class([row("OLD", .8)])
        self.session.save_individual(row("NEW", .7))
        self.session.remember_upload(b"replacement", "new.csv")
        self.assertEqual(self.session.ranking()["Student ID"].tolist(), ["NEW"])

    def test_identical_upload_does_not_clear_ranking(self):
        self.session.remember_upload(b"class", "class.csv")
        self.session.set_class([row("A", .8)])
        self.session.remember_upload(b"class", "class.csv")
        self.assertEqual(len(self.session.ranking()), 1)

    def test_individual_duplicate_needs_confirmation(self):
        self.session.set_class([row("A", .8)])
        with self.assertRaises(ValueError):
            self.session.save_individual(row("A", .4))
        self.assertEqual(self.session.ranking().iloc[0]["_score"], .8)

    def test_confirmed_individual_replacement_no_duplicate(self):
        self.session.set_class([row("A", .8)])
        self.session.save_individual(row("A", .4), replace=True)
        self.assertEqual(len(self.session.ranking()), 1)
        self.assertEqual(self.session.ranking().iloc[0]["_score"], .4)

    def test_class_conflict_needs_choice(self):
        self.session.save_individual(row("A", .8))
        with self.assertRaises(ValueError):
            self.session.set_class([row("A", .4)])
        self.assertEqual(self.session.ranking().iloc[0]["_score"], .8)

    def test_confirmed_keep_individual(self):
        self.session.save_individual(row("A", .8))
        self.session.set_class([row("A", .4)], "individual")
        self.assertEqual(self.session.ranking().iloc[0]["_score"], .8)

    def test_confirmed_use_class(self):
        self.session.save_individual(row("A", .8))
        self.session.set_class([row("A", .4)], "sheet")
        self.assertEqual(self.session.ranking().iloc[0]["_score"], .4)
        self.assertFalse(self.session.data["individual_rows"])

    def test_clear_class_keeps_individuals_and_resets_uploader(self):
        key = self.session.upload_key
        self.session.set_class([row("A", .8)])
        self.session.save_individual(row("B", .4))
        self.session.clear_class()
        self.assertEqual(self.session.ranking()["Student ID"].tolist(), ["B"])
        self.assertNotEqual(key, self.session.upload_key)

    def test_clear_all_removes_both_sources(self):
        self.session.set_class([row("A", .8)])
        self.session.save_individual(row("B", .4))
        self.session.clear_all()
        self.assertTrue(self.session.ranking().empty)

    def test_unrounded_scores_control_order(self):
        self.session.set_class([row("A", .60001), row("B", .60002)])
        self.assertEqual(self.session.ranking()["Student ID"].tolist(), ["B", "A"])

    def test_repeated_class_ids_rejected(self):
        with self.assertRaises(ValueError):
            self.session.set_class([row("A", .8), row("A", .4)])


if __name__ == "__main__":
    unittest.main()
