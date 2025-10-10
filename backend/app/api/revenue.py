from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...crud import get_revenue_summary
from ...models import RevenueSummary
from ...auth import get_current_user

router = APIRouter(prefix="/revenue", tags=["revenue"])

@router.get("/summary/{site_id}/{month}", response_model=RevenueSummary)
def get_revenue_analysis(site_id: int, month: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Financial summary: DSM loss/gain, scenarios (with/without DSM).
    Month e.g., '2025-10'.
    """
    summary = get_revenue_summary(db, site_id, month)
    return RevenueSummary(**summary)
