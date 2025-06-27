from flask import Flask, render_template, request
import os
import re

# === Flask App Setup ===
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# === Routes ===

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    # Get uploaded file and job description
    resume = request.files['resume']
    job_desc = request.form['jobdesc']

    # Save the uploaded resume file
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
    resume.save(resume_path)

    # Extract text from resume
    resume_text = extract_text(resume_path).lower()

    # Split into words (word tokens) for clean matching
    resume_words = set(re.findall(r'\b\w+\b', resume_text))
    job_keywords = set(job_desc.lower().split())

    # Match logic
    matched_keywords = [word for word in job_keywords if word in resume_words]
    missing_keywords = [word for word in job_keywords if word not in resume_words]
    match_score = round((len(matched_keywords) / len(job_keywords)) * 100, 2)

    return render_template(
        'result.html',
        score=match_score,
        matched=matched_keywords,
        missing=missing_keywords,
        resume_text=resume_text
    )


# === Resume Text Extractor ===
def extract_text(path):
    text = ""
    try:
        if path.endswith('.pdf'):
            import PyPDF2
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text

        elif path.endswith('.docx'):
            import docx
            doc = docx.Document(path)
            for para in doc.paragraphs:
                text += para.text + '\n'

        elif path.endswith('.txt'):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        else:
            text = "Unsupported file format."

    except Exception as e:
        text = f"Error reading file: {e}"

    return text.lower()


if __name__ == '__main__':
    app.run(debug=True)
