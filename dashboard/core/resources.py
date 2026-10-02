"""Generate the questionnaire and class answer-sheet downloads."""

import csv
from html import escape
from io import StringIO

from .questions import (
    APPROVED_COLUMNS,
    DISPLAY_SECTIONS,
    QUESTIONS,
    SECTION_INTROS,
    SECTION_TITLES,
)


def build_csv_template():
    """Create an empty class answer sheet with readable column names."""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Student ID",
        *[QUESTIONS[column]["header"] for column in APPROVED_COLUMNS],
    ])

    # Excel can recognise these headers correctly with this encoding.
    return output.getvalue().encode("utf-8-sig")


def build_questionnaire():
    """Create a questionnaire that can be opened and printed in a browser."""
    sections = []
    question_number = 0

    for section in DISPLAY_SECTIONS:
        items = []
        introduction = SECTION_INTROS.get(section, "Choose one answer.")

        for column, item in QUESTIONS.items():
            if item["section"] != section:
                continue

            question_number += 1
            options = "".join(
                f'<span class="answer">□ {escape(label)}</span>'
                for label in item["options"].values()
            )

            items.append(
                f'<div class="question">'
                f'<p><strong>{question_number}. '
                f'{escape(item["question"])}</strong></p>'
                f'<div class="answers">{options}</div>'
                f'</div>'
            )

        sections.append(
            f'<section>'
            f'<h2>{escape(SECTION_TITLES[section])}</h2>'
            f'<p class="instruction">{escape(introduction)}</p>'
            f'{"".join(items)}'
            f'</section>'
        )

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Student questionnaire</title>
    <style>
        body {{
            max-width: 850px;
            margin: 35px auto;
            padding: 0 24px;
            color: #213B39;
            background: white;
            font: 15px/1.5 Arial, sans-serif;
        }}
        h1, h2 {{ color: #203D3B; }}
        h1 {{ font-size: 28px; }}
        h2 {{
            font-size: 21px;
            border-bottom: 2px solid #327B70;
            padding-bottom: 8px;
            margin-top: 28px;
        }}
        .instruction {{ color: #536962; }}
        .question {{
            padding: 10px 0 15px;
            border-bottom: 1px solid #DCE6DF;
            break-inside: avoid;
            page-break-inside: avoid;
        }}
        .question p {{ margin: 0 0 9px; }}
        .answer {{
            display: inline-block;
            margin: 0 20px 8px 0;
        }}
        .student-id {{
            margin: 22px 0;
            padding: 15px;
            border: 1px solid #DCE6DF;
        }}
        .print-note {{
            background: #EAF5F2;
            padding: 14px;
            border-radius: 8px;
        }}
        footer {{
            margin-top: 25px;
            color: #536962;
            font-size: 12px;
        }}
        @media print {{
            @page {{ size: A4; margin: 18mm; }}
            body {{ margin: 0; padding: 0; font-size: 11pt; }}
            .print-note {{ display: none; }}
            h2 {{ break-after: avoid; page-break-after: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="print-note">
        To print this questionnaire, use your browser's Print option.
        You can also choose “Save as PDF”.
    </div>

    <h1>Student questionnaire</h1>
    <p>
        Please answer using your own experiences and views.
        Choose one answer for each question. You may leave a question
        blank if you do not wish to answer.
    </p>

    <div class="student-id">
        <strong>Student ID:</strong> ______________________________
        <p>Use the ID provided by your counsellor. Do not write your name.</p>
    </div>

    {"".join(sections)}

    <footer>
        Screening Priority Tool · Pilot version<br>
        These answers help organise counsellor review.
        They do not diagnose depression.
    </footer>
</body>
</html>"""

    return document.encode("utf-8")


def build_question_list():
    """Create a plain-text question list for setting up a Google Form."""
    lines = [
        "STUDENT QUESTIONNAIRE — FORM SETUP",
        "",
        "Add a required short-answer field named Student ID.",
        "Use the ID assigned by the counsellor.",
        "Do not add names, email addresses or phone numbers.",
        "Allow students to skip questionnaire answers.",
        "",
        "Use the exact wording and answer options below.",
        "CSV header names are included for matching the exported answers",
        "to the class answer-sheet template.",
        "",
    ]

    for section in DISPLAY_SECTIONS:
        lines.extend([
            SECTION_TITLES[section].upper(),
            SECTION_INTROS.get(section, "Choose one answer."),
            "",
        ])

        for item in QUESTIONS.values():
            if item["section"] != section:
                continue

            lines.append(f"Question: {item['question']}")
            lines.append(f"CSV header: {item['header']}")
            lines.extend(
                f"- {label}" for label in item["options"].values()
            )
            lines.append("")

    return "\n".join(lines).encode("utf-8")