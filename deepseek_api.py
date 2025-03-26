import os
import requests
from fastapi import APIRouter
from merge import merge_results

router = APIRouter()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

API_URL = "https://api.deepseek.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def build_payload(prompt, model):
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert developer in MQL4, MQL5, and Python for trading systems."
            },
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

def query_deepseek(prompt: str, model: str):
    payload = build_payload(prompt, model)
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    data = response.json()

    if "error" in data:
        return {
            "error": data["error"].get("message", "Unknown error from DeepSeek API."),
            "model_used": model
        }

    return {
        "response": data,
        "model_used": model
    }

# ✅ 1. Стандартно deepseek извикване (за код)
@router.post("/deepseek")
def code_with_deepseek(data: dict):
    return query_deepseek(data["prompt"], "deepseek-chat")

# ✅ 2. Само reasoning
@router.post("/reasoner")
def code_with_reasoner(data: dict):
    return query_deepseek(data["prompt"], "deepseek-reasoner")

# ✅ 3. Reasoning верига: chat → reasoner → chat
@router.post("/reasoning-chain")
def process_with_reasoning_chain(data: dict):
    prompt = data["prompt"]

    # 1. DeepSeek Chat
    first_response = query_deepseek(prompt, "deepseek-chat")

    # 2. Reasoning
    reasoning_input = first_response["response"]["choices"][0]["message"]["content"]
    reasoning_response = query_deepseek(reasoning_input, "deepseek-reasoner")

    # 3. Final chat output
    final_input = reasoning_response["response"]["choices"][0]["message"]["content"]
    final_response = query_deepseek(final_input, "deepseek-chat")

    return {
        "initial_understanding": first_response,
        "reasoning": reasoning_response,
        "final_output": final_response
    }

# ✅ 4. Разсъждение по събрани външни данни (GitHub + WebPilot + MQL5)
@router.post("/reasoning-merge")
def process_merge_reasoning(data: dict):
    merged = merge_results(
        github_results=data.get("github_results", []),
        webpilot_results=data.get("webpilot_results", {}),
        mql5_results=data.get("mql5_results", [])
    )

    combined_text = "\n\n".join(
        f"[{item['source']}] {item['title']}:\n{item['content']}" for item in merged
    )

    reasoning_input = f"Обмисли следните резултати и предложи логическо решение:\n{combined_text}"
    reasoning_response = query_deepseek(reasoning_input, "deepseek-reasoner")

    final_prompt = reasoning_response["response"]["choices"][0]["message"]["content"]
    final_code = query_deepseek(final_prompt, "deepseek-chat")

    return {
        "merged_sources": merged,
        "reasoning": reasoning_response,
        "final_code": final_code
    }
