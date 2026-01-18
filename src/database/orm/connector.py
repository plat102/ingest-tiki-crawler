from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.config import DB_CONFIG_DICT

DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG_DICT['user']}:{DB_CONFIG_DICT['password']}@{DB_CONFIG_DICT['host']}:{DB_CONFIG_DICT['port']}/{DB_CONFIG_DICT['dbname']}"

# create engine wih pool
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
