from sqlalchemy import Column, Integer, String, Float, Date, Enum as SQLEnum, ForeignKey, DateTime, JSON, Text, Boolean
from sqlalchemy.sql import func
from .database import Base

# Users
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum('admin', 'operator', 'engineer', name='roles'), default='operator', nullable=False)
    created_at = Column(DateTime, default=func.now())

# Sites
class Site(Base):
    __tablename__ = "sites"
    site_id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String(100), nullable=False)
    capacity_mw = Column(Float, nullable=False)
    region = Column(String(50))
    state = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=func.now())

# Schedules
class Schedule(Base):
    __tablename__ = "schedules"
    schedule_id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    block_no = Column(Integer, nullable=False)  # 1-96
    scheduled_mw = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

# Generations
class Generation(Base):
    __tablename__ = "generations"
    generation_id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    block_no = Column(Integer, nullable=False)
    actual_mw = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

# Deviations
class Deviation(Base):
    __tablename__ = "deviations"
    deviation_id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    block_no = Column(Integer, nullable=False)
    deviation_percent = Column(Float)
    penalty_band = Column(SQLEnum('none', 'partial', 'full', name='penalty_bands'))
    created_at = Column(DateTime, default=func.now())

# DSM Settlements
class DsmSettlement(Base):
    __tablename__ = "dsm_settlements"
    dsm_id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    block_no = Column(Integer, nullable=False)
    dsm_payable = Column(Float, default=0.0)
    dsm_receivable = Column(Float, default=0.0)
    market_price = Column(Float)
    created_at = Column(DateTime, default=func.now())

# Market Prices
class MarketPrice(Base):
    __tablename__ = "market_prices"
    market_id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    block_no = Column(Integer, nullable=False)
    dam_price = Column(Float)
    rtm_price = Column(Float)
    created_at = Column(DateTime, default=func.now())

# Weather Data
class WeatherData(Base):
    __tablename__ = "weather_data"
    weather_id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    block_no = Column(Integer, nullable=False)
    irradiance = Column(Float)
    temp = Column(Float)
    wind_speed = Column(Float)
    cloud_cover = Column(Integer)
    created_at = Column(DateTime, default=func.now())

# Reports
class Report(Base):
    __tablename__ = "reports"
    report_id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.site_id"))
    report_type = Column(SQLEnum('daily', 'weekly', 'monthly', 'consolidated', name='report_types'))
    period = Column(String(50))
    json_data = Column(JSON)
    created_at = Column(DateTime, default=func.now())

# Audit Logs
class AuditLog(Base):
    __tablename__ = "audit_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action = Column(String(100), nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, default=func.now())

# AI Memory
class AiMemory(Base):
    __tablename__ = "ai_memory"
    memory_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    context = Column(JSON)
    response = Column(Text)
    timestamp = Column(DateTime, default=func.now())
