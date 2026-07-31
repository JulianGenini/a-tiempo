-- Developed with assistance from OpenAI Codex.

PRAGMA foreign_keys = ON;
PRAGMA user_version = 1;

CREATE TABLE airports (
    id INTEGER PRIMARY KEY,
    iata TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name TEXT
);

CREATE TABLE airlines (
    id INTEGER PRIMARY KEY,
    iata TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name TEXT
);

CREATE TABLE aircraft (
    id INTEGER PRIMARY KEY,
    registration TEXT NOT NULL UNIQUE COLLATE NOCASE,
    model TEXT,
    manufacturer_serial_number TEXT,
    company TEXT,
    operational_status TEXT,
    detail_url TEXT,
    age_years REAL,
    seat_configuration TEXT
);

CREATE TABLE flight_statuses (
    id INTEGER PRIMARY KEY,
    status_es TEXT,
    status_en TEXT,
    status_pt TEXT,
    color TEXT
);

CREATE TABLE flights (
    id INTEGER PRIMARY KEY,
    flight_date TEXT NOT NULL,
    scheduled_at TEXT,
    actual_at TEXT,
    delay_seconds INTEGER,
    movement TEXT NOT NULL CHECK (movement IN ('A', 'D')),
    flight_number TEXT,
    rotation TEXT,
    airport_id INTEGER NOT NULL REFERENCES airports(id),
    counterpart_airport_id INTEGER REFERENCES airports(id),
    airline_id INTEGER REFERENCES airlines(id),
    aircraft_id INTEGER REFERENCES aircraft(id),
    status_id INTEGER REFERENCES flight_statuses(id),
    passenger_count INTEGER,
    aircraft_body_type TEXT,
    flight_region_code TEXT
);

-- Principal access paths for the dashboard: airport/date, route, airline and delay.
CREATE INDEX flights_airport_date_idx
    ON flights (airport_id, flight_date, counterpart_airport_id);

CREATE INDEX flights_counterpart_date_idx
    ON flights (counterpart_airport_id, flight_date);

CREATE INDEX flights_airline_date_idx
    ON flights (airline_id, flight_date);

CREATE INDEX flights_delay_idx
    ON flights (delay_seconds);

-- Readable projection for application queries. Views occupy no meaningful disk space.
CREATE VIEW flight_details AS
SELECT
    f.id,
    f.flight_date,
    f.scheduled_at,
    f.actual_at,
    f.delay_seconds,
    ROUND(f.delay_seconds / 60.0, 1) AS delay_minutes,
    f.movement,
    f.flight_number,
    f.rotation,
    origin.iata AS airport_iata,
    origin.name AS airport_name,
    counterpart.iata AS counterpart_iata,
    counterpart.name AS counterpart_name,
    al.iata AS airline_iata,
    al.name AS airline_name,
    ac.registration AS aircraft_registration,
    ac.model AS aircraft_model,
    ac.manufacturer_serial_number,
    ac.age_years AS aircraft_age_years,
    ac.seat_configuration,
    fs.status_es,
    fs.status_en,
    fs.color AS status_color,
    f.passenger_count,
    f.aircraft_body_type,
    f.flight_region_code
FROM flights AS f
JOIN airports AS origin ON origin.id = f.airport_id
LEFT JOIN airports AS counterpart ON counterpart.id = f.counterpart_airport_id
LEFT JOIN airlines AS al ON al.id = f.airline_id
LEFT JOIN aircraft AS ac ON ac.id = f.aircraft_id
LEFT JOIN flight_statuses AS fs ON fs.id = f.status_id;
