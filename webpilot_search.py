import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

WEBPILOT_API = "https://gpts.webpilot.ai/gpts_webpilot_ai__jit_plugin.webPageReader"

class WebPilotRequest(BaseModel):
    link: str
    query: str

@router.post("/webpilot")
def search_webpilot(data: WebPilotRequest):
    payload = {
        "link": data.link,
        "ur": data.query,
        "lp": True  # подаден директен линк (lp = link provided)
    }

    try:
        response = requests.post(WEBPILOT_API, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"WebPilot API error: {str(e)}")
