import re
from typing import List
from typing import Optional

from fastapi import Request


class CreateGalleryForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.name: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.name = form.get("name")

    async def is_valid(self):
        if not self.name or len(self.name) < 1:
            self.errors.append("A valid name is required")
        if not self.errors:
            return True
        return False