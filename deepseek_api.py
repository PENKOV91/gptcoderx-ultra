import os
import requests
from fastapi import APIRouter

router = APIRouter()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

API_URL = "https://api.deepseek.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def build_payload(prompt, model="deepseek-coder-v2"):
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert developer in MQL4, MQL5, and Python for trading systems."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

def generate_code(prompt: str):
    payload = build_payload(prompt, model="deepseek-coder-v2")
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()

def generate_reasoning(prompt: str):
    payload = build_payload(prompt, model="deepseek-reasoner")
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()

# 🧩 Добавяме route-ите тук, за да работят с include_router()
@router.post("/deepseek")
def code_with_deepseek(data: dict):
    return generate_code(data["prompt"])

@router.post("/reasoner")
def code_with_reasoner(data: dict):
    return generate_reasoning(data["prompt"])
