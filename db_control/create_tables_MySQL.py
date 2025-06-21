from connect_MySQL import engine
from mymodels_MySQL import Base
from sqlalchemy import inspect


def init_db():
    inspector = inspect(engine)

    # 現在のモデルに基づく必要なテーブル一覧（Baseから取得）
    required_tables = Base.metadata.tables.keys()

    # 既存テーブルのリスト
    existing_tables = inspector.get_table_names()

    print("Checking existing tables in the database...")

    # 存在しないテーブルをチェック
    missing_tables = [table for table in required_tables if table not in existing_tables]

    if missing_tables:
        print(f"🛠️ Creating missing tables: {missing_tables}")
        try:
            Base.metadata.create_all(bind=engine)
            print(" Tables created successfully.")
        except Exception as e:
            print(f" Error creating tables: {e}")
            raise
    else:
        print(" All required tables already exist. No action taken.")

if __name__ == "__main__":
    init_db()