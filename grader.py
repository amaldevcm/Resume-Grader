from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.utils import secure_filename
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline, AutoModelForCausalLM
import os
import pdfplumber
import docx
from groq import Groq
from dotenv import load_dotenv
import json



app = Flask(__name__)
load_dotenv()
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'uploads'
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}

# Load models
print("Loading models...")
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

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

def truncate_text(text, max_words=512):
    return ' '.join(text.split()[:max_words])

def format_ouput(data):
    pass

def get_improvement_suggestions(resume, job_desc):

    prompt = f"""
You are a professional career coach.Suggest improvements to the resume to better match the job description.
Include missing skills, keyword suggestions, and better phrasing if applicable.

Give output as:

Score: <score>/100,
Match: <array of matching skills>,
Missing: <array of missing skills>,  
Suggestions: <suggestions in python array>,
Comment: <brief comment in string format>

Resume:
{resume}

Job Description:
{job_desc}
"""
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",  # Or your desired Groq model
        )
        generated_content = chat_completion.choices[0].message.content
        
        return generated_content
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=['GET', "POST"])
def grader():
    if(request.method == "GET"):
        return render_template('main.html', )

    elif(request.method == "POST"):
        print("requested files",'resumeInput' in request.files, 'jobInput' in request.files)
        
        # check if the post request has the file part
        if 'resumeInput' not in request.files or 'jobInput' not in request.files:
            print('No file part')
            return redirect(request.url)

        resume_text = request.files['resumeInput']
        job_desc = request.files['jobInput']

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        resume_text.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_text.filename))
        job_desc.save(os.path.join(app.config['UPLOAD_FOLDER'], job_desc.filename))

        if resume_text.filename == '' or job_desc.filename == '':
            print('No selected file')
            return redirect(request.url)

        resume = load_file(os.path.join(app.config['UPLOAD_FOLDER'], resume_text.filename))
        jobDesc = load_file(os.path.join(app.config['UPLOAD_FOLDER'], job_desc.filename))

        print("\nCalculating match score...")
        score = compute_similarity(resume, jobDesc)
        # print(f"\nMatch Score: {score}%")

        print("\nGenerating suggestions to improve resume...")
        suggestions = get_improvement_suggestions(resume, jobDesc)
        print("\n--- Suggestions ---")
        print(suggestions)

        # result = {'score': score, 'suggestions': suggestions}

        return render_template('result.html', data=suggestions)

    else:
        pass