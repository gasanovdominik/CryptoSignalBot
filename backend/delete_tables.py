from sqlalchemy import text
from backend.database import engine

def drop_tables():
    with engine.connect() as conn:
        print("Удаляю таблицы...")
        conn.execute(text("DROP TABLE IF EXISTS signal_deliveries CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS signals CASCADE;"))
        conn.commit()
        print("Таблицы удалены.")

drop_tables()
