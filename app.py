from flask import Flask, render_template, request
import os
import pdfplumber
import re
import spacy

app = Flask(__name__)

# Ensure 'en_core_web_sm' model is available
MODEL_NAME = "en_core_web_sm"

try:
    nlp = spacy.load(MODEL_NAME)
except OSError:
    import spacy.cli
    spacy.cli.download(MODEL_NAME)
    nlp = spacy.load(MODEL_NAME)

# Folder for uploaded resumes
UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Job description (Modify as needed)
job_description = """
We are looking for a Software Engineer with experience in Python, Java, Machine Learning, and SQL.
The candidate should also be familiar with AI and Data Science concepts.
"""

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

# Function to extract email
def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group() if match else None

# Function to extract phone number
def extract_phone_number(text):
    match = re.search(r"\+?\d{10,13}", text)
    return match.group() if match else None

# Function to extract name using NLP
def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

# Function to extract skills
def extract_skills(text):
    skills = ["Java", "Python", "AI", "Machine Learning", "Data Science", "C++", "SQL"]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]
    return found_skills

# Function to match resume skills with job description
def match_skills(resume_skills, job_description):
    job_skills = extract_skills(job_description)
    matched = set(resume_skills) & set(job_skills)
    match_percentage = (len(matched) / len(job_skills)) * 100 if job_skills else 0
    return matched, round(match_percentage, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    candidates = []

    if request.method == "POST":
        # Get uploaded files
        files = request.files.getlist("resumes")

        for file in files:
            if file.filename.endswith(".pdf"):
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(file_path)

                extracted_text = extract_text_from_pdf(file_path)
                name = extract_name(extracted_text)
                email = extract_email(extracted_text)
                phone = extract_phone_number(extracted_text)
                resume_skills = extract_skills(extracted_text)

                matched_skills, match_score = match_skills(resume_skills, job_description)

                candidates.append({
                    "Name": name if name else "Unknown",
                    "Email": email if email else "Not Found",
                    "Phone": phone if phone else "Not Found",
                    "Matched Skills": ", ".join(matched_skills),
                    "Match Score": match_score
                })

        # Sort candidates by match score
        candidates.sort(key=lambda x: x["Match Score"], reverse=True)

    return render_template("index.html", candidates=candidates)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
