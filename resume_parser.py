import os
import pdfplumber
import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Sample job description
job_description = """
We are looking for a Software Engineer with experience in Python, Java, Machine Learning, and SQL.
The candidate should also be familiar with AI and Data Science concepts.
"""

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
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

# Process all resumes in the "resumes" folder
resumes_folder = "resumes"
candidates = []

for resume_file in os.listdir(resumes_folder):
    if resume_file.endswith(".pdf"):
        resume_path = os.path.join(resumes_folder, resume_file)
        extracted_text = extract_text_from_pdf(resume_path)

        name = extract_name(extracted_text)
        email = extract_email(extracted_text)
        phone = extract_phone_number(extracted_text)
        resume_skills = extract_skills(extracted_text)

        matched_skills, match_score = match_skills(resume_skills, job_description)

        candidates.append({
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Matched Skills": ", ".join(matched_skills),
            "Match Score": match_score
        })

# Sort candidates by match score (highest first)
candidates.sort(key=lambda x: x["Match Score"], reverse=True)

# Print results
print("\nCandidate Ranking:")
for idx, candidate in enumerate(candidates, start=1):
    print(f"{idx}. {candidate['Name']} - Match Score: {candidate['Match Score']}%")
    print(f"   Email: {candidate['Email']}, Phone: {candidate['Phone']}")
    print(f"   Matched Skills: {candidate['Matched Skills']}")
    print("-" * 40)
