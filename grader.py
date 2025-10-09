from flask import Flask, render_template, request, redirect
import os
import pdfplumber
import docx
from groq import Groq
from dotenv import load_dotenv
import json
from customResume import generateResume
from ResumeReview import get_improvement_suggestions
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

    if(type(result) is not dict):
        return render_template('errorPage.html')
    else:
        return render_template('customDocs.html', data=json.dumps(result))


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

        if(type(results) is not dict):
            return render_template('errorPage.html')
        else:
            chart_img = plot_circular_scorecard(results['score'])
            return render_template('result.html', data=json.dumps(results), chart=chart_img)

    else:
        pass