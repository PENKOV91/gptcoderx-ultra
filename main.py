from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Внос на всички routers
from deepseek_api import router as deepseek_router
from github_search import router as github_router
from webpilot_search import router as webpilot_router
from merge import router as merge_router

app = FastAPI(
    title="GPT-CODER X ULTRA",
    description="Персонализиран GPT агент за създаване на MQL4/MQL5/Python код чрез DeepSeek, GitHub, WebPilot и Reasoner.",
    version="1.0.0"
)

# CORS - за да може да се вика отвън
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Може да ограничиш към конкретен домейн
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включване на всички routers
app.include_router(deepseek_router, prefix="/code")
app.include_router(github_router, prefix="/search")
app.include_router(webpilot_router, prefix="/search")
app.include_router(merge_router, prefix="/merge")

# Root endpoint (за проверка)
@app.get("/")
def root():
    return {"message": "🚀 GPT-CODER X ULTRA Backend is running!"}

# ✅ Сървиране на статични JSON файлове от .well-known
if not os.path.exists(".well-known"):
    os.makedirs(".well-known")

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="wellknown")
