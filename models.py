from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ResearchPaper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    introduction = Column(Text)
    conclusion = Column(Text)
    full_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
