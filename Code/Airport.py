class Airport:
    def __init__(
        self,
        city,
        code,
        lat,
        lon,
        runway_length,
        available_slots,
    ):
        self.city: str = city
        self.code: str = code
        self.lat: float = lat
        self.lon: float = lon
        self.runway_length: int = runway_length
        self.available_slots: int = available_slots

    def __repr__(self):
        return f"Airport(city={self.city}, code={self.code}, lat={self.lat}, lon={self.lon}, runway_length={self.runway_length}, available_slots={self.available_slots})"
