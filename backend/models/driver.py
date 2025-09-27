from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.db_init import Base

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    driver_number = Column(String, nullable=False)  # ex: "44"
    code = Column(String, nullable=False)           # ex: "HAM"
    first_name = Column(String, nullable=False)     # ex: "Lewis"
    last_name = Column(String, nullable=False)      # ex: "Hamilton"
    full_name = Column(String, nullable=False)      # ex: "Lewis Hamilton"
    nationality = Column(String, nullable=True)     # dispo via fastf1
    headshot_url = Column(String, nullable=True)    # portrait du pilote

    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="drivers")

    def __repr__(self):
        return f"<Driver {self.code} - {self.full_name}>"
