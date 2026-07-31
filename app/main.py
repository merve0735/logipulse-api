import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger, log_duration
from app.db.mongodb import close_mongo_connection, connect_to_mongo

configure_logging()
_api_logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


# Production'da Swagger/ReDoc kapali kalir; local/staging'de acik kalmaya devam eder.
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        _api_logger.error("%s %s failed: %s", request.method, request.url.path, exc)
        raise

    elapsed_ms = (time.perf_counter() - start) * 1000
    operation_name = f"{request.method} {request.url.path} -> {response.status_code}"
    log_duration(_api_logger, operation_name, elapsed_ms)
    return response


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/demo/")


app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_PREFIX)
app.mount("/demo", StaticFiles(directory="app/static", html=True), name="demo")
