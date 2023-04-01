from pydantic import BaseModel

class CreateGallery(BaseModel):
    name: str

class CreatePhoto(BaseModel):
    filename: str
    caption: str