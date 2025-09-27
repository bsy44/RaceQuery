from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from backend.db_init import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(Integer, nullable=False)
    points = Column(Float, nullable=True)
    status = Column(String, nullable=True)

    driver_id = Column(Integer, ForeignKey("drivers.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    race_id = Column(Integer, ForeignKey("races.id"))

    driver = relationship("Driver")
    team = relationship("Team", back_populates="results")
    race = relationship("Race", back_populates="results")