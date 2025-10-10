-- Sample Data for SPRNG DSM Portal
-- Run after schema.sql. Passwords plain for test—use bcrypt in prod.

-- Sample Users (password: 'password123' for both)
INSERT INTO users (name, email, password_hash, role) VALUES 
('Admin User', 'admin@sprngenergy.com', 'password123', 'admin'),
('Operator User', 'operator@sprngenergy.com', 'password123', 'operator');

-- Sample Site (REWA Solar)
INSERT INTO sites (site_name, capacity_mw, region, state, latitude, longitude) VALUES 
('REWA Solar', 50.0, 'Central', 'Madhya Pradesh', 23.2599, 77.4126);

-- Sample Schedule (Day-ahead for 2025-10-07, first 5 blocks for test; expand to 96)
INSERT INTO schedules (site_id, date, block_no, scheduled_mw) VALUES 
(1, '2025-10-07', 1, 20.0),
(1, '2025-10-07', 2, 18.5),
(1, '2025-10-07', 3, 22.0),
(1, '2025-10-07', 4, 19.2),
(1, '2025-10-07', 5, 21.5);

-- Sample Generation (Actual data with deviations for DSM test)
INSERT INTO generations (site_id, date, block_no, actual_mw) VALUES 
(1, '2025-10-07', 1, 25.0),  -- Over-injection: 25% deviation (penalty)
(1, '2025-10-07', 2, 16.0),  -- Under-injection: ~13% (no penalty)
(1, '2025-10-07', 3, 26.4),  -- Over: 20% (full penalty)
(1, '2025-10-07', 4, 18.0),  -- Under: ~6% (no penalty)
(1, '2025-10-07', 5, 23.0);  -- Over: ~7% (no penalty)

-- Sample Market Prices (Default 3 INR/kWh for test)
INSERT INTO market_prices (date, block_no, dam_price, rtm_price) VALUES 
('2025-10-07', 1, 3.0, 3.5),
('2025-10-07', 2, 3.2, 3.6),
('2025-10-07', 3, 2.8, 3.4),
('2025-10-07', 4, 3.1, 3.7),
('2025-10-07', 5, 3.0, 3.5);

-- Sample Weather (For correlation test)
INSERT INTO weather_data (site_id, date, block_no, irradiance, temp, wind_speed, cloud_cover) VALUES 
(1, '2025-10-07', 1, 500.0, 28.5, 5.2, 30),
(1, '2025-10-07', 2, 480.0, 29.0, 4.8, 40),
(1, '2025-10-07', 3, 550.0, 27.8, 6.0, 20),
(1, '2025-10-07', 4, 520.0, 28.2, 5.5, 25),
(1, '2025-10-07', 5, 510.0, 29.1, 4.9, 35);

-- Note: Expand to 96 blocks for full day. Run this after schema.sql.
