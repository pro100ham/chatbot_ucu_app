from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    LLM = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="messages")
