import google.generativeai as genai
import os
from datetime import date
from ...models import AIQuery, AIResponse
from ...crud import create_ai_memory, get_ai_memory, get_dsm_summary, get_site  # Etc. for data grounding
from ...database import get_db
from sqlalchemy.orm import Session

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "your_gemini_api_key"))
model = genai.GenerativeModel('gemini-1.5-flash')  # Or 'gemini-pro'

def process_ai_query(db: Session, user_id: int, query_obj: AIQuery) -> AIResponse:
    """
    Process natural language query using Gemini, grounded in DB data (e.g., DSM reports).
    Maintains memory by fetching recent context and appending to prompt.
    Examples: "Show DSM for REWA on 2025-10-07" -> Fetches and summarizes.
    """
    # Fetch memory context
    recent_memory = get_ai_memory(db, user_id, limit=3)
    context_str = "\n".join([f"Q: {m.query}\nA: {m.response}" for m in recent_memory]) if recent_memory else ""
    
    # Ground prompt with data (parse query for intent, e.g., site/date)
    prompt = f"""
    You are a DSM expert for SPRNG Energy. Use CERC rules. Ground responses in provided data.
    Recent conversation: {context_str}
    
    User query: {query_obj.query}
    
    Available data examples:
    - Sites: REWA Solar (50MW, Madhya Pradesh)
    - DSM Summary: For a site/date, compute deviation/penalty.
    
    If query asks for report: e.g., "DSM for REWA 2025-10-07" -> "Deviation 5%, Payable INR 1000".
    If predictive: "Predict tomorrow's penalty" -> Use trends/weather.
    Keep responses concise, actionable.
    """
    
    try:
        # Query Gemini
        response = model.generate_content(prompt)
        ai_text = response.text if response.text else "Sorry, could not process query."
        
        # Store memory
        create_ai_memory(db, user_id, query_obj.query, ai_text, {"context": context_str})
        
        # Update context for next (simple last response)
        new_context = ai_text[:200]  # Truncate
        
        return AIResponse(response=ai_text, context=new_context)
    except Exception as e:
        error_msg = f"AI error: {e}. Fallback: Query logged, manual check needed."
        create_ai_memory(db, user_id, query_obj.query, error_msg)
        return AIResponse(response=error_msg, context=None)
