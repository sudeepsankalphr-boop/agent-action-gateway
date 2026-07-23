from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import actions, audit, health
from app.dashboard import router as dashboard_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Agent Action Gateway", lifespan=lifespan)
app.include_router(actions.router)
app.include_router(audit.router)
app.include_router(health.router)
app.include_router(dashboard_router.router)
