# app/main.py

from fastapi import FastAPI

from .routers import auth, assets, optimize
from .routers import data_router
from .routers import portfolios 


app = FastAPI(title="InvestIQ", version="0.1.0")

app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(optimize.router)
app.include_router(data_router.router)
app.include_router(portfolios.router)  


@app.get("/health")
def health():
    return {"status": "ok"}
