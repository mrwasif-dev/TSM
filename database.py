from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(200))
    balance = Column(Float, default=0.0)
    joined_date = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)

class Service(Base):
    __tablename__ = 'services'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price_per_1000 = Column(Float, nullable=False)  # Price in PKR
    min_order = Column(Integer, default=100)
    max_order = Column(Integer, default=10000)
    api_service_id = Column(String(100))  # ID in upstream panel
    is_active = Column(Boolean, default=True)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    service_id = Column(Integer, nullable=False)
    service_name = Column(String(200))
    link = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(50), default='pending')  # pending, processing, completed, cancelled
    api_order_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String(50))  # deposit, order_payment, refund
    method = Column(String(50))  # jazzcash, easypaisa, admin
    status = Column(String(50), default='pending')
    reference = Column(String(200))  # Transaction ID or note
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)
