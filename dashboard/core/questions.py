"""Approved Survey C questions for the counsellor app.

Only the 34 non-symptom inputs used by the saved model appear here.
Wording and answer codes follow the Survey C codebook.
APPROVED_COLUMNS is in the model's input order; the app still reorders
columns using approved_input_columns from step5_locked_details.json.
"""

SUPPORT_OPTIONS = {
    1: "Very strongly disagree",
    2: "Strongly disagree",
    3: "Mildly disagree",
    4: "Neutral",
    5: "Mildly agree",
    6: "Strongly agree",
    7: "Very strongly agree",
}

FINANCE_OPTIONS = {
    1: "Not at all",
    2: "Seldom",
    3: "Sometimes",
    4: "Often",
    5: "Very often",
}

ASPIRATION_OPTIONS = {
    1: "Not important at all",
    2: "2",
    3: "3",
    4: "Moderately important",
    5: "5",
    6: "6",
    7: "Very important",
}

EDUCATION_OPTIONS = {
    1: "Not aware",
    2: "Primary school",
    3: "Secondary school",
    4: "University",
}

# Extra spellings accepted when reading answers (e.g. the codebook's own wording).
SUPPORT_ALIASES = {6: ["Strong agree"]}

# Shown once above each section (the codebook asks the aspiration items this way).
SECTION_INTROS = {
    "Family support": "How much do you agree with each statement?",
    "Financial strain": "How often does this happen to you?",
    "Aspirations": "How important is each of these to you?",
}

# Each key is the exact column name expected by the trained model.
# "header" is the readable column name for the class answer sheet.
# "aliases" lists extra accepted spellings for a code (optional).
QUESTIONS = {
    "MSPSS_3": {
        "section": "Family support",
        "question": "My family really tries to help me",
        "header": "Family tries to help",
        "options": SUPPORT_OPTIONS,
        "aliases": SUPPORT_ALIASES,
    },
    "MSPSS_4": {
        "section": "Family support",
        "question": "I get the emotional help and support I need from my family",
        "header": "Family emotional support",
        "options": SUPPORT_OPTIONS,
        "aliases": SUPPORT_ALIASES,
    },
    "MSPSS_8": {
        "section": "Family support",
        "question": "I can talk about my problems with my family",
        "header": "Can talk with family",
        "options": SUPPORT_OPTIONS,
        "aliases": SUPPORT_ALIASES,
    },
    "MSPSS_11": {
        "section": "Family support",
        "question": "My family is willing to help me make decisions",
        "header": "Family helps with decisions",
        "options": SUPPORT_OPTIONS,
        "aliases": SUPPORT_ALIASES,
    },
    "FSS_1": {
        "section": "Financial strain",
        "question": "Do you have serious financial worries?",
        "header": "Serious financial worries",
        "options": FINANCE_OPTIONS,
    },
    "FSS_2": {
        "section": "Financial strain",
        "question": "Are you unable to do the things you like because of shortages of money?",
        "header": "Money limits things you like",
        "options": FINANCE_OPTIONS,
    },
    "FSS_3": {
        "section": "Financial strain",
        "question": "Are you unable to do the things you need because of shortages of money?",
        "header": "Money limits things you need",
        "options": FINANCE_OPTIONS,
    },
    "FSS_4": {
        "section": "Financial strain",
        "question": "Are you unable to manage the money you have?",
        "header": "Difficulty managing money",
        "options": FINANCE_OPTIONS,
    },
    "AI_1": {
        "section": "Aspirations",
        "question": "To be rich",
        "header": "Importance of being rich",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_2": {
        "section": "Aspirations",
        "question": "To be famous",
        "header": "Importance of being famous",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_3": {
        "section": "Aspirations",
        "question": "To have good friends that I can count on",
        "header": "Importance of dependable friends",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_4": {
        "section": "Aspirations",
        "question": "To be physically healthy",
        "header": "Importance of physical health",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_5": {
        "section": "Aspirations",
        "question": "To work to make the world a better place",
        "header": "Importance of improving the world",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_6": {
        "section": "Aspirations",
        "question": "To be admired by many people",
        "header": "Importance of being admired",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_7": {
        "section": "Aspirations",
        "question": "To share my life with someone I love",
        "header": "Importance of sharing life with loved one",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_8": {
        "section": "Aspirations",
        "question": "To have many people often comment about how attractive I look",
        "header": "Importance of appearance compliments",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_9": {
        "section": "Aspirations",
        "question": "To keep up with fashions in hair and clothing",
        "header": "Importance of keeping up with fashion",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_10": {
        "section": "Aspirations",
        "question": "To know and accept who I really am",
        "header": "Importance of knowing yourself",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_11": {
        "section": "Aspirations",
        "question": "To feel that there are people who love me and whom I love",
        "header": "Importance of loving relationships",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_12": {
        "section": "Aspirations",
        "question": "To have enough money to buy everything I want",
        "header": "Importance of buying what you want",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_13": {
        "section": "Aspirations",
        "question": "To help people in need",
        "header": "Importance of helping others",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_14": {
        "section": "Aspirations",
        "question": "To be relatively free from sickness",
        "header": "Importance of avoiding sickness",
        "options": ASPIRATION_OPTIONS,
    },
    "AI_15": {
        "section": "Aspirations",
        "question": "To grow and learn new things",
        "header": "Importance of learning",
        "options": ASPIRATION_OPTIONS,
    },
    "Age": {
        "section": "Student information",
        "question": "How old are you?",
        "header": "Age",
        "options": {age: str(age) for age in range(13, 22)},
    },
    "Gender": {
        "section": "Student information",
        "question": "What is your gender?",
        "header": "Gender",
        "options": {1: "Female", 2: "Male"},
    },
    "Form": {
        "section": "Student information",
        "question": "Which form are you in?",
        "header": "Form",
        "options": {i: f"Form {i}" for i in range(1, 5)},
    },
    "Religion": {
        "section": "Student information",
        "question": "What is your religion or spirituality?",
        "header": "Religion or spirituality",
        "options": {
            1: "Christian Protestant",
            2: "Christian Catholic",
            3: "Muslim",
            4: "Buddhist",
            5: "Traditional African",
            6: "No religion",
            7: "Other",
        },
    },
    "Surviving_Parents": {
        "section": "Student information",
        "question": "At home, how many parents do you live with?",
        "header": "Parents living at home",
        "options": {0: "No parents", 1: "One parent", 2: "Both parents"},
        "aliases": {1: ["Single parent"]},  # codebook wording
    },
    "Parents_Dead": {
        "section": "Student information",
        "question": "Have any of your parents passed away?",
        "header": "Parents who have passed away",
        "options": {1: "Father", 2: "Mother", 3: "Both", 4: "None"},
    },
    "Fathers_Education": {
        "section": "Student information",
        "question": "What is your father's highest level of education?",
        "header": "Father's education",
        "options": EDUCATION_OPTIONS,
    },
    "Mothers_Education": {
        "section": "Student information",
        "question": "What is your mother's highest level of education?",
        "header": "Mother's education",
        "options": EDUCATION_OPTIONS,
    },
    "Co_Curricular": {
        "section": "Student information",
        "question": "Are you involved in co-curricular activities like clubs and societies?",
        "header": "Clubs and societies",
        "options": {
            1: "Not involved at all",
            2: "Quite involved",
            3: "Extremely involved",
        },
    },
    "Sports": {
        "section": "Student information",
        "question": "Are you part of a school sports team, like basketball or rugby?",
        "header": "School sports team",
        "options": {1: "No", 2: "Yes"},
    },
    # Internal name keeps the dataset's spelling because the saved model expects it.
    "Percieved_Academic_Abilities": {
        "section": "Student information",
        "question": "How would you rate your academic performance?",
        "header": "Academic performance rating",
        "options": {
            1: "Not satisfactory",
            2: "Satisfactory",
            3: "Good",
            4: "Very good",
            5: "Excellent",
        },
    },
}

# Model input order (used for scoring).
APPROVED_COLUMNS = list(QUESTIONS)

# Order and plain titles shown to counsellors (form, questionnaire, review).
DISPLAY_SECTIONS = [
    "Student information",
    "Family support",
    "Financial strain",
    "Aspirations",
]
SECTION_TITLES = {
    "Student information": "About the student",
    "Family support": "Family support",
    "Financial strain": "Money worries",
    "Aspirations": "Hopes for the future",
}

# Label shown for a blank answer; it is stored as missing, never as a code.
SKIPPED_LABEL = "Skipped"


def columns_in_section(section):
    """Model columns belonging to one section, in display order."""
    return [col for col, item in QUESTIONS.items() if item["section"] == section]


# Catch an accidental addition, deletion, or repeated header early.
assert len(APPROVED_COLUMNS) == 34
assert len({item["header"] for item in QUESTIONS.values()}) == 34
assert set(DISPLAY_SECTIONS) == {item["section"] for item in QUESTIONS.values()}
