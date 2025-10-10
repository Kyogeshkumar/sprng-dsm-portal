from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from datetime import date
from ...database import get_db
from ...crud import upload_generation
from ...models import GenerationUpload
from ...auth import get_current_user

router = APIRouter(prefix="/generation", tags=["generation"])

@router.post("/upload")
def upload_generation_file(file: UploadFile = File(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.xlsx', '.xls', '.json')):
        raise HTTPException(400, "Only Excel or JSON allowed")
    
    content = file.file.read()
    try:
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(BytesIO(content))
        else:
            df = pd.read_json(BytesIO(content))
        
        if len(df) != 96:
            raise HTTPException(400, "Must have exactly 96 blocks")
        required_cols = ['site_id', 'date', 'block_no', 'actual_mw']  # Note: actual_mw
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(400, "Missing columns: site_id, date, block_no, actual_mw")
        if not all(1 <= b <= 96 for b in df['block_no']):
            raise HTTPException(400, "Block numbers must be 1-96")
        
        upload_data = GenerationUpload(
            site_id=int(df['site_id'].iloc[0]),
            date=pd.to_datetime(df['date'].iloc[0]).date(),
            blocks=[{"block_no": int(row['block_no']), "scheduled_mw": float(row['actual_mw'])} for _, row in df.iterrows()]  # Map to model
        )
        upload_generation(db, upload_data, current_user.user_id)
        # Auto-trigger DSM calc after upload
        for block in upload_data.blocks:
            from ...crud import calculate_and_store_deviation
            calculate_and_store_deviation(db, upload_data.site_id, upload_data.date, block.block_no, current_user.user_id)
        return {"message": "Generation uploaded and DSM calculated", "blocks": 96}
    except Exception as e:
        raise HTTPException(400, f"Upload error: {str(e)}")

@router.get("/{site_id}/{target_date}")
def get_generation_detail(site_id: int, target_date: date, db: Session = Depends(get_db)):
    return {"blocks": get_generation(db, site_id, target_date)}

@router.get("/summary/{site_id}/{target_date}")
def get_summary(site_id: int, target_date: date, db: Session = Depends(get_db)):
    gens = get_generation(db, site_id, target_date)
    return {"total_actual": sum(g.actual_mw for g in gens), "avg_mw": sum(g.actual_mw for g in gens) / len(gens) if gens else 0}
