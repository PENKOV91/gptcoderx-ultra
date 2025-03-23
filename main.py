from fastapi import FastAPI, Request
from deepseek_api import generate_code, generate_reasoning
from github_search import search_github_repos
from webpilot_search import search_webpilot
from merge import merge_results

app = FastAPI(
    title="GPT-CODER X ULTRA",
    description="""
    Персонализиран GPT агент за създаване на MQL4/MQL5/Python код чрез DeepSeek-Coder-V2 и Reasoner.
    Поддържа извличане от GitHub, WebPilot и MQL5, както и reasoning от DeepSeek R1.
    """,
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "🔥 GPT-CODER X ULTRA backend is live!"}

@app.post("/code/deepseek")
def code_with_deepseek(data: dict):
    """
    Генериране на код с DeepSeek-Coder-V2
    """
    prompt = data.get("prompt", "")
    return generate_code(prompt)

@app.post("/code/reasoner")
def code_with_reasoner(data: dict):
    """
    Генериране на логически анализ чрез DeepSeek Reasoner
    """
    prompt = data.get("prompt", "")
    return generate_reasoning(prompt)

@app.post("/search/github")
def github_search(data: dict):
    """
    Извличане на код/репозитории от GitHub
    """
    query = data.get("query", "")
    return search_github_repos(query)

@app.post("/search/webpilot")
def webpilot_search_endpoint(data: dict):
    """
    Web scraping чрез WebPilot
    """
    link = data.get("link", "")
    query = data.get("query", "")
    return search_webpilot(link, query)

@app.post("/merge/results")
def merge_all(data: dict):
    """
    Обединяване на резултати от GitHub, WebPilot, MQL5
    """
    github_results = data.get("github_results", [])
    webpilot_results = data.get("webpilot_results", {})
    mql5_results = data.get("mql5_results", [])
    return merge_results(github_results, webpilot_results, mql5_results)
