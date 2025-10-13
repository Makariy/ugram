from cache.lifespan import cache_lifespan
from fastapi import FastAPI

from auth.router import router as auth_router


app = FastAPI(
    lifespan=cache_lifespan,
)

app.include_router(auth_router, prefix="/auth")


