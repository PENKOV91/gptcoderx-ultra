import requests

WEBPILOT_API = "https://gpts.webpilot.ai/gpts_webpilot_ai__jit_plugin.webPageReader"

def webpilot_deep_search(link: str, query: str):
    payload = {
        "link": link,
        "ur": query,
        "lp": True  # ⬅️ няма l = език, ще работи автоматично
    }

    try:
        response = requests.post(WEBPILOT_API, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
