import os
import requests

GITHUB_API = "https://api.github.com/search/repositories"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def search_github_repos(query: str):
    params = {"q": query}
    response = requests.get(GITHUB_API, headers=HEADERS, params=params)

    if response.status_code != 200:
        return {"error": f"GitHub API error: {response.status_code}", "details": response.text}

    data = response.json()
    results = []

    for item in data.get("items", []):
        results.append({
            "name": item.get("full_name"),
            "url": item.get("html_url"),
            "description": item.get("description"),
            "stars": item.get("stargazers_count")
        })

    return results
