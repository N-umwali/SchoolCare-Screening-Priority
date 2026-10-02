"""Shared appearance for the counsellor dashboard."""

import streamlit as st


def apply_styles():
    """Apply the dashboard's colours, spacing and reusable styles."""
    st.markdown(
        """
        <style>
        :root {
            --ink: #213B39;
            --teal: #327B70;
            --teal-dark: #203D3B;
            --teal-soft: #EAF5F2;
            --blue-soft: #EEF6FA;
            --muted: #536962;
            --line: #DCE6DF;
            --white: #FFFFFF;
        }

        /* White background and readable text. */
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {
            background: var(--white);
            color: var(--ink);
        }

        .stApp {
            font-family: Arial, Helvetica, sans-serif;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: var(--ink);
            line-height: 1.2;
        }

        h1, h2 {
            font-family: Georgia, "Times New Roman", serif;
        }

        p, li {
            line-height: 1.65;
        }

        [data-testid="stCaptionContainer"] {
            color: var(--muted);
        }

        a {
            color: var(--teal);
        }

        /* Shared buttons and keyboard focus. */
        .stButton > button,
        .stDownloadButton > button {
            min-height: 46px;
            padding: 0.65rem 1.1rem;
            border-radius: 9px;
            border: 1px solid var(--teal);
            background: var(--white);
            color: var(--teal-dark);
            font-weight: 600;
            transition: background 0.15s ease, border-color 0.15s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: var(--teal-soft);
            border-color: var(--teal-dark);
            color: var(--teal-dark);
        }

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background: var(--teal);
            border-color: var(--teal);
            color: var(--white);
        }

        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button[kind="primary"]:hover {
            background: #28665D;
            border-color: #28665D;
            color: var(--white);
        }

        .stButton > button:focus-visible,
        .stDownloadButton > button:focus-visible {
            outline: 3px solid #7CC4B3;
            outline-offset: 3px;
        }

        .stButton > button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Brand header and welcome section. */
        .app-brand {
            background: var(--teal-dark);
            color: var(--white);
            padding: 20px 26px;
            border-radius: 14px;
            margin-bottom: 12px;
        }

        .app-brand-title {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 24px;
            font-weight: 700;
        }

        .app-brand-subtitle {
            margin-top: 4px;
            color: #CDE2D9;
            font-size: 13px;
        }

        .home-hero {
            background: linear-gradient(115deg, #244542, #397E7A);
            border-radius: 18px;
            padding: 42px;
            margin: 20px 0;
            color: var(--white);
        }

        .home-hero h1 {
            color: var(--white);
            font-size: clamp(30px, 3.5vw, 46px);
            margin: 12px 0 20px;
        }

        .home-hero p {
            color: #E9F3ED;
            font-size: 17px;
            margin-bottom: 0;
        }

        .eyebrow {
            color: var(--teal);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .home-hero .eyebrow {
            color: #B3DFC9;
        }

        /* Reusable cards and section headings. */
        .dashboard-card {
            background: var(--white);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 16px;
            box-shadow: 0 5px 18px rgba(23, 61, 38, 0.04);
        }

        .dashboard-card h3 {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 20px;
            margin: 0 0 14px;
        }

        .dashboard-card p,
        .dashboard-card li {
            color: var(--muted);
            font-size: 15px;
        }

        .dashboard-card ul {
            padding-left: 20px;
            margin-bottom: 0;
        }

        .route-card {
            border-top: 4px solid var(--teal);
        }

        .step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: var(--teal);
            color: var(--white);
            font-weight: 700;
            margin-bottom: 18px;
        }

        .section-heading {
            margin-top: 28px;
            margin-bottom: 20px;
        }

        .section-heading h2 {
            margin-top: 4px;
            margin-bottom: 8px;
            font-size: 32px;
        }

        .soft-panel {
            background: var(--blue-soft);
            border: 1px solid #D6E6ED;
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 18px;
        }

        .care-note {
            background: #FFF9F1;
            border: 1px solid #EDE4D6;
            border-radius: 12px;
            padding: 18px 22px;
            color: #675549;
            font-size: 14px;
            line-height: 1.65;
            margin-top: 22px;
        }

        /* Forms and class-upload controls. */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input {
            background: var(--white);
            color: var(--ink);
        }

        [data-testid="stFileUploaderDropzone"] {
            background: var(--blue-soft);
            border: 2px dashed #A8C4B3;
            border-radius: 14px;
        }

        [data-testid="stMetric"] {
            background: var(--teal-soft);
            padding: 20px;
            border-radius: 14px;
        }

        .app-footer {
            border-top: 1px solid var(--line);
            padding-top: 18px;
            margin-top: 36px;
            color: var(--muted);
            font-size: 12px;
        }

        /* Keep the layout comfortable on smaller screens. */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .home-hero {
                padding: 26px;
            }

            .dashboard-card {
                padding: 22px;
            }

            .section-heading h2 {
                font-size: 28px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )