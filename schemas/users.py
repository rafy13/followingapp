from pydantic import BaseModel, PastDate

class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    gender: str
    location_latitude: float
    location_longitude: float
    date_of_birth: PastDate
