from flask import Flask, render_template, request, redirect, url_for, jsonify
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import os
import pdfplumber
import docx


app = Flask(__name__)

def load_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    elif ext == '.docx':
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .txt, .pdf, or .docx")

def compute_similarity(resume, job_desc):
    resume_embed = embedder.encode(resume, convert_to_tensor=True)
    jd_embed = embedder.encode(job_desc, convert_to_tensor=True)
    score = util.pytorch_cos_sim(resume_embed, jd_embed).item()
    return round(score * 100, 2)

def get_improvement_suggestions(resume, job_desc):
    prompt = f"""
You are a professional career coach.
Here is a resume:
{resume}

Here is a job description:
{job_desc}

Suggest improvements to the resume to better match the job description. Include missing skills, keyword suggestions, and better phrasing if applicable.
"""
    output = sugg_pipeline(prompt, max_new_tokens=300, do_sample=False, temperature=0.3)
    return output[0]['generated_text'].replace(prompt, '').strip()


@app.route("/", methods=['GET', "POST"])
def main():
    if(request.method == "GET"):
        return render_template('main.html', )

    resume_text = load_file("./Amal Resume.pdf")
    job_desc_text = load_file("./jobdesc.txt")

    print("\nCalculating match score...")
    score = compute_similarity(resume_text, job_desc_text)
    print(f"\nMatch Score: {score}%")

    print("\nGenerating suggestions to improve resume...")
    suggestions = get_improvement_suggestions(resume_text, job_desc_text)
    print("\n--- Suggestions ---")
    print(suggestions)


if __name__ == '__main__':
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
    
    ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}

    # Load models
    print("Loading models...")
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    sugg_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
    sugg_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
    sugg_pipeline = pipeline("text2text-generation", model=sugg_model, tokenizer=sugg_tokenizer, device=0 if torch.cuda.is_available() else -1)
