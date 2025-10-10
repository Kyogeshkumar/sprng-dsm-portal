from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import date
from ...database import get_db
from ...crud import create_report, get_reports, get_dsm_summary
from ...models import ReportRequest
from ...auth import get_current_user
from ...utils.email import send_daily_report
from ...utils.dsm_calc import calculate_dsm  # For summaries

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/daily/{target_date}")
def get_daily_report(target_date: date, site_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Generate daily DSM report (JSON + optional PDF/Excel export).
    """
    summaries = []
    if site_id:
        summaries = get_dsm_summary(db, site_id, target_date)
    else:
        # All sites; aggregate (expand query)
        pass
    
    if not summaries:
        raise HTTPException(404, "No data for date")
    
    # JSON data for charts
    json_data = {"date": target_date, "blocks": [{"block_no": s.block_no, "payable": s.dsm_payable, "receivable": s.dsm_receivable} for s in summaries]}
    report = create_report(db, site_id, 'daily', str(target_date), json_data)
    
    # PDF Export (simple)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"Daily DSM Report - {target_date}")
    y = 700
    for s in summaries:
        p.drawString(100, y, f"Block {s.block_no}: Payable INR {s.dsm_payable}, Receivable INR {s.dsm_receivable}")
        y -= 20
    p.save()
    buffer.seek(0)
    pdf_base64 = base64.b64encode(buffer.read()).decode()
    
    # Excel Export (via pandas)
    df = pd.DataFrame(json_data["blocks"])
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    excel_base64 = base64.b64encode(excel_buffer.read()).decode()
    
    return {
        "report_id": report.report_id,
        "json_data": json_data,
        "pdf_export": pdf_base64,
        "excel_export": excel_base64
    }

@router.get("/monthly/{month}")  # e.g., month='2025-10'
def get_monthly_report(month: str, site_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Monthly consolidated report (aggregate DSM).
    """
    # Parse month to dates (simplified)
    year, mon = map(int, month.split('-'))
    # Fetch all days in month, sum DSM
    total_payable = 0.0
    total_receivable = 0.0
    # Loop days (use calendar module for full)
    for day in range(1, 32):  # Rough
        try:
            d = date(year, mon, day)
            summaries = get_dsm_summary(db, site_id, d) if site_id else []
            total_payable += sum(s.dsm_payable for s in summaries)
            total_receivable += sum(s.dsm_receivable for s in summaries)
        except ValueError:
            continue
    
    json_data = {"month": month, "total_payable": total_payable, "total_receivable": total_receivable, "net": total_receivable - total_payable}
    report = create_report(db, site_id, 'monthly', month, json_data)
    return {"report_id": report.report_id, "data": json_data}

@router.post("/email")
def email_report(report_type: str, period: str, to_email: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Auto-email report (e.g., daily at 6 AM via scheduler).
    """
    # Generate content (call get_daily_report etc.)
    content = f"<h1>{report_type.capitalize()} Report for {period}</h1><p>Summary: Check attachment.</p>"  # HTML
    success = send_daily_report(to_email, f"{report_type} DSM Report - {period}", content, attachment_path=None)  # Add PDF path in prod
    if success:
        return {"message": "Report emailed successfully"}
    raise HTTPException(500, "Email failed")
