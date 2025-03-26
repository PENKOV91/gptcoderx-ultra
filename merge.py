from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class GitHubItem(BaseModel):
    name: str = ""
    description: str = ""
    url: str = ""

class WebPilotResult(BaseModel):
    title: str = ""
    content: str = ""
    link: str = ""

class MQL5Item(BaseModel):
    title: str = ""
    description: str = ""
    url: str = ""

class MergeRequest(BaseModel):
    github_results: List[GitHubItem] = []
    webpilot_results: WebPilotResult = WebPilotResult()
    mql5_results: List[MQL5Item] = []

@router.post("/results")
def merge_results(data: MergeRequest):
    merged = []

    for item in data.github_results:
        merged.append({
            "source": "GitHub",
            "title": item.name,
            "content": item.description or "",
            "link": item.url
        })

    if data.webpilot_results and data.webpilot_results.title:
        merged.append({
            "source": "WebPilot",
            "title": data.webpilot_results.title,
            "content": data.webpilot_results.content[:1500],
            "link": data.webpilot_results.link
        })

    for item in data.mql5_results:
        merged.append({
            "source": "MQL5",
            "title": item.title,
            "content": item.description,
            "link": item.url
        })

    return merged
