from backend.database import engine

def drop_tables():
    with engine.connect() as conn:
        conn.execute("DROP TABLE IF EXISTS signal_deliveries CASCADE;")
        conn.execute("DROP TABLE IF EXISTS signals CASCADE;")
        conn.commit()

drop_tables()
print("Таблицы signals и signal_deliveries удалены!")
