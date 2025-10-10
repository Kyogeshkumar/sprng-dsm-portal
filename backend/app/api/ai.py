from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...models import AIQuery, AIResponse
from ...auth import get_current_user
from ...integrations.ai import process_ai_query

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/query", response_model=AIResponse)
def ai_query(query_obj: AIQuery, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Natural language DSM query with persistent memory.
    E.g., POST {"query": "Show DSM for REWA on 2025-10-07", "context": "previous query"}
    """
    response = process_ai_query(db, current_user.user_id, query_obj)
    return response

@router.get("/history")
def get_ai_history(limit: int = 10, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Retrieve conversation history (persistent memory).
    """
    from ...crud import get_ai_memory
    memories = get_ai_memory(db, current_user.user_id, limit)
    return [{"query": m.query, "response": m.response, "timestamp": m.timestamp} for m in memories]
