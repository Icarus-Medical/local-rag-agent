from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from api.raglib import query, build_prompt, ollama

app = FastAPI(title="Local RAG API", version="0.1.0")

class Ask(BaseModel):
    text: str
    top_k: int = 5
    temperature: float = 0.2
    max_tokens: int = 512
    product: str | None = None

@app.get("/healthz")
def health():
    return {"status": "ok"}

'''
@app.post("/answer")
async def answer(body: Ask):
    retrieved = await query(body.text, k=body.top_k)
    prompt, sources = build_prompt(body.text, retrieved["hits"])
    out = await ollama.generate(prompt, temperature=body.temperature, max_tokens=body.max_tokens)
    return {"text": out, "sources": sources}
'''

@app.post("/answer")
async def answer(body: Ask):
    retrieved = await query(body.text, k=body.top_k, product=body.product)
    prompt, sources = build_prompt(body.text, retrieved["hits"], product=body.product)
    out = await ollama.generate(prompt, temperature=body.temperature, max_tokens=body.max_tokens)
    return {"text": out, "sources": sources}