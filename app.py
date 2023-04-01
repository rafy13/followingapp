import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from webapp.auth import route_auth
from webapp.users import router_user
from webapp.photos import route_photo


api_router = APIRouter()
api_router.include_router(route_auth.router, prefix="", tags=["auth-webapp"])
api_router.include_router(router_user.router, prefix="", tags=["users-webapp"])
api_router.include_router(route_photo.router, prefix="", tags=["photos-webapp"])


app = FastAPI()
app.include_router(api_router)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == '__main__':
    uvicorn.run(app, reload=True)



