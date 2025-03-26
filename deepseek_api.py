import os
import logging
import requests
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from merge import merge_results

# Настройки за логване
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1024
    temperature: Optional[float] = 0.7

class ExternalDataRequest(BaseModel):
    prompt: str
    github_results: List[Dict] = []
    webpilot_results: Dict = {}
    mql5_results: List[Dict] = []

# Конфигурация за DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-1fffaaad868945feb8030ed27e1ac46a")
API_URL = "https://api.deepseek.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

SYSTEM_PROMPT = "You are an expert developer in MQL4, MQL5, and Python for trading systems."

def build_payload(prompt: str, model: str, max_tokens: int, temperature: float) -> dict:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }

def handle_api_error(error_data: dict) -> None:
    error_msg = error_data.get("error", {}).get("message", "Unknown API error")
    error_code = error_data.get("error", {}).get("code", "unknown")
    logger.error(f"DeepSeek API Error [{error_code}]: {error_msg}")
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"API Error: {error_msg}"
    )

def query_deepseek(prompt: str, model: str, max_tokens: int, temperature: float) -> dict:
    try:
        if not DEEPSEEK_API_KEY:
            logger.error("DeepSeek API key not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error"
            )

        payload = build_payload(prompt, model, max_tokens, temperature)
        logger.info(f"Sending request to DeepSeek API with model: {model}")

        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            handle_api_error(data)

        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Connection to AI service failed"
        )

# Рутиране
@router.post("/deepseek", summary="Генериране на код с DeepSeek Chat")
async def code_with_deepseek(request: PromptRequest):
    try:
        response = query_deepseek(
            prompt=request.prompt,
            model="deepseek-chat",
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return {
            "result": response["choices"][0]["message"]["content"],
            "model": "deepseek-chat",
            "usage": response.get("usage", {})
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/reasoner", summary="Само Reasoning логика")
async def code_with_reasoner(request: PromptRequest):
    try:
        response = query_deepseek(
            prompt=request.prompt,
            model="deepseek-reasoner",
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return {
            "reasoning": response["choices"][0]["message"]["content"],
            "model": "deepseek-reasoner",
            "usage": response.get("usage", {})
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/reasoning-chain", summary="Верижно разсъждение")
async def process_with_reasoning_chain(request: PromptRequest):
    try:
        # Стъпка 1: Първоначално разбиране
        first_step = await code_with_deepseek(request)
        
        # Стъпка 2: Разсъждение
        reasoning_request = PromptRequest(
            prompt=first_step["result"],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        reasoning_step = await code_with_reasoner(reasoning_request)
        
        # Стъпка 3: Финален код
        final_request = PromptRequest(
            prompt=reasoning_step["reasoning"],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        final_step = await code_with_deepseek(final_request)
        
        return {
            "initial_understanding": first_step,
            "reasoning_process": reasoning_step,
            "final_output": final_step
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Chain processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reasoning chain processing failed"
        )

@router.post("/reasoning-merge", summary="Разсъждение със сливане на данни")
async def process_merge_reasoning(request: ExternalDataRequest):
    try:
        # Сливане на данните
        merged_data = merge_results(
            github_results=request.github_results,
            webpilot_results=request.webpilot_results,
            mql5_results=request.mql5_results
        )
        
        # Подготовка на входните данни
        combined_input = "\n\n".join(
            f"[{item['source']}] {item.get('title', 'No title')}:\n{item.get('content', '')}"
            for item in merged_data
        )
        
        # Генериране на разсъждение
        reasoning_response = await code_with_reasoner(PromptRequest(
            prompt=f"Анализирай и предложи решение на базата на следните данни:\n{combined_input}",
            max_tokens=request.max_tokens,
            temperature=request.temperature
        ))
        
        # Генериране на финален код
        final_code = await code_with_deepseek(PromptRequest(
            prompt=reasoning_response["reasoning"],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        ))
        
        return {
            "analysis": reasoning_response,
            "generated_code": final_code,
            "sources_used": [item["source"] for item in merged_data]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Merge processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data merge processing failed"
        )
