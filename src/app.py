from cache.lifespan import cache_lifespan
from fastapi import FastAPI

from auth.router import router as auth_router
from group.router import router as group_router 
from message.router import router as message_router 


app = FastAPI(
    lifespan=cache_lifespan,
)

app.include_router(auth_router, prefix="/auth")
app.include_router(group_router, prefix="/group")
app.include_router(message_router, prefix="/message")

