from backend.database import engine

def drop_tables():
    with engine.connect() as conn:
        print("Удаляю таблицы...")
        conn.exec_driver_sql("DROP TABLE IF EXISTS signal_deliveries CASCADE;")
        conn.exec_driver_sql("DROP TABLE IF EXISTS signals CASCADE;")
        print("Таблицы удалены! ✅")

drop_tables()

