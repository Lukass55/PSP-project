from fastapi import FastAPI

from app.routers.tenants import router as tenants_router
from app.routers.users import router as users_router
from app.routers.groups import router as groups_router
from app.routers.expenses import router as expenses_router
from app.routers.balances import router as balances_router

app = FastAPI(title="SplitPay")

app.include_router(tenants_router)
app.include_router(users_router)
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(balances_router)

@app.get("/")
def home():
    return {"message": "Sveiki atvykę į SplitPay!"}