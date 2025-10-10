# SPRNG DSM Portal - Deployment & Setup Guide

This is the unified DSM Automation Web Portal for SPRNG Energy. It merges RE50Hertz (scheduling), Reconnect (DSM calc), and Regent (analytics/weather) with AI and CERC compliance.

## Quick Start (Local Testing - Optional)
- **DB**: Install PostgreSQL locally (or use Supabase). Run `db/schema.sql` then `db/seed.sql`.
- **Backend**: `cd backend`, copy `.env.example` to `.env` (fill API keys), `pip install -r requirements.txt`, `python run.py` (runs on http://localhost:8000).
- **Frontend**: `cd frontend`, copy `.env.local.example` to `.env.local` (set API_URL to backend), `npm install`, `npm run dev` (runs on http://localhost:3000).
- Test: Login at frontend, upload sample data from `/templates/`.

## Production Deployment

### Backend (FastAPI API) - Deploy to Render (Free Tier)
1. Go to [render.com](https://render.com) and sign up (use GitHub login).
2. Click **New** → **Web Service**.
3. Connect your GitHub repo (`sprng-dsm-portal`).
4. Settings:
   - **Name**: `sprng-dsm-backend`.
   - **Runtime**: Python 3.
   - **Region**: Closest to you (e.g., Oregon for India).
   - **Branch**: `main`.
   - **Build Command**: `pip install -r backend/requirements.txt`.
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. **Environment Variables** (click "Add Environment Variable"):
   - `DATABASE_URL`: Paste from Supabase (see DB section below).
   - `SECRET_KEY`: `your-super-secret-jwt-key-change-this` (generate a strong one, e.g., via [randomkeygen.com](https://randomkeygen.com)).
   - `IEX_API_KEY`: Get free from [posoco.in](https://posoco.in) or IEX India API (register for market data access).
   - `OPENWEATHER_API_KEY`: Free from [openweathermap.org](https://openweathermap.org/api) → Sign up → API Keys.
   - `GEMINI_API_KEY`: Free from [aistudio.google.com](https://aistudio.google.com/app/apikey) → Create API key.
   - `SENDGRID_API_KEY`: Free from [sendgrid.com](https://sendgrid.com) → Sign up → API Keys (for emails).
6. Click **Create Web Service**. Render builds/deploys (~5-10 mins). Live URL: `https://sprng-dsm-backend.onrender.com`.
7. Test: Visit `/docs` (Swagger UI) → Try POST /auth/login (email: admin@sprngenergy.com, pass: from seed.sql).

### Database (PostgreSQL) - Deploy to Supabase (Free Tier)
See detailed guide below.

### Frontend (Next.js) - Deploy to Vercel (Free Tier)
1. Go to [vercel.com](https://vercel.com) → Sign up (GitHub login).
2. **New Project** → Import repo (`sprng-dsm-portal`).
3. Settings:
   - Framework: Next.js (auto-detected).
   - Root Directory: `frontend`.
   - Build Command: `npm install && npm run build`.
   - Output Directory: `.next`.
4. **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: `https://sprng-dsm-backend.onrender.com/api` (your Render URL).
5. Deploy (~2 mins). Live URL: `https://sprng-dsm-portal-frontend.vercel.app`.
6. Test: Login, upload data, view DSM charts.

## API Testing (Postman)
Use `/docs/postman_collection.json` in Postman:
1. Download Postman (free: [postman.com](https://postman.com)).
2. Import the JSON file.
3. Set base URL to your Render URL (e.g., `https://sprng-dsm-backend.onrender.com`).
4. Test endpoints: Auth → Uploads → DSM Calc.

## Sample Data Uploads
Use `/templates/` files:
- `schedule_sample.xlsx`: Day-ahead schedule (96 rows).
- `generation_sample.json`: Actual generation (96 blocks).

## Troubleshooting
- **DB Connection Error**: Check DATABASE_URL format (postgresql://user:pass@host:port/dbname).
- **API Keys**: All free tiers have limits (e.g., 100 calls/day for OpenWeather).
- **CORS Issues**: Update `app/main.py` allow_origins with your Vercel URL.
- **Logs**: Render/Supabase dashboards show errors.
- **Scaling**: Free tiers sleep after inactivity; upgrade for $5/month.

## CERC Compliance
- DSM calc in `app/utils/dsm_calc.py`: 0-15% no penalty, 15-20% 50%, >20% 100%.
- Audit logs for all actions.

Questions? Check repo issues or contact.
