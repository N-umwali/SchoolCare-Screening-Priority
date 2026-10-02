"""Questionnaire resources for the school counsellor."""

import streamlit as st

from core.resources import (
    build_csv_template,
    build_question_list,
    build_questionnaire,
)
from .home import go_to, show_html


def render_prepare():
    show_html("""
        <div class="section-heading">
            <div class="eyebrow">Step 1 · Prepare</div>
            <h2>Prepare the questionnaire</h2>
            <p>
                Give every student the same questions and answer choices.
                Use the downloads below to collect their answers and
                prepare your class answer sheet.
            </p>
        </div>
    """)

    first, second, third = st.columns(3)

    with first:
        show_html("""
            <div class="dashboard-card route-card">
                <span class="step-number">1</span>
                <h3>Printable questionnaire</h3>
                <p>
                    Download the questionnaire, open it in your browser,
                    and print one copy for each student.
                    You can also save it as a PDF.
                </p>
            </div>
        """)
        st.download_button(
            "Download questionnaire",
            data=build_questionnaire(),
            file_name="student_questionnaire.html",
            mime="text/html",
            key="download_questionnaire",
            type="primary",
            use_container_width=True,
        )

    with second:
        show_html("""
            <div class="dashboard-card route-card">
                <span class="step-number">2</span>
                <h3>Class answer sheet</h3>
                <p>
                    Download the blank CSV template.
                    Enter one student per row, using their assigned ID
                    and the answers from their questionnaire.
                </p>
            </div>
        """)
        st.download_button(
            "Download answer sheet",
            data=build_csv_template(),
            file_name="class_answer_sheet.csv",
            mime="text/csv",
            key="download_class_template",
            type="primary",
            use_container_width=True,
        )

    with third:
        show_html("""
            <div class="dashboard-card route-card">
                <span class="step-number">3</span>
                <h3>Google Form question list</h3>
                <p>
                    Get the question wording and answer choices to copy
                    into a Google Form. The list also shows how to match
                    the answers to the class answer sheet.
                </p>
            </div>
        """)
        st.download_button(
            "Download question list",
            data=build_question_list(),
            file_name="google_form_question_list.txt",
            mime="text/plain",
            key="download_form_questions",
            type="primary",
            use_container_width=True,
        )

    st.write("")

    left, right = st.columns(2)

    with left:
        show_html("""
            <div class="dashboard-card">
                <h3>Collect the student's own answers</h3>
                <ol>
                    <li>Assign each student a private Student ID.</li>
                    <li>Ask students to complete the questionnaire
                        themselves.</li>
                    <li>Keep the list linking IDs to names securely
                        outside this tool.</li>
                    <li>Use one row per student for each screening round.</li>
                </ol>
            </div>
        """)

    with right:
        show_html("""
            <div class="dashboard-card">
                <h3>Complete the class answer sheet</h3>
                <ol>
                    <li>Keep the template's column headings unchanged.</li>
                    <li>Enter the answer words or their survey codes.</li>
                    <li>Leave skipped answers blank.</li>
                    <li>Save the completed sheet as a CSV file.</li>
                </ol>
                <p>
                    If an ID begins with zero, format its spreadsheet
                    column as text before entering it.
                </p>
            </div>
        """)

    with st.expander("Using answers collected in Google Forms"):
        st.write(
            "Use the downloaded question list to create your form. "
            "Collect the assigned Student ID, and allow questionnaire "
            "questions to be skipped."
        )
        st.write(
            "After collecting responses, copy the Student IDs and answers "
            "into the matching columns of the class answer-sheet template. "
            "Do not include the Google Forms timestamp or email columns."
        )
        st.write(
            "Check that each student's ID and answers stay together "
            "when copying them. Save the completed template as CSV."
        )

    show_html("""
        <div class="care-note">
            <strong>Before collecting answers.</strong>
            Follow your school's consent and privacy procedures.
            Do not include names, contact details or depression and anxiety
            symptom answers in the class file. Use students' own responses;
            do not guess missing answers.
        </div>
    """)

    st.write("")

    back, next_page = st.columns(2)

    with back:
        st.button(
            "← Home",
            key="prepare_home",
            use_container_width=True,
            on_click=go_to,
            args=("home",),
        )

    with next_page:
        st.button(
            "Next: rank a class →",
            key="prepare_rank",
            type="primary",
            use_container_width=True,
            on_click=go_to,
            args=("rank",),
        )