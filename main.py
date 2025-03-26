import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError

# Импортиране на всички рутери
from deepseek_api import router as deepseek_router
from github_search import router as github_router
from webpilot_search import router as webpilot_router
from merge import router as merge_router

# Настройка на логирането
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GPT-CODER X ULTRA",
    description="Персонализиран GPT агент за създаване на MQL4/MQL5/Python код",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    on_startup=[lambda: logger.info("🚀 Сервирът стартира успешно!")],
    on_shutdown=[lambda: logger.info("🛑 Сервирът спира...")]
)

# ==============================================
# Мидълуери и сигурност
# ==============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # За production променете на конкретни домейни
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-API-Version"]
)

# Добавяне на security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.update({
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'"
    })
    return response

# ==============================================
# Глобална обработка на грешки
# ==============================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Невалидни входни данни"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Вътрешна грешка в сървъра"}
    )

# ==============================================
# Регистрация на рутери
# ==============================================
app.include_router(
    deepseek_router,
    prefix="/code",
    tags=["Code Generation"]
)

app.include_router(
    github_router,
    prefix="/search",
    tags=["GitHub Search"]
)

app.include_router(
    webpilot_router,
    prefix="/search",
    tags=["Web Search"]
)

app.include_router(
    merge_router,
    prefix="/merge",
    tags=["Data Merging"]
)

# ==============================================
# Статични файлове и базови ендпойнти
# ==============================================
WELL_KNOWN_DIR = ".well-known"

@app.on_event("startup")
async def startup_event():
    # Създаване на директория ако не съществува
    os.makedirs(WELL_KNOWN_DIR, exist_ok=True)
    logger.info(f"Директория {WELL_KNOWN_DIR} е подготвена")

@app.get("/", include_in_schema=False)
async def root():
    return {
        "status": "active",
        "version": app.version,
        "services": ["DeepSeek", "GitHub", "WebPilot", "MQL5"]
    }

@app.get("/health", include_in_schema=False)
async def health_check():
    return JSONResponse(content={"status": "OK", "timestamp": datetime.utcnow().isoformat()})

app.mount(
    "/.well-known",
    StaticFiles(directory=WELL_KNOWN_DIR),
    name="wellknown"
)

@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return FileResponse(
        f"{WELL_KNOWN_DIR}/openapi.json",
        media_type="application/json",
        headers={"X-API-Version": app.version}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,
        timeout_keep_alive=300
    )
