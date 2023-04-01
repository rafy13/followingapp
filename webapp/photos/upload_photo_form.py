from fastapi import Request

class CreatePhotoForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.caption: str = ""

    async def load_data(self):
        form = await self.request.form()
        self.caption = form.get("caption")