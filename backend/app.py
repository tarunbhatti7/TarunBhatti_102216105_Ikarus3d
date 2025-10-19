from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from utils.config import settings
from models.recommender import ContentRecommender
from fastapi.responses import StreamingResponse
import requests


app = FastAPI(title="Ikarus Product Recommendation API", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reco = ContentRecommender(settings.DATA_PATH, settings.VECTOR_INDEX_DIR, settings.EMBEDDING_MODEL_NAME)

class RecommendReq(BaseModel):
    prompt: str
    top_k: int = 6
    filters: Optional[Dict[str, Any]] = None

@app.get('/ping')
def ping():
    return {"ok": True}

@app.post('/recommend')
def recommend(req: RecommendReq):
    items = reco.recommend(req.prompt, req.top_k, req.filters or {})
    return {"items": items}

@app.get('/item/{uniq_id}')
def item(uniq_id: str):
    res = reco.item(uniq_id)
    return res

@app.get('/analytics')
def analytics():
    return reco.analytics()

@app.get("/proxy-image")
def proxy_image(url: str):
    """Fetch external image server-side to avoid hotlink/CORS/mixed-content issues."""
    try:
        # a desktop UA helps some CDNs
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, stream=True, timeout=10, headers=headers)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "image/jpeg")
        return StreamingResponse(r.raw, media_type=ctype)
    except Exception:
        # return a 1x1 transparent PNG if anything fails
        import base64, io
        transparent_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWP4//8/AwAI/AL+qsg7xQAAAABJRU5ErkJggg=="
        )
        return StreamingResponse(io.BytesIO(transparent_png), media_type="image/png")

