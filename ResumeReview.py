import os
from LLM import generateLLMResopnse

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
