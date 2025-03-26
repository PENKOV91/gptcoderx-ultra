import logging
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from core.utils import make_api_request

router = APIRouter(tags=["WebPilot Search"])
logger = logging.getLogger(__name__)

WEBPILOT_API = "https://gpts.webpilot.ai/api/read"

class WebPilotRequest(BaseModel):
    link: HttpUrl = Field(default="https://en.wikipedia.org/wiki/Artificial_intelligence", example="https://en.wikipedia.org/wiki/Artificial_intelligence")
    query: str = Field(default="Main developments in AI", min_length=3, max_length=500)
    language: str = Field(default="en", pattern="^[a-z]{2}(-[A-Z]{2})?$")
    retry: bool = Field(default=False, description="Retry with different approach if True")

class WebPilotResponse(BaseModel):
    title: Optional[str]
    content: str
    meta: Dict[str, str]
    links: List[str]
    search_results: List[Dict]
    tips: List[str]

@router.post("/webpilot", response_model=WebPilotResponse)
async def search_webpilot(data: WebPilotRequest):
    """
    Извличане на информация от уеб страници чрез WebPilot без API ключ
    """
    try:
        payload = {
            "link": str(data.link),
            "ur": data.query,
            "lp": True,
            "rt": data.retry,
            "l": data.language
        }

        logger.info(f"Изпраща се заявка към WebPilot за {data.link} | Запитване: {data.query}")

        response = await make_api_request(
            url=WEBPILOT_API,
            method="POST",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        content = response.get("content", "")
        if not content.strip():
            raise HTTPException(status_code=404, detail="Няма намерено съдържание за този линк.")

        return WebPilotResponse(
            title=response.get("title"),
            content=content,
            meta=response.get("meta", {}),
            links=response.get("links", []),
            search_results=response.get("extra_search_results", []),
            tips=response.get("tips", [])
        )

    except HTTPException as he:
        error_detail = f"❗ WebPilot Error: {he.detail}"
        logger.error(error_detail)
        raise HTTPException(status_code=he.status_code, detail=error_detail)
        
    except Exception as e:
        logger.critical(f"🔥 Критична грешка от WebPilot: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal processing error"
        )
