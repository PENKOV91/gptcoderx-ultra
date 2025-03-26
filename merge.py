import logging
from datetime import datetime
from typing import List, Optional, Dict, Any  # ✅ Добавен Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl, validator
from core.config import settings

router = APIRouter(tags=["Data Merging"])
logger = logging.getLogger(__name__)

class GitHubItem(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = Field(default="")
    url: HttpUrl
    stars: Optional[int] = Field(default=0, ge=0)
    language: Optional[str] = Field(default=None)
    last_updated: Optional[datetime] = Field(default=None)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v

class WebPilotResult(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=10)
    link: HttpUrl
    source: Optional[str] = Field(default="Web")
    relevance: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)

class MQL5Item(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10)
    url: HttpUrl
    votes: Optional[int] = Field(default=0, ge=0)
    category: Optional[str] = Field(default=None)

class MergeRequest(BaseModel):
    github_results: List[GitHubItem] = Field(default_factory=list)
    webpilot_results: List[WebPilotResult] = Field(default_factory=list)
    mql5_results: List[MQL5Item] = Field(default_factory=list)
    content_limit: Optional[int] = Field(
        default=getattr(settings, "DEFAULT_CONTENT_LIMIT", 1000),
        ge=100,
        le=5000
    )

class MergedItem(BaseModel):
    source: str
    title: str
    content: str
    link: str
    metadata: Dict[str, Any]  # ✅ Поправено
    relevance_score: float
    last_updated: Optional[datetime]

def calculate_relevance(item: dict) -> float:
    score = 0.0
    if item['source'] == 'GitHub':
        score = item.get('stars', 0) * 0.1
    elif item['source'] == 'WebPilot':
        score = item.get('relevance', 0.0)
    return min(max(score, 0.0), 1.0)

@router.post("/results", response_model=List[MergedItem])
async def merge_results(data: MergeRequest):
    try:
        merged = []

        for item in data.github_results:
            merged.append({
                "source": "GitHub",
                "title": item.name,
                "content": item.description[:data.content_limit],
                "link": str(item.url),
                "metadata": {
                    "stars": item.stars,
                    "language": item.language,
                    "last_updated": item.last_updated
                },
                "relevance_score": calculate_relevance({
                    "source": "GitHub",
                    "stars": item.stars
                }),
                "last_updated": item.last_updated
            })

        for item in data.webpilot_results:
            merged.append({
                "source": item.source or "WebPilot",
                "title": item.title,
                "content": item.content[:data.content_limit],
                "link": str(item.link),
                "metadata": {
                    "source": item.source,
                    "relevance": item.relevance
                },
                "relevance_score": item.relevance,
                "last_updated": datetime.now()
            })

        for item in data.mql5_results:
            merged.append({
                "source": "MQL5",
                "title": item.title,
                "content": item.description[:data.content_limit],
                "link": str(item.url),
                "metadata": {
                    "votes": item.votes,
                    "category": item.category
                },
                "relevance_score": calculate_relevance({
                    "source": "MQL5",
                    "votes": item.votes
                }),
                "last_updated": None
            })

        merged.sort(key=lambda x: x['relevance_score'], reverse=True)

        return merged

    except Exception as e:
        logger.error(f"Merge error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Data merging failed: {str(e)}"
        )
