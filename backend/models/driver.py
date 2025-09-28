from dataclasses import dataclass

@dataclass
class Driver:
    id: int
    racingNumber: str
    broadcastName: str
    first_name: str
    last_name: str
    full_name: str
    nationality: str
