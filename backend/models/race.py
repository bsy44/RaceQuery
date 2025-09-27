from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from backend.db_init import Base

class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=True)

    circuit_id = Column(Integer, ForeignKey("circuits.id"))
    circuit = relationship("Circuit", back_populates="races")

    results = relationship("Result", back_populates="race")