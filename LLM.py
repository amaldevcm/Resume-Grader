import os
from groq import Groq
import json


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))           # Get groq client

def generateLLMResopnse(prompt):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-20b",  # Or your desired Groq model
        )
        generated_content = chat_completion.choices[0].message.content
        print(generated_content)
        return format_ouput(generated_content)
    except Exception as e:
        return "Error"
    

def format_ouput(data):
    try:
        data = data.strip()

        if data.startswith("```json"):
            data = data[7:]  
        if data.endswith("```"):
            data = data[:-3] 

        # Try parsing JSON
        return json.loads(data)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}")