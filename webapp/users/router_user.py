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
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from services.user_activation_service import UserActivationService
from pydantic import ValidationError

from db.session import get_db
from webapp.users.registration_form import UserRegistrationForm
from schemas.users import UserRegistration
from db.repository.users import UserRepository
from db.repository.follow import FollowRepository
from db.models.users import User
from core.filters import calculate_age
from services.user_service import UserService
from services.auth_service import AuthHandlerService

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
    user_repository = UserRepository(db)
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
            user = user_repository.create(user=user)
            user_activation_service.send_email_verification_url(user)
            return templates.TemplateResponse("user/user_successful_registration.html", {"request": request})
        except ValidationError as error:
            form.__dict__.get("errors").append(str(error))
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate email")
    logging.error(form.errors)
    return templates.TemplateResponse("user/registration.html", form.__dict__)

@router.post("/users/upload-profile-image")
def upload_profile_image(request: Request, db: Session = Depends(get_db), profile_image: UploadFile = File(...)):
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        user_service = UserService(db)
        current_user = user_service.upload_profile_image(user = current_user, profile_image=profile_image)
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    except ValidationError as e:
        return templates.TemplateResponse("user/profile.html", {
            "request": request,
            "user": current_user,
            "is_owner": True,
            "errors": ["Upload a valid image"]})
    except Exception as error:
        logging.error(error, exc_info=error)
        raise error

    return responses.RedirectResponse("/myprofile", status_code=status.HTTP_302_FOUND)

@router.get('/myprofile')
def get_my_profile(request: Request, db: Session = Depends(get_db)):
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        return templates.TemplateResponse("user/profile.html", {"request": request, "user": current_user, "is_owner": True})
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.get("/users/{id}")
def get_user(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        user_repository = UserRepository(db)
        user: User = user_repository.get_active_user(id=id)
        user_service = UserService(db)
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
    user_repository = UserRepository(db)
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        users = user_repository.fetch_nearby_active_users(current_user=current_user)
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
    user_repository = UserRepository(db)
    follow_repository = FollowRepository(db)
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        follow = follow_repository.get_by_follower_id_followed_id(follower_id=current_user.id, followed_id=id)
        if follow:
            follow_repository.delete(follow)
        else:
            follow_repository.create(follower_id=current_user.id, followed_id=id)
        return templates.TemplateResponse(
            "user/user_list.html",
            {  
                "request": request,
                "users": user_repository.fetch_nearby_active_users(current_user=current_user)
            })
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

