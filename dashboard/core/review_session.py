"""Keep uploaded and individually saved students in one session."""

import hashlib
import math

import pandas as pd


def require(condition, message):
    """Check a rule and provide a readable error."""
    try:
        {True: True}[bool(condition)]
    except KeyError:
        raise ValueError(message) from None


class ReviewSession:
    """Keep review data separate from temporary page widgets."""

    KEY = "screening_review_session_v2"

    def __init__(self, state):
        self.data = state.setdefault(
            self.KEY,
            {
                "file_bytes": None,
                "file_name": "",
                "file_hash": "",
                "class_rows": {},
                "individual_rows": {},
                "upload_revision": 0,
            },
        )

    @staticmethod
    def _student_id(student_id):
        """Use the same ID format for saving and removing."""
        return str(student_id).strip()

    @property
    def upload_key(self):
        return f"review_class_upload_{self.data['upload_revision']}"

    @property
    def file_bytes(self):
        return self.data["file_bytes"]

    @property
    def file_name(self):
        return self.data["file_name"]

    def remember_upload(self, content, name):
        """Replace the class sheet while keeping individual students."""
        digest = hashlib.sha256(content).hexdigest()
        changed = digest != self.data["file_hash"]

        self.data["class_rows"] = {
            True: {},
            False: self.data["class_rows"],
        }[changed]

        self.data.update(
            file_bytes=content,
            file_name=name,
            file_hash=digest,
        )

    def clear_class(self):
        """Remove the uploaded class, keeping individual students."""
        self.data.update(
            file_bytes=None,
            file_name="",
            file_hash="",
            class_rows={},
        )
        self.data["upload_revision"] += 1

    def clear_all(self):
        """Remove both sources from the review list."""
        self.clear_class()
        self.data["individual_rows"] = {}

    def _checked_row(self, row, source):
        """Check a result before adding it to the list."""
        row = dict(row)
        student_id = self._student_id(row["Student ID"])
        score = float(row["_score"])

        require(bool(student_id), "Enter a Student ID.")
        require(
            math.isfinite(score) and 0 <= score <= 1,
            "Invalid saved score.",
        )

        row.update(
            {
                "Student ID": student_id,
                "_score": score,
                "_prioritise": bool(row["_prioritise"]),
                "Entry method": source,
            }
        )
        row.pop("Rank", None)
        return row

    def contains(self, student_id):
        """Check whether an ID exists in either source."""
        return (
            self.has_class_student(student_id)
            or self.has_individual(student_id)
        )

    def has_class_student(self, student_id):
        """Check whether an ID is in the scored class sheet."""
        student_id = self._student_id(student_id)
        return student_id in self.data["class_rows"]

    def has_individual(self, student_id):
        """Check whether an individual result has been saved."""
        student_id = self._student_id(student_id)
        return student_id in self.data["individual_rows"]

    def individual_conflicts(self, student_ids):
        """Find uploaded IDs that also have individual results."""
        uploaded_ids = {
            self._student_id(student_id)
            for student_id in student_ids
        }
        return sorted(
            uploaded_ids & set(self.data["individual_rows"])
        )

    def save_individual(self, row, replace=False):
        """Save a result when the counsellor chooses to retain it."""
        row = self._checked_row(row, "One student")
        student_id = row["Student ID"]

        require(
            not self.contains(student_id) or replace,
            "Confirm replacement of this Student ID first.",
        )

        self.data["individual_rows"][student_id] = row

    def remove_individual(self, student_id, confirmed=False):
        """Remove one individual result after confirmation."""
        student_id = self._student_id(student_id)

        require(
            self.has_individual(student_id),
            "This student has no individually saved result to remove.",
        )
        require(
            confirmed,
            "Confirm removal of this student's saved result first.",
        )

        self.data["individual_rows"].pop(student_id)

        # A class-sheet result for the same ID remains available.
        messages = {
            True: (
                f"Removed the individual result for {student_id}. "
                "The class-sheet result is now used in the ranking."
            ),
            False: (
                f"Removed {student_id} from the review list. "
                "Other students remain unchanged."
            ),
        }
        return messages[self.has_class_student(student_id)]

    def set_class(self, rows, conflict_choice=None):
        """Combine scored class rows with saved individual results."""
        checked = [
            self._checked_row(row, "Class sheet")
            for row in rows
        ]
        indexed = {
            row["Student ID"]: row
            for row in checked
        }

        require(
            len(indexed) == len(checked),
            "Repeated Student IDs in class sheet.",
        )

        overlaps = (
            set(indexed) & set(self.data["individual_rows"])
        )
        require(
            not overlaps
            or conflict_choice in ("individual", "sheet"),
            "Choose which answers to use for repeated Student IDs.",
        )

        # Replace overlapping individual results only when chosen.
        remove = {
            True: overlaps,
            False: set(),
        }[conflict_choice == "sheet"]

        remaining = {
            key: value
            for key, value in self.data["individual_rows"].items()
            if key not in remove
        }

        self.data["class_rows"] = indexed
        self.data["individual_rows"] = remaining

    def ranking(self):
        """Build the combined list using full scores."""
        combined = {
            **self.data["class_rows"],
            **self.data["individual_rows"],
        }

        columns = [
            "Student ID",
            "Screening priority score",
            "Review guidance",
            "Skipped answers",
            "Entry method",
            "_score",
            "_prioritise",
        ]

        ranked = pd.DataFrame(
            list(combined.values()),
            columns=columns,
        )

        ranked = (
            ranked.sort_values(
                "_score",
                ascending=False,
                kind="stable",
            )
            .reset_index(drop=True)
        )
        ranked.insert(
            0,
            "Rank",
            range(1, len(ranked) + 1),
        )
        return ranked