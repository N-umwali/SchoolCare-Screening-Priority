# SchoolCare: Student Screening Priority

SchoolCare helps secondary-school counsellors organise which students to review first for formal depression screening. It uses information about family support, financial strain, aspirations, and student circumstances.

The screening priority score guides review order. It is not a diagnosis or a percentage chance of depression.

## GitHub repository

[SchoolCare-Screening-Priority](https://github.com/N-umwali/SchoolCare-Screening-Priority)

## Project Scope

The work includes data preparation, exploratory analysis, model training, evaluation on held-out schools, and a Streamlit dashboard for counsellors.

## Data and outcome

The project uses Survey C from a Kenyan secondary-school student survey.

- Original dataset: 2,905 records and 56 columns.
- Eligible students: 1,799 from 32 schools.
- Elevated PHQ-8 symptoms: 535 students, or 29.7%.

Students were included when their school was recorded and all eight PHQ items were answered. Undefined predictor codes were converted to missing values.

The outcome is an elevated PHQ-8 score of 10 or more. PHQ and GAD answers are excluded from the model inputs.

The model uses 34 non-symptom predictors. Missing predictor answers are handled by the saved preprocessing pipeline.

## Training and evaluation

Students were split by school to keep the final test schools separate from model development:

- Development: 1,438 students from 25 schools.
- Final test: 361 students from 7 schools.

Logistic Regression, Decision Tree, and Random Forest were compared using five school-aware validation folds. Preprocessing was fitted within each training fold.

Logistic Regression was selected using the highest mean validation ROC-AUC. Its review threshold was chosen from development-only predictions and fixed before final testing.

## Final results

| Model | ROC-AUC | Recall | Precision | F1 |
|---|---:|---:|---:|---:|
| Logistic Regression: selected model | 0.685 | 0.577 | 0.403 | 0.475 |
| Random Forest: secondary comparison | 0.673 | 0.608 | 0.393 | 0.478 |
| Decision Tree: secondary comparison | 0.598 | 0.577 | 0.316 | 0.409 |

The selected model met the ROC-AUC target of 0.65 but missed the recall target of 0.60. It identified 56 of the 97 students with elevated PHQ-8 symptoms in the final test set.

Random Forest met both targets in the secondary comparison. The selected model was retained because the choice had been fixed before viewing test results.

A secondary sensitivity analysis excluded students who gave a non-zero answer to the attention-check question. Those results did not replace the primary model.

## Dashboard features

The dashboard provides four pages:

- **Home:** an introduction and navigation to the main tasks.
- **Prepare questionnaire:** download the questionnaire and class answer sheet.
- **Rank a class:** upload a completed CSV, check answers, and download a ranked review list.
- **One student:** enter answers, check them, view a result, and choose whether to save it to the current review list.

Individually entered students can be compared with students from an uploaded class sheet. Saved individual entries can also be removed.

Student IDs help counsellors match results to their own school records. Names are not required.

## Interface designs

Dashboard screenshots are stored in `reports/dashboard_screenshots/`.

They show the Home page, questionnaire downloads, class ranking,
and individual student review.

## Repository folders

| Location | Contents |
|---|---|
| `codebook/` | Survey wording and answer definitions |
| `data/` | Locally stored raw and prepared data |
| `notebook/` | Data preparation, analysis, training, and evaluation |
| `reports/` | Saved tables and figures |
| `dashboard/app.py` | Dashboard entry point and navigation |
| `dashboard/core/` | Questions, answer conversion, checks, scoring, and review session |
| `dashboard/ui/` | Dashboard pages and styling |
| `dashboard/model_artifacts/` | Saved pipeline and locked model details |
| `dashboard/tests/` | Automated checks |
| `dashboard/requirements.txt` | Required Python packages |

## Run the dashboard

Open a terminal in the repository folder.

Create a virtual environment:

    python -m venv .venv

Activate it in Windows PowerShell:

    .venv\Scripts\Activate.ps1

Or activate it in Git Bash:

    source .venv/Scripts/activate

Install the required packages:

    python -m pip install -r dashboard/requirements.txt

Start the dashboard:

    python -m streamlit run dashboard/app.py

Open the local address shown in the terminal.

The following files must be available together:

- `dashboard/model_artifacts/selected_pipeline.joblib`
- `dashboard/model_artifacts/step5_locked_details.json`

Use the scikit-learn version recorded in the model details. The saved pipeline and its metadata must come from the same training run.

## Run the tests

From the repository folder:

    cd dashboard
    python -m unittest discover -s tests -v

The tests cover answer conversion, input checks, saved model scoring, and review list behaviour.

## Use the notebook

Open the notebook in `notebook/` using Jupyter or Google Colab.

Follow the steps in order. Keep preprocessing within training folds and retain the original school split, model selection rule, and locked thresholds.

Data paths may need adjusting when running in Google Colab.

## Deployment plan

The initial demonstration runs locally using Streamlit.

A hosted pilot is planned after checking access controls, student-data
handling, and compatibility with the saved model. Public demonstrations
use invented student records.

## Responsible use

Higher scores indicate higher screening priority. A lower score must not prevent screening when a counsellor is concerned about a student.

Performance differed across gender and age groups in the test sample. Results from these schools do not establish performance in every school.

The dashboard keeps the review list in the current session rather than a database. Download the list before ending the session. Keep student answer sheets and review lists out of GitHub, and use invented student records for public demonstrations.

School safeguarding procedures and professional judgement always take priority over the score.

## Author

**Umwali Noella**  
BSc Software Engineering  
African Leadership University
