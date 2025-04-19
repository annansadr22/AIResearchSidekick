import os
import json
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import google.generativeai as genai
import re

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ----------------------------
# 🌍 Environment & Config
# ----------------------------
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------
# 🧠 DB Setup
# ----------------------------
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# 📟 DB Models
# ----------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class ResearchPaper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    introduction = Column(Text)
    conclusion = Column(Text)
    full_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

Base.metadata.create_all(bind=engine)

# ----------------------------
# 📝 Pydantic Schemas
# ----------------------------
class UserAuth(BaseModel):
    email: str
    password: str

class PaperConfig(BaseModel):
    topic: str
    keywords: List[str]
    audience: str
    tone: str
    pageLength: dict
    citationStyle: str
    outputFormat: str
    user_id: int

# ----------------------------
# 🚀 FastAPI App
# ----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# 🔍 Serper Search
# ----------------------------
def search_with_serper(query: str) -> str:
    res = requests.post(
        "https://google.serper.dev/search",
        json={"q": query},
        headers={"X-API-KEY": SERPER_API_KEY}
    )
    data = res.json()
    snippets = [r["title"] + "\n" + r.get("snippet", "") for r in data.get("organic", [])]
    return "\n\n".join(snippets)

# ----------------------------
# 🧠 Gemini Summary
# ----------------------------
def extract_json_from_backticks(text: str) -> str:
    # Extract JSON inside triple backticks ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        # fallback: try to extract a lone JSON object (not wrapped)
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            return match.group(1)
    return ""


def summarize_with_gemini(context: str, topic: str) -> dict:
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = f"""
You are an academic AI assistant. Write a well-structured academic paper on the topic: "{topic}"

Use the following web search context:\n\n{context}

Return ONLY a valid JSON object. Do not wrap the response in markdown, code blocks, or explain anything. The JSON should include:
- title: str
- abstract: str
- introduction: str
- sections: list of objects with "title" and "content"
- conclusion: str
- references: list of strings
"""

    try:
        response = model.generate_content(prompt)

        print("\n---- Gemini Output Start ----\n")
        print(response.text or "[Empty response]")
        print("\n---- Gemini Output End ----\n")

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        # Clean the response before parsing
        cleaned_text = extract_json_from_backticks(response.text)
        if not cleaned_text:
            raise ValueError("Failed to extract JSON from Gemini output.")

        return json.loads(cleaned_text)

    except json.JSONDecodeError as e:
        raise ValueError("❌ Invalid JSON from Gemini. Check printed output above.") from e
    except Exception as e:
        raise RuntimeError("❌ Gemini request failed.") from e


# ----------------------------
# 🔐 Signup
# ----------------------------
@app.post("/signup")
def signup(user: UserAuth, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Signup successful", "user_id": new_user.id}

# ----------------------------
# 🔐 Login
# ----------------------------
@app.post("/login")
def login(user: UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email, User.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": db_user.id}

# ----------------------------
# ✍️ Generate Paper
# ----------------------------
@app.post("/generate")
def generate(config: PaperConfig, db: Session = Depends(get_db)):
    query = config.topic + " " + " ".join(config.keywords)
    search_results = search_with_serper(query)
    parsed = summarize_with_gemini(search_results, config.topic)

    new_paper = ResearchPaper(
        user_id=config.user_id,
        title=parsed["title"],
        abstract=parsed["abstract"],
        introduction=parsed["introduction"],
        conclusion=parsed["conclusion"],
        full_text=json.dumps(parsed)
    )
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)

    return {
        "title": parsed["title"],
        "abstract": parsed["abstract"],
        "introduction": parsed["introduction"],
        "conclusion": parsed["conclusion"],
        "sections": parsed["sections"],
        "references": parsed["references"]
    }

# ----------------------------
# 📂 Get Papers for User
# ----------------------------
@app.get("/papers")
def get_papers(user_id: int = Query(...), db: Session = Depends(get_db)):
    papers = db.query(ResearchPaper).filter(ResearchPaper.user_id == user_id).order_by(ResearchPaper.created_at.desc()).all()
    return [
        {
            "id": paper.id,
            "title": paper.title,
            "abstract": paper.abstract,
            "created_at": paper.created_at
        } for paper in papers
    ]

# ----------------------------
# 🔧 Debug Endpoints
# ----------------------------
@app.get("/debug/users")
def debug_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        } for user in users
    ]

@app.get("/debug/papers")
def debug_papers(db: Session = Depends(get_db)):
    papers = db.query(ResearchPaper).all()
    return [
        {
            "id": paper.id,
            "user_id": paper.user_id,
            "title": paper.title,
            "created_at": paper.created_at
        } for paper in papers
    ]