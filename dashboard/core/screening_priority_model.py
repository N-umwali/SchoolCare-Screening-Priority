"""Load the locked model and score approved student answers."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

from .questions import APPROVED_COLUMNS, QUESTIONS


class ScreeningPriorityModel:
    """Score students with the pipeline selected before final testing."""

    def __init__(self, artifacts_dir=None):
        if artifacts_dir is None:
            artifacts_dir = Path(__file__).resolve().parents[1] / "model_artifacts"

        artifacts_dir = Path(artifacts_dir)
        details_path = artifacts_dir / "step5_locked_details.json"
        model_path = artifacts_dir / "selected_pipeline.joblib"

        if not details_path.is_file() or not model_path.is_file():
            raise FileNotFoundError(
                "The saved model files are missing from model_artifacts/. "
                "Add selected_pipeline.joblib and step5_locked_details.json."
            )

        with details_path.open(encoding="utf-8") as file:
            self.details = json.load(file)

        saved_columns = self.details["approved_input_columns"]
        if saved_columns != APPROVED_COLUMNS:
            raise ValueError(
                "The app's 34 questions do not match the saved model's "
                "input columns and order."
            )

        saved_version = self.details["scikit_learn_version"]
        if sklearn.__version__ != saved_version:
            raise RuntimeError(
                f"The model was saved with scikit-learn {saved_version}, "
                f"but this app has {sklearn.__version__}. Install the "
                "saved version before loading the model."
            )

        self.threshold = float(self.details["selected_threshold"])
        if not np.isfinite(self.threshold) or not 0 <= self.threshold <= 1:
            raise ValueError("The saved review threshold is invalid.")

        # Load only the model file exported from our own Step 5 notebook.
        self.pipeline = joblib.load(model_path)

        if not hasattr(self.pipeline, "predict_proba"):
            raise TypeError("The saved pipeline cannot produce priority scores.")

        model_columns = getattr(self.pipeline, "feature_names_in_", None)
        if model_columns is not None and list(model_columns) != saved_columns:
            raise ValueError(
                "The fitted pipeline expects different input columns."
            )

        classes = list(self.pipeline.classes_)
        if 1 not in classes:
            raise ValueError("The saved model has no elevated-symptom class.")
        self.positive_class_index = classes.index(1)

    @staticmethod
    def _check_inputs(inputs):
        """Require exactly the approved columns and valid survey codes."""
        if not isinstance(inputs, pd.DataFrame) or inputs.empty:
            raise ValueError("Provide a non-empty table of student answers.")

        if set(inputs.columns) != set(APPROVED_COLUMNS):
            raise ValueError(
                "Student answers must contain exactly the 34 approved columns."
            )

        # The saved pipeline expects numbers. Missing answers remain missing.
        ordered = inputs.loc[:, APPROVED_COLUMNS].copy()

        for column in APPROVED_COLUMNS:
            try:
                ordered[column] = pd.to_numeric(
                    ordered[column], errors="raise"
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"'{QUESTIONS[column]['header']}' contains a "
                    "non-numeric answer."
                ) from exc

            valid = set(QUESTIONS[column]["options"])
            invalid = (
                ordered[column].notna()
                & ~ordered[column].isin(valid)
            )
            if invalid.any():
                raise ValueError(
                    f"'{QUESTIONS[column]['header']}' contains an "
                    "answer outside its permitted choices."
                )

        return ordered

    def score(self, inputs):
        """Return one priority score between 0 and 1 per student."""
        ordered = self._check_inputs(inputs)
        probabilities = self.pipeline.predict_proba(ordered)

        scores = probabilities[:, self.positive_class_index]
        if not np.isfinite(scores).all():
            raise ValueError("The model returned an invalid priority score.")

        return pd.Series(
            scores,
            index=inputs.index,
            name="priority_score",
        )

    def needs_review(self, scores):
        """Apply the decision rule locked in Step 5."""
        return scores >= self.threshold