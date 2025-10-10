-- Database Schema for SPRNG DSM Portal
-- Run this in PostgreSQL/Supabase to create tables

-- Users & Auth
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',  -- 'admin', 'operator', 'engineer'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sites
CREATE TABLE sites (
    site_id SERIAL PRIMARY KEY,
    site_name VARCHAR(100) NOT NULL,
    capacity_mw DECIMAL(5,2) NOT NULL,
    region VARCHAR(50),
    state VARCHAR(50),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schedules (from RE50Hertz)
CREATE TABLE schedules (
    schedule_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    block_no INTEGER NOT NULL CHECK (block_no BETWEEN 1 AND 96),  -- 15-min blocks/day
    scheduled_mw DECIMAL(8,2) NOT NULL,
    UNIQUE(site_id, date, block_no),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generations (from Regent/SCADA)
CREATE TABLE generations (
    generation_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    block_no INTEGER NOT NULL CHECK (block_no BETWEEN 1 AND 96),
    actual_mw DECIMAL(8,2) NOT NULL,
    UNIQUE(site_id, date, block_no),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deviations & DSM (from Reconnect)
CREATE TABLE deviations (
    deviation_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    block_no INTEGER NOT NULL,
    deviation_percent DECIMAL(5,2),  -- (actual - scheduled)/scheduled * 100
    penalty_band VARCHAR(10)  -- 'none', 'partial', 'full'
);

CREATE TABLE dsm_settlements (
    dsm_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    block_no INTEGER NOT NULL,
    dsm_payable DECIMAL(10,2) DEFAULT 0,  -- Over-injection penalty
    dsm_receivable DECIMAL(10,2) DEFAULT 0,  -- Under-injection credit
    market_price DECIMAL(8,2),  -- From IEX
    UNIQUE(site_id, date, block_no),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market Prices (from Regent/IEX)
CREATE TABLE market_prices (
    market_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    block_no INTEGER NOT NULL CHECK (block_no BETWEEN 1 AND 96),
    dam_price DECIMAL(8,2),  -- Day-Ahead Market
    rtm_price DECIMAL(8,2),  -- Real-Time Market
    UNIQUE(date, block_no),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather (from Regent/OpenWeatherMap)
CREATE TABLE weather_data (
    weather_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    block_no INTEGER NOT NULL,
    irradiance DECIMAL(6,2),  -- W/m²
    temp DECIMAL(4,2),  -- °C
    wind_speed DECIMAL(4,2),  -- m/s
    cloud_cover INTEGER CHECK (cloud_cover BETWEEN 0 AND 100),  -- %
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id),
    report_type VARCHAR(20),  -- 'daily', 'weekly', 'monthly', 'consolidated'
    period VARCHAR(50),  -- e.g., '2025-10-07' or '2025-W40'
    json_data JSONB,  -- Store chart data, summaries
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,  -- e.g., 'upload_schedule'
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Memory
CREATE TABLE ai_memory (
    memory_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    context JSONB,  -- Previous queries/responses
    response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_schedules_site_date ON schedules(site_id, date);
CREATE INDEX idx_generations_site_date ON generations(site_id, date);
CREATE INDEX idx_deviations_site_date ON deviations(site_id, date);
CREATE INDEX idx_market_prices_date ON market_prices(date);
CREATE INDEX idx_weather_site_date ON weather_data(site_id, date);
CREATE INDEX idx_ai_memory_user ON ai_memory(user_id);
