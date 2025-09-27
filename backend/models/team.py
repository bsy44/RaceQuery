from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.db_init import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=True)
    nationality = Column(String, nullable=True)

    drivers = relationship("Driver", back_populates="team")

    results = relationship("Result", back_populates="team")