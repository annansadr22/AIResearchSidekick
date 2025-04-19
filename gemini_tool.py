import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")  # you can try 1.5-pro too

def gemini_summarize(text):
    response = model.generate_content(text)
    return response.text
