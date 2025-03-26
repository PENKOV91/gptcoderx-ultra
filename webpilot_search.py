import logging
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from core.utils import make_api_request

router = APIRouter(tags=["WebPilot Search"])
logger = logging.getLogger(__name__)

WEBPILOT_API = "https://gpts.webpilot.ai/api/read"

class WebPilotRequest(BaseModel):
    link: HttpUrl = Field(..., example="https://en.wikipedia.org/wiki/Artificial_intelligence")
    query: str = Field(..., min_length=3, max_length=500, example="Main developments in AI")
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

        response = await make_api_request(
            url=WEBPILOT_API,
            method="POST",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        return WebPilotResponse(
            title=response.get("title"),
            content=response.get("content", ""),
            meta=response.get("meta", {}),
            links=response.get("links", []),
            search_results=response.get("extra_search_results", []),
            tips=response.get("tips", [])
        )

    except HTTPException as he:
        error_detail = f"WebPilot Error: {he.detail}"
        logger.error(error_detail)
        raise HTTPException(status_code=he.status_code, detail=error_detail)
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal processing error"
        )
