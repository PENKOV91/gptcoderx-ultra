from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from deepseek_api import generate_code, generate_reasoning
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "GPT-CODER X ULTRA is running 🚀"}

@app.post("/code/deepseek")
async def code_with_deepseek(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    return generate_code(prompt)

@app.post("/code/reasoner")
async def code_with_reasoner(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    return generate_reasoning(prompt)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
