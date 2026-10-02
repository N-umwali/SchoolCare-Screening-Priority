"""Home page for the Screening Priority Tool."""

from textwrap import dedent

import streamlit as st

from .styles import apply_styles


def go_to(page):
    """Remember which page the counsellor wants to open."""
    st.session_state["page"] = page


def show_html(content):
    """Display the page's static content."""
    st.markdown(dedent(content), unsafe_allow_html=True)


class StreamlitInterface:
    """Counsellor interface, following the proposal's component name."""

    def render_home(self):
        apply_styles()

        show_html("""
            <div class="home-hero">
                <div style="display:flex; flex-wrap:wrap; gap:36px;
                            align-items:center;">
                    <div style="flex:2; min-width:240px;">
                        <div class="eyebrow">
                            Support for busy school counselling teams
                        </div>
                        <h1>
                            Know which students to offer
                            depression screening first.
                        </h1>
                        <p>
                            Students answer questions about their family,
                            money worries, hopes for the future and school
                            life. The tool uses these answers to suggest
                            the order in which to offer formal depression
                            screening.
                        </p>
                    </div>
                    <div style="flex:1; min-width:240px;
                                border:1px solid #8CAC9C;
                                border-radius:16px; padding:24px;
                                background:rgba(255,255,255,0.08);">
                        <div class="eyebrow">Before you start</div>
                        <h3 style="color:white;">What you will need</h3>
                        <ul style="padding-left:20px; color:#E9F3ED;">
                            <li>The questionnaire provided by this tool</li>
                            <li>A private ID for each student</li>
                            <li>The student's own answers</li>
                            <li>Your school's usual screening and
                                referral process</li>
                        </ul>
                    </div>
                </div>
            </div>
        """)

        left, right = st.columns(2)
        with left:
            st.button(
                "Prepare the questionnaire →",
                key="home_prepare",
                type="primary",
                use_container_width=True,
                on_click=go_to,
                args=("prepare",),
            )
        with right:
            st.button(
                "I have my class answers →",
                key="home_class_answers",
                use_container_width=True,
                on_click=go_to,
                args=("rank",),
            )

        show_html("""
            <div class="section-heading">
                <div class="eyebrow">Choose where to start</div>
                <h2>Three simple steps</h2>
                <p>
                    Prepare the questionnaire, rank a class,
                    or enter one student's answers.
                </p>
            </div>
        """)

        routes = [
            {
                "number": 1,
                "title": "Prepare the questionnaire",
                "description": (
                    "Get the questionnaire and class answer-sheet "
                    "template. Use the same questions for every student."
                ),
                "button": "Get the questionnaire →",
                "page": "prepare",
            },
            {
                "number": 2,
                "title": "Rank a class",
                "description": (
                    "Upload your class answers, correct any errors, "
                    "and see which students to offer screening first."
                ),
                "button": "Rank a class →",
                "page": "rank",
            },
            {
                "number": 3,
                "title": "One student",
                "description": (
                    "Enter one student's questionnaire answers, "
                    "check them, and see their screening priority."
                ),
                "button": "Enter one student →",
                "page": "student",
            },
        ]

        for column, route in zip(st.columns(3), routes):
            with column:
                show_html(f"""
                    <div class="dashboard-card route-card">
                        <span class="step-number">{route["number"]}</span>
                        <h3>{route["title"]}</h3>
                        <p>{route["description"]}</p>
                    </div>
                """)
                st.button(
                    route["button"],
                    key=f'home_route_{route["page"]}',
                    type="primary",
                    use_container_width=True,
                    on_click=go_to,
                    args=(route["page"],),
                )

        st.write("")

        first, second, third = st.columns(3)

        with first:
            show_html("""
                <div class="dashboard-card">
                    <h3>What the tool does</h3>
                    <ul>
                        <li>Suggests an order for offering depression
                            screening</li>
                        <li>Uses answers about home, money, aspirations
                            and school life</li>
                        <li>Identifies students by their assigned ID</li>
                        <li>Checks answers before scoring</li>
                    </ul>
                </div>
            """)

        with second:
            show_html("""
                <div class="dashboard-card">
                    <h3>What it does not do</h3>
                    <ul>
                        <li>Diagnose depression</li>
                        <li>Assess suicide risk</li>
                        <li>Recommend treatment</li>
                        <li>Replace your professional judgement</li>
                    </ul>
                </div>
            """)

        with third:
            show_html("""
                <div class="dashboard-card">
                    <h3>Know its limits</h3>
                    <ul>
                        <li>Some students who need support may receive
                            a low score</li>
                        <li>In the research test, more elevated cases
                            were missed among boys than girls</li>
                        <li>Use students' own answers</li>
                        <li>Keep the list linking IDs to names securely
                            outside this tool</li>
                    </ul>
                </div>
            """)

        show_html("""
            <div class="care-note">
                <strong>Use with care.</strong>
                A low score should never stop you from offering screening
                when you are concerned about a student. If you are worried
                about their immediate safety, follow your school's
                safeguarding procedure straight away.
            </div>
            <div class="app-footer">
                Pilot version · African Leadership University capstone project
                · For school counsellors
            </div>
        """)