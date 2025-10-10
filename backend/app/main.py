from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine, Base, get_db
from .api import auth, sites, schedule, generation, deviation, market, weather_api, reports, ai, revenue  # Import all routers
from sqlalchemy.orm import Session
import os

# Create all tables on startup (use migrations in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SPRNG DSM Portal API", version="1.0.0", description="Unified DSM Automation for SPRNG Energy")

# CORS for frontend (update origins for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],  # Add your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (prefix /api already in each router file)
app.include_router(auth.router)
app.include_router(sites.router)
app.include_router(schedule.router)
app.include_router(generation.router)
app.include_router(deviation.router)
app.include_router(market.router)
app.include_router(weather_api.router)
app.include_router(reports.router)
app.include_router(ai.router)
app.include_router(revenue.router)

@app.get("/")
def root():
    return {"message": "SPRNG DSM Portal API - Ready for DSM Automation"}

@app.on_event("startup")
async def startup_event():
    # Optional: Init scheduler or fetch market data
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
