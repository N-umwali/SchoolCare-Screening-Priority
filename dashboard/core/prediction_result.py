"""Counsellor-facing results from the saved screening priority model."""

from dataclasses import dataclass
import math


SAFEGUARDING_MESSAGE = (
    "If you have an immediate concern about a student, follow your "
    "school's safeguarding process regardless of this result."
)


@dataclass(frozen=True)
class PredictionResult:
    student_id: str
    score: float
    prioritise: bool

    @classmethod
    def from_score(cls, student_id, score, model):
        """Apply the model's locked review rule to one score."""
        score = float(score)

        if not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError("The priority score must be between 0 and 1.")

        return cls(
            student_id=str(student_id).strip(),
            score=score,
            prioritise=bool(score >= model.threshold),
        )

    @property
    def score_out_of_100(self):
        return round(self.score * 100, 1)

    @property
    def guidance(self):
        if self.prioritise:
            return "Prioritise for counsellor review"
        return "Continue usual student support"

    def to_row(self):
        """Fields for a class ranking table or CSV download."""
        return {
            "Student ID": self.student_id,
            "Screening priority score": self.score_out_of_100,
            "Review guidance": self.guidance,
        }