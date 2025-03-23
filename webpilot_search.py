import requests
from fastapi import APIRouter

router = APIRouter()

WEBPILOT_API = "https://gpts.webpilot.ai/gpts_webpilot_ai__jit_plugin.webPageReader"

@router.post("/webpilot")
def search_webpilot(link: str, query: str):
    payload = {
        "link": link,
        "ur": query,
        "lp": True  # без език, автоматично
    }

    try:
        response = requests.post(WEBPILOT_API, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
