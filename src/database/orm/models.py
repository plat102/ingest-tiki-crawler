from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, JSON, TIMESTAMP, func

Base = declarative_base()
class ProductORM(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url_key = Column(String)
    price = Column(Numeric(12,2))
    description = Column(Text)
    image_urls = Column(JSON)
    raw_data = Column(JSON)

    # Auto update times
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now(), nullable=False)
