from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    operator = "operator"
    engineer = "engineer"

class PenaltyBandEnum(str, Enum):
    none = "none"
    partial = "partial"
    full = "full"

class ReportTypeEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    consolidated = "consolidated"

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.operator

class User(UserBase):
    user_id: int
    role: RoleEnum

    class Config:
        from_attributes = True

class SiteBase(BaseModel):
    site_name: str
    capacity_mw: float
    region: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SiteCreate(SiteBase):
    pass

class Site(SiteBase):
    site_id: int

    class Config:
        from_attributes = True

class ScheduleBlock(BaseModel):
    block_no: int  # 1-96
    scheduled_mw: float

class ScheduleUpload(BaseModel):
    site_id: int
    date: date
    blocks: List[ScheduleBlock]

class GenerationUpload(ScheduleUpload):
    # Reuse for actual_mw
    pass

class DeviationResponse(BaseModel):
    deviation_percent: float
    penalty_band: PenaltyBandEnum
    dsm_payable: float
    dsm_receivable: float

class DsmSettlementResponse(BaseModel):
    dsm_payable: float
    dsm_receivable: float
    market_price: float

class MarketPriceBlock(BaseModel):
    block_no: int
    dam_price: Optional[float] = None
    rtm_price: Optional[float] = None

class MarketUpload(BaseModel):
    date: date
    blocks: List[MarketPriceBlock]

class WeatherResponse(BaseModel):
    irradiance: Optional[float]
    temp: Optional[float]
    wind_speed: Optional[float]
    cloud_cover: Optional[int]

class ReportRequest(BaseModel):
    report_type: ReportTypeEnum
    period: str  # e.g., '2025-10-07' or '2025-10'

class AIQuery(BaseModel):
    query: str
    context: Optional[str] = None

class AIResponse(BaseModel):
    response: str
    context: Optional[str] = None  # For next query memory

class RevenueSummary(BaseModel):
    total_revenue: float
    dsm_loss: float
    scenarios: dict  # e.g., {"with_dsm": 10000, "without_dsm": 12000}
