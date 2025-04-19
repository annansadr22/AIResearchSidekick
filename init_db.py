from db import engine, SessionLocal
from models import Base, ResearchPaper, User

# Drop papers table if it exists (manual migration workaround)
ResearchPaper.__table__.drop(engine)  # ← DANGEROUS: use only if you're okay losing `papers`

# Recreate tables
Base.metadata.create_all(bind=engine)

# Optional test insert
db = SessionLocal()

# Add a user if needed
test_user = db.query(User).filter(User.email == "testuser@example.com").first()
if not test_user:
    test_user = User(email="testuser@example.com", password="password123")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

# Add a test paper
test_paper = ResearchPaper(
    user_id=test_user.id,
    title="AI in Research: Test Paper",
    abstract="Sample abstract",
    introduction="Sample intro",
    conclusion="Sample conclusion",
    full_text="Full text of the paper..."
)
db.add(test_paper)
db.commit()
db.close()

print("✅ Dropped & recreated papers table with correct column type.")
