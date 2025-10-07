from flask import Flask, render_template, request, redirect
import os
import pdfplumber
import docx
from groq import Groq
from dotenv import load_dotenv
import json
from LLM import generateLLMResopnse
from customResume import generateResume
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import io
import base64



app = Flask(__name__)
load_dotenv()
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}
resume_file_name = ""
job_file_name = ""


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

def truncate_text(text, max_words=512):
    return ' '.join(text.split()[:max_words])

def get_improvement_suggestions(resume, job_desc):
    prompt = """
You are a professional career coach. Evaluate how well the following resume aligns with the given job description.

Output only a valid JSON string using the structure below. Do not include any other text, comments, or formatting outside the JSON block.

{
  score: <integer between 0 and 100>,
  match: ["<matching_skill_1>", "<matching_skill_2>", "..."],
  missing: ["<missing_skill_1>", "<missing_skill_2>", "..."],
  suggestions: ["<concise suggestion 1>", "<concise suggestion 2>", "<concise suggestion 3>"],
  section: {
    "Education": "<brief feedback on education section>",
    "Work Experience": "<brief feedback on work experience section>",
    "Projects": "<brief feedback on projects section>",
    "Achievements": "<brief feedback on achievements section>",
  },
  comment: "<professional summary of how well the resume aligns with the job description. Be neutral, factual, and avoid exaggeration.>",
}

Rules:
- Output must be valid JSON with no trailing commas, quotation mismatches, or formatting errors.
- Do not include any explanation, header, or markdown formatting — just the JSON.
- score must reflect how well the resume fits the job (100 = perfect match).
- match and missing arrays must each contain 5 to 15 distinct, relevant skills, tools, or qualifications, clearly stated in either the resume or job description.
- suggestions, section, and comment must each be arrays of 1 to 3 concise strings.
- suggestions must be concise, specific suggestions to improve the resume for this job.
- section must be a JSON object with keys like "Education", "Work Experience", or "Projects" and values as concise feedback.
- Follow grammar and spelling rules.
- Avoid assumptions — only list what's explicitly mentioned.
- Ensure the output is properly structured for parsing.

"""
    prompt += f"""
    ### INPUTS:

    #### Resume:
    {resume}

    #### Job Description:
    {job_desc}

    """
    return generateLLMResopnse(prompt)


# Function to display score card
def plot_circular_scorecard(score):
    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")

    # Data for the pie chart
    data = [score, 100 - score]
    
    # Define colors
    score_color = '#4CAF50'  # Green
    remaining_color = '#E0E0E0'  # Light gray
    colors = [score_color, remaining_color]

    # Create the plot
    fig, ax = plt.subplots(figsize=(3, 3))
    
    # Create the outer pie/donut chart
    ax.pie(
        data, 
        colors=colors, 
        startangle=90, 
        counterclock=False, 
        wedgeprops=dict(width=0.3, edgecolor='white')
    )
    
    # Add a white circle in the center to create the "donut" effect
    center_circle = Circle((0, 0), 0.7, color='white')
    ax.add_patch(center_circle)
    
    # Display the score text in the center
    ax.text(
        0, 0, 
        f"{score}", 
        ha='center', 
        va='center', 
        fontsize=30, 
        fontweight='bold', 
        color=score_color
    )
    
    # Display "out of 100" text below the score
    ax.text(
        0, -0.25, 
        "out of 100", 
        ha='center', 
        va='center', 
        fontsize=10, 
        color='gray'
    )
    
    # Ensure the plot is a circle
    ax.axis('equal')

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.read()).decode('utf-8')

    return img_data
    
@app.route("/customize", methods=['GET'])
def customizeCV():
    
    resume = load_file(os.path.join(app.config['UPLOAD_FOLDER'], resume_file_name))
    jobDesc = load_file(os.path.join(app.config['UPLOAD_FOLDER'], job_file_name))
    result = generateResume(resume, jobDesc)
    print(json.dumps(result))
    return render_template('result.html', data=json.dumps(result))


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
        
        global resume_file_name
        global job_file_name
        resume_file_name = resume_text.filename
        job_file_name = job_desc.filename
        resume = load_file(os.path.join(app.config['UPLOAD_FOLDER'], resume_text.filename))
        jobDesc = load_file(os.path.join(app.config['UPLOAD_FOLDER'], job_desc.filename))

        results = get_improvement_suggestions(resume, jobDesc)
        print("\n--- Suggestions ---")
        print(json.dumps(results))

        if(type(results) is not dict):
            return render_template('errorPage.html')
        else:
            chart_img = plot_circular_scorecard(results['score'])
            return render_template('result.html', data=json.dumps(results), chart=chart_img)

    else:
        pass