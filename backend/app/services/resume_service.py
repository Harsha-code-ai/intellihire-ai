import pdfplumber

skills_list = [
    "python",
    "java",
    "machine learning",
    "fastapi",
    "sql",
    "react",
    "docker"
]


def extract_text_from_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    return text.lower()


def analyze_resume(text):

    found_skills = []
    missing_skills = []

    for skill in skills_list:

        if skill in text:
            found_skills.append(skill)

        else:
            missing_skills.append(skill)

    total = len(skills_list)

    score = int((len(found_skills) / total) * 100)

    if score > 70:
        suggestion = "Your resume matches the role well."

    elif score > 40:
        suggestion = "Improve by adding more backend and dev skills."

    else:
        suggestion = "You need to add more relevant technical skills."

    return {
        "skills_found": found_skills,
        "missing_skills": missing_skills,
        "role_match_percentage": score,
        "suggestions": suggestion
    }