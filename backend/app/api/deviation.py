from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from ...database import get_db
from ...crud import calculate_and_store_deviation, get_dsm_summary
