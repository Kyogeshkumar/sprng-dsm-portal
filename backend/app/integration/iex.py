import requests
import os
from datetime import date
from ...models import MarketPriceBlock
from ...crud import create_or_update_market
from ...database import get_db
from sqlalchemy.orm import Session

IEX_API_KEY = os.getenv("IEX_API_KEY", "your_iex_api_key_here")  # Get from posoco.in or IEX India

def fetch_dam_prices(target_date: date, db: Session = None) -> list[MarketPriceBlock]:
    """
    Fetch Day-Ahead Market (DAM) prices from IEX API for a date (96 blocks).
    Stores in DB if session provided. Returns list of blocks.
    Note: IEX API may require registration; this uses a placeholder endpoint.
    """
    # Real IEX endpoint example (adapt to official API; may need auth)
    url = f"https://api.iexindia.in/v1/market-data/day-ahead/{target_date.strftime('%Y-%m-%d')}?apikey={IEX_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Assume API returns hourly; interpolate to 15-min blocks (simplified)
            blocks = []
            for hour in range(24):
                price = data.get(f"hour_{hour+1}", 3.0)  # Default 3 INR/kWh
                for block_offset in range(4):  # 4 x 15-min per hour
                    block_no = hour * 4 + block_offset + 1
                    if 1 <= block_no <= 96:
                        create_or_update_market(db, target_date, block_no, dam_price=price) if db else None
                        blocks.append(MarketPriceBlock(block_no=block_no, dam_price=price))
            return blocks
        else:
            # Fallback: Mock data for testing
            return [MarketPriceBlock(block_no=i, dam_price=3.0 + i*0.1) for i in range(1, 97)]
    except Exception as e:
        print(f"IEX API error: {e}")
        # Fallback mock
        return [MarketPriceBlock(block_no=i, dam_price=3.0) for i in range(1, 97)]
