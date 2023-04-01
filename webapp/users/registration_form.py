from typing import List
import datetime
import re

from fastapi import Request


class UserRegistrationForm:
    def __init__(self, request: Request):
        self.request = request
        self.name: str = None
        self.email: str = None
        self.password: str = None
        self.gender: str = None
        self.location_latitude: float = 0
        self.location_longitude: float = 0
        self.date_of_birth: datetime.date = None
        self.errors: List = []

    async def load_data(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.email = form.get("email")
        self.password = form.get("password")
        self.gender = form.get("gender")
        self.location_latitude = form.get("location_latitude")
        self.location_longitude = form.get("location_longitude")
        self.date_of_birth = form.get("date_of_birth")

    async def is_valid(self):
        if not self.name or len(self.name) < 1:
            self.errors.append("Provide a valid name")
        if not self.email or re.match("^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", self.email) is None:
            self.errors.append("Invalid Email address")
        if not self.password or len(self.password) < 8:
            self.errors.append("Password must contains 8 chars or more")
        if not self.errors:
            return True
        return False
