import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

print("🤖 Gemini Assistant (type 'exit' to quit)\n")

while True:
    user_input = input("🧑 You: ")
    
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Exiting chat. See you again!")
        break

    try:
        response = model.generate_content(user_input)
        print("\n🤖 Gemini:", response.text.strip(), "\n")
    except Exception as e:
        print("⚠️ Error:", str(e))
