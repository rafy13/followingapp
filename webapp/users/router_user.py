import shutil
import uuid
import os
import logging

from fastapi import (
    File,
    Request,
    Depends,
    UploadFile,
    status,
    responses,
    APIRouter,
    HTTPException)
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from services.user_activation_service import UserActivationService
from pydantic import ValidationError

from db.session import get_db
from webapp.users.registration_form import UserRegistrationForm
from schemas.users import UserRegistration
from db.repository.users import (
    fetch_user,
    create_new_user,
    fetch_nearby_users)
from db.repository.follow import(
    fetch_follow,
    delete_follow,
    create_follow)
from apis.users_api import  get_current_user_from_token
from db.models.users import User
from core.filters import calculate_age
from services.user_service import UserService

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)
templates.env.filters['age'] = calculate_age

@router.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("user/registration.html", {"request": request})

@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    form = UserRegistrationForm(request)
    user_activation_service = UserActivationService()
    await form.load_data()
    if await form.is_valid():
        try:
            user = UserRegistration(
                name=form.name, 
                email=form.email, 
                password=form.password,
                location_latitude=form.location_latitude,
                location_longitude=form.location_longitude,
                date_of_birth=form.date_of_birth,
                gender=form.gender
            )
            user = create_new_user(user=user, db=db)
            user_activation_service.send_email_verification_url(user)
            return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        except ValidationError as error:
            form.__dict__.get("errors").append(str(error))
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate email")
    logging.error(form.errors)
    return templates.TemplateResponse("user/registration.html", form.__dict__)

@router.post("/users/upload-profile-image")
def upload_profile_image(request: Request, db: Session = Depends(get_db), profile_image: UploadFile = File(...)):
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    file_name = str(uuid.uuid4())+profile_image.filename
    file_path = f"static/gallery/{current_user.id}/{file_name}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(profile_image.file, buffer)

    current_user.profile_image = f"gallery/{current_user.id}/{file_name}"
    db.commit()

    return responses.RedirectResponse("/myprofile", status_code=status.HTTP_302_FOUND)

# @router.get('/')
# def get_timeline(request: Request, db: Session = Depends(get_db)):
#     try:
#         token = request.cookies.get("access_token")
#         scheme, param = get_authorization_scheme_param(
#             token
#         )
#         current_user: User = get_current_user_from_token(token=param, db=db)
#         return templates.TemplateResponse("photos/timeline.html", {"request": request})
#     except Exception as e:
#         return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get('/myprofile')
def get_my_profile(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
        return templates.TemplateResponse("user/profile.html", {"request": request, "user": current_user, "is_owner": True})
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/users/{id}")
def get_user(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
        user: User = fetch_user(id=id, db=db)
        user_service = UserService(db)
        print("============================")
        logging.error("^^^^^^^^^^^^^^^^^^^^", current_user.id, user.id, user_service.check_is_follower(current_user.id, user.id))
        return templates.TemplateResponse(
            "user/profile.html",{
                "request": request,
                "user": user,
                "is_owner": user.id == current_user.id,
                "is_follower": user_service.check_is_follower(current_user.id, user.id)
            }
        )
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        _, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
        users = fetch_nearby_users(current_user=current_user, db=db)
        return templates.TemplateResponse("user/user_list.html", {"request": request, "users": users})
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/users/activate/{token}", response_class=HTMLResponse)
async def activate_user(token: str, request: Request, db: Session = Depends(get_db)):
    user_activation_service = UserActivationService()
    user: User = user_activation_service.activate_user_with_activation_token(token, db)
    return templates.TemplateResponse("user/user_activation.html", {"request": request, "user": user})

@router.post("/users/{id}/toggle_follow", response_class=HTMLResponse)
async def toggle_follow(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        _, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
        follow = fetch_follow(follower_id=current_user.id, followed_id=id, db=db)
        if follow:
            delete_follow(follow, db)
        else:
            create_follow(follower_id=current_user.id, followed_id=id, db=db)
        return templates.TemplateResponse("user/user_list.html", {"request": request, "users": fetch_nearby_users(current_user=current_user, db=db)})
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

