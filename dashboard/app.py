"""Start the dashboard and route to its separate page files."""

import streamlit as st

from ui.home import StreamlitInterface, go_to
from ui.prepare import render_prepare
from ui.styles import apply_styles
from ui.rank_class import render_rank_class
from ui.one_student import render_one_student

st.set_page_config(
    page_title="Screening Priority Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_styles()


PAGES = {
    "home": {
        "label": "Home",
        "render": StreamlitInterface().render_home,
    },
    "prepare": {
        "label": "Prepare questionnaire",
        "render": render_prepare,
    },
    "rank": {
        "label": "Rank a class",
        "render": render_rank_class,
    },
    "student": {
        "label": "One student",
        "render": render_one_student,
    },
}

st.session_state.setdefault("page", "home")

# Fall back to Home if an old session contains an unknown page.
current_page = st.session_state["page"]
current_page = {page: page for page in PAGES}.get(current_page, "home")
st.session_state["page"] = current_page

st.markdown(
    """
    <div class="app-brand">
        <div class="app-brand-title">Screening Priority Tool</div>
        <div class="app-brand-subtitle">
            For school counsellors · Pilot version
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

for column, (page, details) in zip(st.columns(4), PAGES.items()):
    with column:
        button_types = {True: "primary", False: "secondary"}
        st.button(
            details["label"],
            key=f"navigation_{page}",
            type=button_types[page == current_page],
            use_container_width=True,
            on_click=go_to,
            args=(page,),
        )

# Open the selected page using its registered function.
PAGES[current_page]["render"]()
