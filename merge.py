def merge_search_results(github_results=None, webpilot_results=None, mql5_results=None):
    merged = []

    if github_results:
        for item in github_results:
            merged.append({
                "source": "GitHub",
                "title": item.get("name"),
                "content": item.get("description") or "No description",
                "link": item.get("url")
            })

    if webpilot_results:
        title = webpilot_results.get("title", "WebPilot Page")
        content = webpilot_results.get("content", "")[:1500]  # trim
        link = webpilot_results.get("link", "N/A")
        merged.append({
            "source": "WebPilot",
            "title": title,
            "content": content,
            "link": link
        })

    if mql5_results:
        for item in mql5_results:
            merged.append({
                "source": "MQL5",
                "title": item.get("title", "MQL5 Resource"),
                "content": item.get("description", ""),
                "link": item.get("url", "")
            })

    return merged
