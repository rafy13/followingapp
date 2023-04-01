import re
from typing import List
from typing import Optional

from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get(
            "email"
        )
        self.password = form.get("password")

    async def is_valid(self):
        if not self.email or re.match("^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", self.email) is None:
            self.errors.append("Invalid Email address")
        if not self.password or len(self.password) < 8:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False