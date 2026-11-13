from pathlib import Path

from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers.users import router as users_router
from app.routers.groups import router as groups_router
from app.routers.expenses import router as expenses_router
from app.routers.balances import router as balances_router
from app.routers import auth
import os
from starlette.middleware.sessions import SessionMiddleware


load_dotenv(Path(__file__).resolve().parent.parent / ".env")
app = FastAPI(title="SplitPay")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SPLITPAY_SESSION_SECRET"],
    same_site="lax",
    https_only=False
)

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)

app.include_router(users_router)
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(balances_router)
app.include_router(auth.router)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )