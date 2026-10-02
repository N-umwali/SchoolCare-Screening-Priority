"""Check a class sheet and rank it together with individual students."""

from io import BytesIO
from html import escape
import logging

import pandas as pd
import streamlit as st

from core.prediction_result import PredictionResult, SAFEGUARDING_MESSAGE
from core.preprocessor import InputValidationError, Preprocessor
from core.screening_priority_model import ScreeningPriorityModel
from core.review_session import ReviewSession
from .home import go_to, show_html


@st.cache_resource
def load_model():
    """Cache the model, never student answers."""
    return ScreeningPriorityModel()


def review_session():
    return ReviewSession(st.session_state)


def show_nothing(value=None):
    return


def save_uploaded_file(uploaded):
    review_session().remember_upload(uploaded.getvalue(), uploaded.name)
    st.session_state.pop("review_class_error", None)
    st.session_state.pop("review_class_notice", None)
    st.session_state.pop("review_conflict_choice", None)


def upload_changed():
    """Keep stored bytes independent of the uploader's page lifecycle."""
    uploaded = st.session_state.get(review_session().upload_key)
    handlers = {True: show_nothing, False: save_uploaded_file}
    handlers[uploaded is None](uploaded)


def clear_uploaded_class():
    review_session().clear_class()
    for key in ["review_class_error", "review_class_notice", "review_conflict_choice"]:
        st.session_state.pop(key, None)


def clear_entire_list():
    review_session().clear_all()
    for key in ["review_class_error", "review_class_notice", "review_conflict_choice"]:
        st.session_state.pop(key, None)


def rank_students(student_ids, inputs, file_hash):
    """Score this sheet, then combine both sources without losing students."""
    session = review_session()
    try:
        from core.review_session import require
        require(file_hash == session.data["file_hash"], "The sheet changed. Check it again.")
        conflicts = session.individual_conflicts(student_ids)
        choices = {
            "Keep individually entered answers": "individual",
            "Use answers from the class sheet": "sheet",
        }
        choice = choices.get(st.session_state.get("review_conflict_choice"))
        require(not conflicts or choice is not None,
                "Choose which answers to keep for the repeated Student IDs.")
        model = load_model()
        scores = model.score(inputs)
        skipped = inputs.isna().sum(axis=1)
        rows = []
        for position, student_id in enumerate(student_ids):
            result = PredictionResult.from_score(str(student_id), float(scores.iloc[position]), model)
            rows.append({**result.to_row(), "Skipped answers": int(skipped.iloc[position]),
                         "_score": float(result.score), "_prioritise": bool(result.prioritise)})
        session.set_class(rows, choice)
        st.session_state.pop("review_class_error", None)
        st.session_state["review_class_notice"] = (
            f"Updated review list: {len(session.ranking())} students in total."
        )
    except ValueError as error:
        st.session_state["review_class_error"] = str(error)
    except Exception:
        logging.exception("Class scoring failed.")
        st.session_state["review_class_error"] = (
            "The list could not be prepared. Ask the app administrator to check the saved model."
        )


def show_conflicts(conflicts):
    st.warning("These Student IDs also have individually entered answers: " + ", ".join(conflicts))
    st.radio(
        "Which answers should the updated list use for these students?",
        ["Keep individually entered answers", "Use answers from the class sheet"],
        index=None,
        key="review_conflict_choice",
    )


def show_saved_class(content):
    session = review_session()
    st.caption(f"Current answer sheet: {session.file_name}")
    try:
        data = Preprocessor.read_csv(BytesIO(content))
        student_ids, inputs = Preprocessor.prepare_class(data)
    except InputValidationError as error:
        st.error("Some answers need correction before this sheet can be ranked.")
        st.dataframe(error.errors, hide_index=True, use_container_width=True)
        return
    except ValueError as error:
        st.error(str(error))
        return

    st.success(f"Answer sheet checked: {len(inputs)} students.")
    st.caption(f"{int(inputs.isna().any(axis=1).sum())} students in this sheet have skipped answers.")
    conflicts = session.individual_conflicts(student_ids)
    handlers = {True: show_conflicts, False: show_nothing}
    handlers[bool(conflicts)](conflicts)
    unresolved = bool(conflicts) and st.session_state.get("review_conflict_choice") is None
    st.button(
        "Rank students / update list", key="rank_students", type="primary",
        use_container_width=True, disabled=unresolved, on_click=rank_students,
        args=(student_ids, inputs, session.data["file_hash"]),
    )


def show_empty_upload(value=None):
    st.info("Upload a class sheet to add its students. Individually saved students appear below.")


def show_ranking(ranked):
    st.divider()
    st.subheader("Your combined screening review list")
    first, second, third = st.columns(3)
    first.metric("Students ranked", len(ranked))
    second.metric("Prioritised for review", int(ranked["_prioritise"].sum()))
    third.metric("Students with skipped answers", int((ranked["Skipped answers"] > 0).sum()))
    st.write("Start at the top. Higher scores indicate higher screening priority. "
             "This list combines the class sheet and individually saved students.")
    display_table = ranked.drop(columns=["_score", "_prioritise"])
    st.dataframe(display_table, hide_index=True, use_container_width=True)
    st.caption("The score is a guide to review order, not a percentage chance of depression. "
               "A low score should never prevent screening when you are concerned.")
    st.download_button(
        "Download the combined ranked list",
        data=display_table.to_csv(index=False).encode("utf-8-sig"),
        file_name="screening_review_list.csv", mime="text/csv",
        key="download_ranking", type="primary", use_container_width=True,
    )
    show_html(f'<div class="care-note"><strong>Use your professional judgement.</strong> '
              f'{escape(SAFEGUARDING_MESSAGE)}</div>')


def render_rank_class():
    session = review_session()
    show_html("""
        <div class="section-heading">
            <div class="eyebrow">Class ranking</div>
            <h2>Rank students for screening review</h2>
            <p>Upload a class sheet and combine it with individually entered students.</p>
        </div>
    """)
    st.caption("Use the template from Prepare questionnaire. Include Student IDs and answers only.")
    st.caption("Your sheet and saved students stay available while you move between pages in this session. "
               "The upload box may look empty when you return; the current sheet is named below.")
    st.file_uploader("Upload or replace a class answer sheet", type=["csv"],
                     key=session.upload_key, on_change=upload_changed)
    st.caption("To remove a stored sheet, use Clear uploaded class below. "
               "Replacing the sheet preserves individually saved students.")
    handlers = {True: show_empty_upload, False: show_saved_class}
    handlers[session.file_bytes is None](session.file_bytes)

    error = st.session_state.get("review_class_error", "")
    {True: st.error, False: show_nothing}[bool(error)](error)
    notice = st.session_state.get("review_class_notice", "")
    {True: st.success, False: show_nothing}[bool(notice)](notice)
    ranked = session.ranking()
    {True: show_ranking, False: show_nothing}[not ranked.empty](ranked)

    st.divider()
    left, right = st.columns(2)
    with left:
        st.button("Clear uploaded class", on_click=clear_uploaded_class,
                  disabled=session.file_bytes is None, use_container_width=True)
    with right:
        confirmed = st.checkbox("I want to clear the entire review list.", key="review_clear_confirm")
        st.button("Clear entire review list", on_click=clear_entire_list,
                  disabled=not confirmed, use_container_width=True)
    st.caption("Download the list before clearing it or ending the session. "
               "Clear uploaded class keeps individually saved students; Clear entire review list removes both.")
    back, next_page = st.columns(2)
    with back:
        st.button("← Prepare questionnaire", key="rank_prepare", on_click=go_to,
                  args=("prepare",), use_container_width=True)
    with next_page:
        st.button("One student →", key="rank_one_student", on_click=go_to,
                  args=("student",), use_container_width=True)
