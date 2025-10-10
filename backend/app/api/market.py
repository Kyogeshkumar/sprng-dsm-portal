from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from ...database import get_db
from ...crud import get_market_prices, upload_market
from ...models import MarketUpload
from ...auth import get_current_user, require_role
from ...integrations.iex import fetch_dam_prices

router = APIRouter(prefix="/market", tags=["market"])

@router.get("/dam/{target_date}")
def get_dam_prices(target_date: date, db: Session = Depends(get_db)):
    """
    Get DAM prices for date (auto-fetches from IEX if missing).
    """
    fetch_dam_prices(target_date, db)  # Ensure data
    prices = get_market_prices(db, target_date)
    return {"date": target_date, "blocks": [{"block_no": p.block_no, "dam_price": p.dam_price, "rtm_price": p.rtm_price} for p in prices]}

@router.get("/rtm/{target_date}")
def get_rtm_prices(target_date: date, db: Session = Depends(get_db)):
    """
    Get RTM prices (similar; mock if no API).
    """
    # Similar to DAM; use same fetch or separate RTM endpoint
    return get_dam_prices(target_date, db)  # Placeholder; adapt for RTM

@router.post("/update")
def update_market_prices(upload: MarketUpload, current_user = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """
    Manual override for prices (e.g., testing).
    """
    upload_market(db, upload, current_user.user_id)
    return {"message": "Market prices updated", "blocks": len(upload.blocks)}
