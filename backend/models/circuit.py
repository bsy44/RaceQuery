from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from backend.db_init import Base

class Circuit(Base):
    __tablename__ = "circuits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    location = Column(String, nullable=True)
    country = Column(String, nullable=True)
    length_km = Column(Float, nullable=True)
    laps = Column(Integer, nullable=True)

    races = relationship("Race", back_populates="circuit")
