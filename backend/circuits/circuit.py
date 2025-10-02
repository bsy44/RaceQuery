class Circuit:
    def __init__(self, circuitId: str, circuitName: str, locality: str, country: str):
        self.circuitId = circuitId
        self.circuitName = circuitName
        self.locality = locality
        self.country = country

    def to_dict(self):
        return {
            "circuitId": self.circuitId,
            "circuitName": self.circuitName,
            "Location": {
                "locality": self.locality,
                "country": self.country
            }
        }
