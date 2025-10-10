from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...crud import create_site, get_sites, get_site, update_site
from ...models import SiteCreate, Site
from ...auth import get_current_user, require_role

router = APIRouter(prefix="/sites", tags=["sites"])

@router.post("/", response_model=Site)
def add_site(site: SiteCreate, current_user = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return create_site(db, site, current_user.user_id)

@router.get("/", response_model=list[Site])
def list_sites(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_sites(db, skip, limit)

@router.get("/{site_id}", response_model=Site)
def get_site_detail(site_id: int, db: Session = Depends(get_db)):
    site = get_site(db, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.put("/{site_id}", response_model=Site)
def edit_site(site_id: int, site: SiteCreate, current_user = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return update_site(db, site_id, site, current_user.user_id)
