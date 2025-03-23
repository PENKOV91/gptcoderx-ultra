from fastapi import APIRouter

router = APIRouter()

@router.post("/results")
def merge_results(
    github_results: list = [],
    webpilot_results: dict = {},
    mql5_results: list = []
):
    merged = []

    for item in github_results:
        merged.append({
            "source": "GitHub",
            "title": item.get("name"),
            "content": item.get("description") or "",
            "link": item.get("url")
        })

    if webpilot_results:
        merged.append({
            "source": "WebPilot",
            "title": webpilot_results.get("title", ""),
            "content": webpilot_results.get("content", "")[:1500],
            "link": webpilot_results.get("link", "")
        })

    for item in mql5_results:
        merged.append({
            "source": "MQL5",
            "title": item.get("title", ""),
            "content": item.get("description", ""),
            "link": item.get("url", "")
        })

    return merged
