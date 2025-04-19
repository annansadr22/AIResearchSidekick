
from db import SessionLocal
from models import ResearchPaper

db = SessionLocal()
papers = db.query(ResearchPaper).all()

for paper in papers:
    print(f"🧠 ID: {paper.id}")
    print(f"📄 Title: {paper.title}")
    print(f"🧾 Abstract: {paper.abstract}")
    print(f"🕒 Created at: {paper.created_at}")
    print("-----------")
