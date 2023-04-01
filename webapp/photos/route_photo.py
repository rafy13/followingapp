import shutil
import uuid
import os
import logging
from fastapi import File, Request, Depends, UploadFile, status, responses, HTTPException, APIRouter
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.session import get_db
from webapp.photos.create_gallery_form import CreateGalleryForm
from webapp.photos.upload_photo_form import CreatePhotoForm
from db.repository.photo import create_new_photo, fetch_timeline_photos
from db.repository.gallery import create_new_gallery, retrieve_gallery, retrive_gallery_by_user_id
from apis.users_api import get_current_user_from_token
from db.models.users import User
from schemas.photos import CreateGallery, CreatePhoto
from services.user_service import UserService
from services.photo_service import PhotoService

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

@router.get('/')
def get_timeline(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        _, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
        photos = fetch_timeline_photos(current_user, db)
        return templates.TemplateResponse("photos/timeline.html", {"request": request, "photos": photos})
    except HTTPException as error:
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        logging.error(e)
        raise e
        

@router.post('/gallery/new')
async def create_gallery(request: Request, db: Session = Depends(get_db)):
    form = CreateGalleryForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            _, param = get_authorization_scheme_param(token)
            current_user: User = get_current_user_from_token(token=param, db=db)
        except Exception as e:
            return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        try:
            gallery = CreateGallery(name = form.name)
            gallery = create_new_gallery(gallery=gallery, user = current_user, db=db)
            return responses.RedirectResponse("/myprofile", status_code=status.HTTP_302_FOUND)
        except Exception as error:
            logging.error(error, exc_info=e)

@router.get("/gallery/{id}")
def fetch_gallery(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        _, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
    except Exception as error:
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    gallery = retrieve_gallery(id=id, db=db)
    user_service = UserService(db)
    return templates.TemplateResponse(
        "photos/gallery_details.html", {
            "request": request,
            "gallery": gallery,
            "is_owner": gallery.owner == current_user,
            "is_follower": user_service.check_is_follower(current_user.id, gallery.owner_id)
        }
    )

@router.post("/gallery/{id}/upload-image")
async def upload_photo(request: Request, id: int, db: Session = Depends(get_db), photo: UploadFile = File(...)):
    form = CreatePhotoForm(request)
    await form.load_data()
    token = request.cookies.get("access_token")
    _, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    gallery = retrive_gallery_by_user_id(
        id=id,
        user_id=current_user.id,
        db=db
    )
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    # Save photo file
    file_name = str(uuid.uuid4())+photo.filename
    file_path = f"static/uploads/{id}/{file_name}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    photo = CreatePhoto(filename = f"uploads/{id}/{file_name}", caption = form.caption)
    db_photo = create_new_photo(
        photo=photo,
        user=current_user,
        gallery=gallery,
        db=db
    )

    return templates.TemplateResponse("photos/gallery_details.html", {"request": request, "gallery": gallery})


@router.post("/photos/{id}/toggle_like", response_class=responses.HTMLResponse)
async def toggle_like(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        _, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
        photo_service = PhotoService(db)
        photo_service.toggle_like(current_user, id)
        return responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.post("/photos/{id}/toggle_dislike", response_class=responses.HTMLResponse)
async def toggle_dislike(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        _, param = get_authorization_scheme_param(
            token
        )
        current_user: User = get_current_user_from_token(token=param, db=db)
        photo_service = PhotoService(db)
        photo_service.toggle_dislike(current_user, id)
        return responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

