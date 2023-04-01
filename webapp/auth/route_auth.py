import logging
from fastapi import Request, Depends, status, responses, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.session import get_db
from webapp.auth.login_form import LoginForm
from apis.users_api import login_for_access_token

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("user/login.html", {"request": request})

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            response = responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
            login_for_access_token(response=response, form_data=form, db=db)
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
    return templates.TemplateResponse("user/login.html", form.__dict__)

@router.get('/logout')
def logout(request: Request):
    response = responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie('access_token')
    return response
