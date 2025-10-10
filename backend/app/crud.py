from sqlalchemy.orm import Session
from sqlalchemy import and_
from .schemas import User, Site, Schedule, Generation, Deviation, DsmSettlement, MarketPrice, WeatherData, Report, AuditLog, AiMemory
from .models import UserCreate, SiteCreate, ScheduleUpload, GenerationUpload
from .auth import get_password_hash
from .utils.audit import log_action  # Circular? Import at bottom if needed

# Users
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(name=user.name, email=user.email, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    log_action(db, db_user.user_id, "create_user", {"email": user.email})  # Audit
    return db_user

# Sites
def get_sites(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Site).offset(skip).limit(limit).all()

def create_site(db: Session, site: SiteCreate, user_id: int) -> Site:
    db_site = Site(**site.dict())
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    log_action(db, user_id, "create_site", {"site_id": db_site.site_id})
    return db_site

def get_site(db: Session, site_id: int) -> Site:
    return db.query(Site).filter(Site.site_id == site_id).first()

# Schedules
def create_or_update_schedule(db: Session, site_id: int, date: date, block_no: int, scheduled_mw: float, user_id: int):
    existing = db.query(Schedule).filter(and_(Schedule.site_id == site_id, Schedule.date == date, Schedule.block_no == block_no)).first()
    if existing:
        existing.scheduled_mw = scheduled_mw
    else:
        db_schedule = Schedule(site_id=site_id, date=date, block_no=block_no, scheduled_mw=scheduled_mw)
        db.add(db_schedule)
    db.commit()
    log_action(db, user_id, "update_schedule", {"site_id": site_id, "date": date, "block_no": block_no})

def get_schedule(db: Session, site_id: int, date: date):
    return db.query(Schedule).filter(and_(Schedule.site_id == site_id, Schedule.date == date)).all()

def upload_schedule(db: Session, upload: ScheduleUpload, user_id: int):
    for block in upload.blocks:
        if not 1 <= block.block_no <= 96:
            raise ValueError("Block number must be 1-96")
        create_or_update_schedule(db, upload.site_id, upload.date, block.block_no, block.scheduled_mw, user_id)
    log_action(db, user_id, "upload_schedule", {"site_id": upload.site_id, "date": upload.date})

# Generations (similar to schedules)
def create_or_update_generation(db: Session, site_id: int, date: date, block_no: int, actual_mw: float, user_id: int):
    existing = db.query(Generation).filter(and_(Generation.site_id == site_id, Generation.date == date, Generation.block_no == block_no)).first()
    if existing:
        existing.actual_mw = actual_mw
    else:
        db_gen = Generation(site_id=site_id, date=date, block_no=block_no, actual_mw=actual_mw)
        db.add(db_gen)
    db.commit()

def upload_generation(db: Session, upload: GenerationUpload, user_id: int):
    for block in upload.blocks:
        if not 1 <= block.block_no <= 96:
            raise ValueError("Block number must be 1-96")
        create_or
