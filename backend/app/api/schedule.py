from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from datetime import date
from ...database import get_db
from ...crud import upload_schedule
from ...models import ScheduleUpload
from ...auth import get_current_user

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.post("/upload")
def upload_schedule_file(file: UploadFile = File(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.xlsx', '.xls', '.json')):
        raise HTTPException(400, "Only Excel or JSON allowed")
    
    content = file.file.read()
    try:
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(BytesIO(content))
        else:  # JSON
            df = pd.read_json(BytesIO(content))
        
        # Validate: 96 rows, required columns
        if len(df) != 96:
            raise HTTPException(400, "Must have exactly 96 blocks")
        required_cols = ['site_id', 'date', 'block_no', 'scheduled_mw']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(400, "Missing columns: site_id, date, block_no, scheduled_mw")
        if not all(1 <= b <= 96 for b in df['block_no']):
            raise HTTPException(400, "Block numbers must be 1-96")
        
        # Parse to model
        upload_data = ScheduleUpload(
            site_id=int(df['site_id'].iloc[0]),
            date=pd.to_datetime(df['date'].iloc[0]).date(),
            blocks=[{"block_no": int(row['block_no']), "scheduled_mw": float(row['scheduled_mw'])} for _, row in df.iterrows()]
        )
        upload_schedule(db, upload_data, current_user.user_id)
        return {"message": "Schedule uploaded successfully", "blocks": 96}
    except Exception as e:
        raise HTTPException(400, f"Upload error: {str(e)}")

@router.get("/{site_id}/{target_date}")
def get_schedule_detail(site_id: int, target_date: date, db: Session = Depends(get_db)):
    return {"blocks": get_schedule(db, site_id, target_date)}  # From crud

@router.put("/update")
def update_schedule(upload: ScheduleUpload, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    upload_schedule(db, upload, current_user.user_id)
    return {"message": "Schedule updated"}
