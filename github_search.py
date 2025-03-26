import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

class GitHubQuery(BaseModel):
    query: str
    per_page: int = 10  # по подразбиране максимум 10 резултата

@router.post("/github")
def search_github_repos(data: GitHubQuery):
    url = "https://api.github.com/search/repositories"
    params = {
        "q": data.query,
        "per_page": min(data.per_page, 30)  # GitHub максимум = 100, но за бързо API – 30 е супер
    }

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"GitHub API error: {response.text}"
        )

    items = response.json().get("items", [])
    results = []
    for item in items:
        results.append({
            "name": item.get("full_name"),
            "url": item.get("html_url"),
            "description": item.get("description"),
            "stars": item.get("stargazers_count"),
            "language": item.get("language")
        })
    return results
