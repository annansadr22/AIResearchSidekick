import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import google.generativeai as genai

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic input model
class PaperConfig(BaseModel):
    topic: str
    keywords: List[str]
    audience: str
    tone: str
    pageLength: dict
    citationStyle: str
    outputFormat: str

# Serper API search
def search_with_serper(query: str) -> str:
    res = requests.post(
        "https://google.serper.dev/search",
        json={"q": query},
        headers={"X-API-KEY": SERPER_API_KEY}
    )
    data = res.json()
    snippets = [r["title"] + "\n" + r.get("snippet", "") for r in data.get("organic", [])]
    return "\n\n".join(snippets)

# Gemini summary
def summarize_with_gemini(context: str, topic: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = f"Write an academic research paper on the topic '{topic}'. Use the following sources:\n\n{context}"
    response = model.generate_content(prompt)
    return response.text

# /generate endpoint
@app.post("/generate")
async def generate(config: PaperConfig):
    query = config.topic + " " + " ".join(config.keywords)
    search_results = search_with_serper(query)
    paper = summarize_with_gemini(search_results, config.topic)
    return {
        "title": f"{config.topic} - AI Generated",
        "abstract": paper[:500],
        "introduction": paper[:800],
        "conclusion": paper[-800:],
        "sections": [{"title": "Generated", "content": paper}],
        "references": []
    }
