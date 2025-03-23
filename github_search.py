import os
import requests
from fastapi import APIRouter

router = APIRouter()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

@router.post("/github")
def search_github_repos(query: str):
    url = "https://api.github.com/search/repositories"
    params = {"q": query}

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        return {"error": f"GitHub API error: {response.status_code}", "details": response.text}

    items = response.json().get("items", [])
    results = []
    for item in items:
        results.append({
            "name": item.get("full_name"),
            "url": item.get("html_url"),
            "description": item.get("description"),
            "stars": item.get("stargazers_count")
        })
    return results
