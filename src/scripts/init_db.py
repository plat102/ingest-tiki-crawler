import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.database.config import DB_CONFIG_DICT

def init():
    config = DB_CONFIG_DICT.copy()
    target_db_name = config.pop("dbname")
    config["dbname"] = "postgres" # switch to default db for connect

    try:
        #  connect
        conn = psycopg2.connect(**config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # create db
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{target_db_name}'")
        if not cur.fetchone():
            print(f"Creating database '{target_db_name}'...")
            cur.execute(f"CREATE DATABASE {target_db_name}")
            print("Database created successfully!")
        else:
            print(f"Database '{target_db_name}' already exists.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init()
