import re
import pdfplumber
#import spacy
from rapidfuzz import process, fuzz
from functions.ai_doc_extractor import ai_resume_extractor

skills_db = ["Python", "JavaScript", "SQL", "Docker", "Kubernetes",
             "TensorFlow", "Machine Learning", "Data Analysis",
             "Leadership", "Communication", "Project Management",
             "React", "Node.js", "AWS", "Azure", "Google Cloud"]

def dictionary_skill_match(text, skills_db):
    found_skills = []
    words = text.split()
    for word in words:
        match = process.extractOne(word, skills_db, scorer=fuzz.ratio)
        if match and match[1] > 85:
            found_skills.append(match[0])
    return list(set(found_skills))

def extract_resume_data(user_id, file_path):
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # Extract email and phone
    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"(\+?\d[\d\s\-]{7,})", text)

    # EDUCATION — look for degree names or lines near 'EDUCATION'
    education_pattern = re.compile(
        r"(Bachelor|Master|BSc|MSc|PhD|Diploma|Degree)[^\n]{0,100}", re.IGNORECASE
    )
    education_matches = education_pattern.findall(text)
    education_section = re.findall(
        r"EDUCATION[\s\S]{0,400}", text, re.IGNORECASE
    )
    education_lines = []

    if education_section:
        for line in education_section[0].split("\n"):
            if any(keyword in line for keyword in ["Bachelor", "Master", "Degree", "University", "College"]):
                education_lines.append(line.strip())

    education = list(set(education_matches + education_lines))

    # EXPERIENCE — look for experience keywords or sections
    experience_pattern = re.compile(
        r"(?:Engineer|Developer|Assistant|Manager|Research|Intern|Project)[^\n]{0,100}", re.IGNORECASE
    )
    experience = experience_pattern.findall(text)

    # SKILLS — search for 'Skills' section or known patterns
    skills_section = re.findall(r"(SKILLS|TECHNICAL SKILLS)[\s\S]{0,300}", text, re.IGNORECASE)
    skills = []
    if skills_section:
        lines = skills_section[0].split("\n")
        for line in lines:
            if re.search(r"[A-Za-z]{3,}", line):
                skills.append(line.strip())

    # Result
    result = {
        "applicant_id": user_id,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "education": education,
        "experience": experience,
        "skills": skills
    }

    return result, 200

"""
#Enable Spacy and This code on a big server
# Load spaCy (small model)
nlp = spacy.load("en_core_web_sm")

# Example skills database (replace with ESCO / O*NET / LinkedIn dataset)
skills_db = [
    "Python", "JavaScript", "SQL", "Docker", "Kubernetes",
    "TensorFlow", "Machine Learning", "Data Analysis",
    "Leadership", "Communication", "Project Management",
    "React", "Node.js", "AWS", "Azure", "Google Cloud"
]

# Function: Dictionary + Fuzzy Matching
def dictionary_skill_match(text, skills_db):
    found_skills = []
    words = text.split()
    for word in words:
        match = process.extractOne(word, skills_db, scorer=fuzz.ratio)
        if match and match[1] > 85:
            found_skills.append(match[0])
    return list(set(found_skills))

# Main Resume Parser Function
def extract_resume_data(file_path):
    # Step 1: Extract text from PDF
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # Step 2: Extract entities with spaCy
    doc = nlp(text)
    
    entities = {"names": [], "orgs": [], "dates": []}
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["names"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["orgs"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)

    # Step 3: Regex for email and phone
    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"(\+?\d[\d\s\-]{7,})", text)

    # Step 4: Extract skills (only fuzzy matching now)
    skills = dictionary_skill_match(text, skills_db)

    # Step 5: Extract education and experience (simple rules)
    education = [line for line in text.split("\n") if "BSc" in line or "MSc" in line or "Degree" in line]
    experience = [line for line in text.split("\n") if "Engineer" in line or "Developer" in line]

    return {
        "name": entities["names"][0] if entities["names"] else None,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "education": education,
        "experience": experience,
        "skills": skills
    }
"""
