import logging
from fastapi import (
    File,
    Request,
    Depends,
    UploadFile,
    status,
    responses,
    HTTPException,
    APIRouter,
    exceptions)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.session import get_db
from webapp.photos.create_gallery_form import CreateGalleryForm
from webapp.photos.upload_photo_form import CreatePhotoForm
from db.repository.photo import PhotoRepository
from db.repository.gallery import GalleryRepository
from db.models.users import User
from schemas.photos import CreateGallery, CreatePhoto
from services.user_service import UserService
from services.photo_service import PhotoService
from services.auth_service import AuthHandlerService

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

@router.get('/')
def get_timeline(request: Request, db: Session = Depends(get_db)):
    photo_repository = PhotoRepository(db)
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        photos = photo_repository.get_timeline_photos(current_user)
        return templates.TemplateResponse("photos/timeline.html", {"request": request, "photos": photos})
    except HTTPException as error:
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        logging.error(e)
        raise e
        

@router.post('/gallery/new')
async def create_gallery(request: Request, db: Session = Depends(get_db)):
    form = CreateGalleryForm(request)
    gallery_repository = GalleryRepository(db)
    await form.load_data()
    if await form.is_valid():
        try:
            auth_service = AuthHandlerService(db)
            current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        except Exception as error:
            logging.error(error, exc_info=error)
            return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        try:
            gallery = CreateGallery(name = form.name)
            db_gallery = gallery_repository.create(gallery=gallery, user = current_user)
            return responses.RedirectResponse("/myprofile", status_code=status.HTTP_302_FOUND)
        except Exception as error:
            logging.error(error, exc_info=error)

@router.get("/gallery/{id}")
def fetch_gallery(id: int, request: Request, db: Session = Depends(get_db)):
    gallery_repository = GalleryRepository(db)
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    gallery = gallery_repository.get(id=id)
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
async def upload_photo(request: Request, id: int, db: Session = Depends(get_db), image_file: UploadFile = File(...)):
    try:
        form = CreatePhotoForm(request)
        photo_service = PhotoService(db)
        await form.load_data()
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        _, gallery = photo_service.upload_photo(gallery_id=id, user=current_user, image_file=image_file, form=form)
        return templates.TemplateResponse(
            "photos/gallery_details.html", {
                "request": request,
                "gallery": gallery,
                "is_owner": True
            }
        )
    except HTTPException as error:
         logging.error(error)
         return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    except exceptions.RequestValidationError as error:
        logging.error(error)
        return templates.TemplateResponse(
            "photos/gallery_details.html", {
                "request": request,
                "gallery": gallery,
                "is_owner": True,
                "errors": ["Please upload a valid image"]
            }
        )
    except Exception as e:
        logging.error(e, exc_info=e)
        raise e

@router.post("/photos/{id}/toggle_like", response_class=responses.HTMLResponse)
async def toggle_like(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        photo_service = PhotoService(db)
        photo_service.toggle_like(current_user, id)
        return responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.post("/photos/{id}/toggle_dislike", response_class=responses.HTMLResponse)
async def toggle_dislike(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        auth_service = AuthHandlerService(db)
        current_user: User = auth_service.get_authenticated_user(token=request.cookies.get("access_token"))
        photo_service = PhotoService(db)
        photo_service.toggle_dislike(current_user, id)
        return responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except HTTPException as error:
        logging.error(error, exc_info=error)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
