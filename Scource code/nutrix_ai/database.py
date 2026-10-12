from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./nutrix_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)

    conversations = relationship("Conversation", back_populates="user")
    saved_items = relationship("SavedItem", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme = Column(String, default="light")
    language = Column(String, default="en")
    ui_state = Column(Text, default="{}") # JSON string for UI modifications
    
    user = relationship("User", back_populates="preferences")


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True) # in cm
    weight = Column(Float, nullable=True) # in kg
    goal = Column(String, nullable=True)
    diet_type = Column(String, nullable=True)
    
    user = relationship("User", back_populates="health_profile")


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50))
    plan_json = Column(Text, nullable=False) # The generated diet plan JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    messages = relationship("Message", back_populates="conversation")
    user = relationship("User", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")


class SavedItem(Base):
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_type = Column(String, nullable=False) # e.g., 'scanned_label', 'recipe'
    item_data = Column(Text, nullable=False) # JSON data of the item
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="saved_items")

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
