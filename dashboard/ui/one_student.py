"""Enter, check and score a student, then choose whether to save."""

import logging
from html import escape

import pandas as pd
import streamlit as st

from core.questions import QUESTIONS, DISPLAY_SECTIONS, SECTION_INTROS
from core.preprocessor import InputValidationError, Preprocessor
from core.prediction_result import PredictionResult, SAFEGUARDING_MESSAGE
from core.review_session import require
from .rank_class import load_model, review_session
from .home import go_to, show_html


PREFIX = "one_student_"


def show_nothing(value=None):
    return


def show_message():
    message = st.session_state.get(PREFIX + "message", "")
    {True: st.error, False: show_nothing}[bool(message)](message)


def skipped_count():
    return int(
        st.session_state[PREFIX + "inputs"].isna().sum().sum()
    )


def start_again():
    """Clear the open entry without deleting saved students."""
    keys = [
        key for key in st.session_state
        if key.startswith(PREFIX)
    ]

    for key in keys:
        st.session_state.pop(key, None)

    st.session_state[PREFIX + "stage"] = "entry"


def edit_answers():
    """Keep answers but clear the preview and confirmations."""
    for name in [
        "result", "message", "confirmed", "class_message",
        "replace_existing", "remove_confirmed",
    ]:
        st.session_state.pop(PREFIX + name, None)

    st.session_state[PREFIX + "stage"] = "entry"


def save_draft():
    """Keep the open form available when changing pages."""
    old_answers = st.session_state.get(PREFIX + "answers", {})

    st.session_state[PREFIX + "answers"] = {
        column: st.session_state.get(
            PREFIX + column, old_answers.get(column)
        )
        for column in QUESTIONS
    }

    st.session_state[PREFIX + "saved_id"] = str(
        st.session_state.get(
            PREFIX + "id",
            st.session_state.get(PREFIX + "saved_id", ""),
        )
    ).strip()


def prepare_review():
    """Validate answers before showing the review screen."""
    st.session_state.pop(PREFIX + "message", None)
    save_draft()

    student_id = st.session_state[PREFIX + "saved_id"]
    answers = st.session_state[PREFIX + "answers"]

    data = pd.DataFrame([
        {"Student ID": student_id, **answers}
    ])

    try:
        student_ids, inputs = Preprocessor.prepare_class(data)

    except InputValidationError:
        st.session_state[PREFIX + "message"] = (
            "Enter a Student ID and at least one valid answer."
        )
        return

    except ValueError as error:
        st.session_state[PREFIX + "message"] = str(error)
        return

    st.session_state[PREFIX + "saved_id"] = str(student_ids.iloc[0])
    st.session_state[PREFIX + "inputs"] = inputs
    st.session_state[PREFIX + "confirmed"] = False

    for name in [
        "result", "class_message",
        "replace_existing", "remove_confirmed",
    ]:
        st.session_state.pop(PREFIX + name, None)

    st.session_state[PREFIX + "stage"] = "review"


def create_result():
    """Prepare the result without adding it to the review list."""
    st.session_state.pop(PREFIX + "message", None)

    try:
        require(
            st.session_state.get(PREFIX + "confirmed", False),
            "Please confirm that you have checked the answers.",
        )
    except ValueError as error:
        st.session_state[PREFIX + "message"] = str(error)
        return

    try:
        model = load_model()
        scores = model.score(st.session_state[PREFIX + "inputs"])

        result = PredictionResult.from_score(
            st.session_state[PREFIX + "saved_id"],
            float(scores.iloc[0]),
            model,
        )

        st.session_state[PREFIX + "result"] = result

        for name in [
            "class_message", "replace_existing", "remove_confirmed",
        ]:
            st.session_state.pop(PREFIX + name, None)

        st.session_state[PREFIX + "stage"] = "result"

    except Exception:
        logging.exception("Single-student scoring failed.")
        st.session_state[PREFIX + "message"] = (
            "The result could not be prepared. "
            "Ask the app administrator to check the saved model setup."
        )


def result_row():
    result = st.session_state[PREFIX + "result"]

    return {
        **result.to_row(),
        "Student ID": str(result.student_id).strip(),
        "Skipped answers": skipped_count(),
        "_score": float(result.score),
        "_prioritise": bool(result.prioritise),
    }


def current_result_is_saved():
    """Check whether this result is individually saved."""
    row = result_row()
    saved = review_session().data["individual_rows"].get(
        row["Student ID"], {}
    )

    return all(
        saved.get(key) == value
        for key, value in row.items()
    )


def save_to_review_list():
    """Save only when the counsellor clicks Save."""
    session = review_session()
    result = st.session_state[PREFIX + "result"]

    try:
        confirmed = bool(
            st.session_state.get(PREFIX + "replace_existing", False)
        )

        require(
            not session.contains(result.student_id) or confirmed,
            "Confirm replacement of this Student ID first.",
        )

        session.save_individual(result_row(), replace=confirmed)
        st.session_state[PREFIX + "class_message"] = (
            "Saved to the review list. This student will be included "
            "when you rank an uploaded class."
        )

    except ValueError as error:
        st.session_state[PREFIX + "class_message"] = str(error)


def remove_saved_student():
    """Remove the individual result only after confirmation."""
    result = st.session_state[PREFIX + "result"]

    try:
        message = review_session().remove_individual(
            result.student_id,
            confirmed=bool(
                st.session_state.get(
                    PREFIX + "remove_confirmed", False
                )
            ),
        )

        st.session_state[PREFIX + "class_message"] = message
        st.session_state.pop(PREFIX + "replace_existing", None)
        st.session_state.pop(PREFIX + "remove_confirmed", None)

    except ValueError as error:
        st.session_state[PREFIX + "class_message"] = str(error)


def render_entry():
    st.subheader("Enter the student's answers")
    st.write(
        "Copy the answers from the questionnaire. "
        "Leave an answer as Skipped when it was not provided."
    )

    saved_answers = st.session_state.get(PREFIX + "answers", {})

    st.session_state.setdefault(
        PREFIX + "id",
        st.session_state.get(PREFIX + "saved_id", ""),
    )

    for column in QUESTIONS:
        st.session_state.setdefault(
            PREFIX + column, saved_answers.get(column)
        )

    st.text_input(
        "Student ID",
        key=PREFIX + "id",
        on_change=save_draft,
        help=(
            "Use the assigned questionnaire ID. "
            "Keep the student's name and ID mapping outside this app."
        ),
    )

    for section in DISPLAY_SECTIONS:
        st.markdown(f"### {section}")
        st.caption(
            SECTION_INTROS.get(
                section, "Select the student's recorded answers."
            )
        )

        section_questions = {
            column: question
            for column, question in QUESTIONS.items()
            if question["section"] == section
        }

        for column, question in section_questions.items():
            labels = {None: "Skipped", **question["options"]}

            st.selectbox(
                question["question"],
                options=list(labels),
                format_func=labels.__getitem__,
                key=PREFIX + column,
                on_change=save_draft,
            )

    st.button(
        "Check answers →",
        key=PREFIX + "check_answers",
        type="primary",
        use_container_width=True,
        on_click=prepare_review,
    )

    show_message()


def render_review():
    st.subheader("Check the student's answers")
    st.write(
        f"**Student ID:** {st.session_state[PREFIX + 'saved_id']}"
    )
    st.write(
        "Compare these answers with the questionnaire. "
        "Choose Edit answers to correct anything."
    )

    answers = st.session_state[PREFIX + "answers"]
    rows = []

    for column, question in QUESTIONS.items():
        labels = {None: "Skipped", **question["options"]}

        rows.append({
            "Section": question["section"],
            "Question": question["question"],
            "Answer": labels[answers[column]],
        })

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        f"Skipped answers: {skipped_count()} of {len(QUESTIONS)}. "
        "Skipped answers are handled by the saved scoring process."
    )

    confirmed = st.checkbox(
        "I have checked these answers against the questionnaire.",
        key=PREFIX + "confirmed",
    )

    back, next_step = st.columns(2)

    with back:
        st.button(
            "← Edit answers",
            key=PREFIX + "edit",
            use_container_width=True,
            on_click=edit_answers,
        )

    with next_step:
        st.button(
            "Show review result →",
            key=PREFIX + "score",
            type="primary",
            disabled=not confirmed,
            use_container_width=True,
            on_click=create_result,
        )

    show_message()


def show_saved_position(position):
    st.info(
        f"Saved in the review list: "
        f"rank {position[0]} of {position[1]} students."
    )


def show_remove_controls(student_id):
    """Offer removal of an individually saved result."""
    session = review_session()

    notes = {
        True: (
            "This ID also exists in the scored class sheet. "
            "Removing the individual result restores the "
            "class-sheet result in the ranking."
        ),
        False: (
            "Removing this saved result takes the student out "
            "of the review list. Other students remain unchanged."
        ),
    }

    st.caption(notes[session.has_class_student(student_id)])

    confirmed = st.checkbox(
        f"I want to remove the individually saved result for {student_id}.",
        key=PREFIX + "remove_confirmed",
    )

    st.button(
        "Remove from review list",
        key=PREFIX + "remove_saved",
        disabled=not confirmed,
        use_container_width=True,
        on_click=remove_saved_student,
    )


def show_class_comparison():
    st.divider()
    st.subheader("Save or discard this result")

    session = review_session()
    result = st.session_state[PREFIX + "result"]
    student_id = str(result.student_id).strip()
    ranked = session.ranking()

    saved_current = current_result_is_saved()
    duplicate = session.contains(student_id)

    statuses = {
        True: "This result is saved in the combined review list.",
        False: (
            "This result has not been individually saved. "
            "Choose Save to include it in the combined review list."
        ),
    }
    st.write(statuses[saved_current])
    st.caption(f"Students currently in the review list: {len(ranked)}.")

    saved_positions = ranked.loc[
        (ranked["Student ID"] == student_id)
        & (ranked["Entry method"] == "One student"),
        "Rank",
    ].tolist()

    position = (
        next(iter(saved_positions), 0),
        len(ranked),
    )
    {True: show_saved_position, False: show_nothing}[
        saved_current and bool(saved_positions)
    ](position)

    replace_confirmed = st.checkbox(
        "Replace the existing result for this Student ID.",
        key=PREFIX + "replace_existing",
        disabled=not duplicate or saved_current,
    )

    save_column, discard_column = st.columns(2)

    with save_column:
        st.button(
            "Save to review list",
            key=PREFIX + "save_result",
            type="primary",
            use_container_width=True,
            disabled=(
                saved_current
                or (duplicate and not replace_confirmed)
            ),
            on_click=save_to_review_list,
        )

    with discard_column:
        labels = {
            True: "Close this entry",
            False: "Discard this entry",
        }
        st.button(
            labels[saved_current],
            key=PREFIX + "discard_entry",
            use_container_width=True,
            on_click=start_again,
        )

    st.caption(
        "Discard or Close clears the open form and result. "
        "It does not delete a result already saved in the review list."
    )

    remove_handlers = {
        True: show_remove_controls,
        False: show_nothing,
    }
    remove_handlers[session.has_individual(student_id)](student_id)

    message = st.session_state.get(PREFIX + "class_message", "")
    {True: st.info, False: show_nothing}[bool(message)](message)

    st.button(
        "View combined ranking →",
        key=PREFIX + "view_class",
        use_container_width=True,
        on_click=go_to,
        args=("rank",),
    )

    st.caption(
        "Saved students can be ranked together with a class uploaded "
        "before or after them. Download the list before ending the session."
    )


def render_result():
    result = st.session_state[PREFIX + "result"]
    row = result.to_row()

    st.subheader("Student screening review")
    st.write(f"**Student ID:** {result.student_id}")

    st.metric(
        "Screening priority score",
        f"{result.score * 100:.1f} out of 100",
    )
    st.write(f"**Review guidance:** {row['Review guidance']}")
    st.caption(
        f"Skipped answers: {skipped_count()} of {len(QUESTIONS)}."
    )

    st.write(
        "Higher scores indicate higher screening priority. "
        "The score is not a percentage chance of depression "
        "and does not provide a diagnosis."
    )
    st.caption(
        "A low score should never prevent screening "
        "when you are concerned about a student."
    )

    download = pd.DataFrame([
        {**row, "Skipped answers": skipped_count()}
    ])

    st.download_button(
        "Download this student's result",
        data=download.to_csv(index=False).encode("utf-8-sig"),
        file_name="student_screening_review.csv",
        mime="text/csv",
        key=PREFIX + "download",
        use_container_width=True,
    )

    show_class_comparison()

    show_html(f"""
        <div class="care-note">
            <strong>Use your professional judgement.</strong>
            {escape(SAFEGUARDING_MESSAGE)}
        </div>
    """)

    st.button(
        "← Edit answers",
        key=PREFIX + "result_edit",
        use_container_width=True,
        on_click=edit_answers,
    )


def render_one_student():
    show_html("""
        <div class="section-heading">
            <div class="eyebrow">One student</div>
            <h2>Prepare a student's screening review</h2>
            <p>
                Enter the questionnaire answers, check them,
                and choose whether to save the result.
            </p>
        </div>
    """)

    st.session_state.setdefault(PREFIX + "stage", "entry")

    screens = {
        "entry": render_entry,
        "review": render_review,
        "result": render_result,
    }
    screens[st.session_state[PREFIX + "stage"]]()

    st.divider()
    st.button(
        "← Rank a class",
        key=PREFIX + "back_to_class",
        on_click=go_to,
        args=("rank",),
    )