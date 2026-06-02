import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.redis import init_redis, close_redis
from app.routers import auth, products, orders
from app.logger import get_logger

logger = get_logger("shopflow")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ShopFlow backend")
    await init_redis()
    yield
    await close_redis()
    logger.info("Shutting down ShopFlow backend")

app = FastAPI(
    title="ShopFlow API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    
    # Не логируем /metrics чтобы не засорять логи
    if request.url.path != "/metrics":
        logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms")
    
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "shopflow-backend"}
