from backend.database import engine

SQL = """
CREATE TABLE IF NOT EXISTS signals (
    id BIGSERIAL PRIMARY KEY,
    market TEXT,
    symbol TEXT,
    direction TEXT,
    tf TEXT,
    entry JSONB,
    sl NUMERIC,
    tps JSONB,
    risk_rr NUMERIC,
    leverage INT,
    risk_pct NUMERIC,
    indicators JSONB,
    comment TEXT,
    image_url TEXT,
    created_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

def create_table():
    with engine.connect() as conn:
        print("Создаю таблицу signals...")
        conn.exec_driver_sql(SQL)
        print("Таблица signals создана! ✅")

create_table()
