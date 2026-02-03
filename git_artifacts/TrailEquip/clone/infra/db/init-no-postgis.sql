-- Simplified schema without PostGIS (for development without PostGIS extension)

CREATE TABLE trails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  distance DECIMAL(10, 2),
  elevation_gain INTEGER,
  elevation_loss INTEGER,
  duration_minutes INTEGER,
  max_slope DECIMAL(5, 2),
  avg_slope DECIMAL(5, 2),
  terrain TEXT[],
  difficulty VARCHAR(20),
  hazards TEXT[],
  source VARCHAR(100),
  geometry TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trails_difficulty ON trails(difficulty);

CREATE TABLE weather_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  start_date DATE,
  end_date DATE,
  forecast_data JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP
);

CREATE INDEX idx_weather_cache_location_date ON weather_cache(latitude, longitude, start_date);

-- Seed data: sample trails
INSERT INTO trails (id, name, description, distance, elevation_gain, elevation_loss, duration_minutes, max_slope, avg_slope, terrain, difficulty, hazards, source, created_at, updated_at) VALUES
('550e8400-e29b-41d4-a716-446655440001'::uuid, 'Omu Peak Loop', 'Classic route via alpine meadows and exposed ridge', 12.5, 450, 450, 240, 35.2, 12.1, ARRAY['forest', 'alpine_meadow', 'exposed_ridge'], 'MEDIUM', ARRAY['exposure', 'weather_dependent'], 'openstreetmap', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('550e8400-e29b-41d4-a716-446655440002'::uuid, 'Sphinx Ridge Scramble', 'Technical scramble with rock climbing sections', 8.3, 680, 680, 320, 65.0, 35.5, ARRAY['scramble', 'exposed_ridge', 'rock'], 'ROCK_CLIMBING', ARRAY['exposure', 'loose_rock', 'high_altitude'], 'openstreetmap', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('550e8400-e29b-41d4-a716-446655440003'::uuid, 'Bulea Lake Forest Walk', 'Easy forested walk with lake views', 6.8, 150, 150, 120, 12.0, 4.5, ARRAY['forest', 'lake'], 'EASY', ARRAY[]::text[], 'openstreetmap', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
