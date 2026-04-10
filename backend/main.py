import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List, Optional
import openai
from decouple import config
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware
import database
import time
from collections import defaultdict
from typing import Dict

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 30

rate_limit_store: Dict[str, List[float]] = defaultdict(list)

def check_rate_limit(client_ip: str) -> bool:
    current_time = time.time()
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip]
        if current_time - t < RATE_LIMIT_WINDOW
    ]
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    rate_limit_store[client_ip].append(current_time)
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(
    title="Prompt-Boost API",
    description="API para melhorar prompts usando IA.",
    version="1.1.0",
    lifespan=lifespan
)

OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
CORS_ORIGINS = config("CORS_ORIGINS", default="http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    StarletteCORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

    @field_validator("prompt")
    @classmethod
    def prompt_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()[:10000]

class ImprovedPromptResponse(BaseModel):
    original_prompt: str
    improved_prompt: str

class ShareRequest(BaseModel):
    original_prompt: str
    improved_prompt: str

    @field_validator("original_prompt", "improved_prompt")
    @classmethod
    def prompts_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()

class ShareResponse(BaseModel):
    share_id: str

class PromptDetails(BaseModel):
    id: str
    original_prompt: str
    improved_prompt: str

class GalleryItem(BaseModel):
    id: str
    original_prompt: str
    improved_prompt: str

class GalleryResponse(BaseModel):
    prompts: List[GalleryItem]

@app.get("/")
def read_root():
    return {"status": "API is running", "version": "1.1.0"}

@app.post("/api/improve-prompt", response_model=ImprovedPromptResponse)
async def improve_prompt(request: PromptRequest, req: Request):
    client_ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    api_key = OPENAI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured on server. Please set OPENAI_API_KEY environment variable."
        )

    try:
        client = openai.OpenAI(api_key=api_key)

        enhancement_instruction = (
            "You are an expert prompt engineer. Refine the following user prompt to be more clear, "
            "focused, and effective for an LLM. Preserve the original intent and key elements, "
            "but enhance structure, specificity, and clarity. "
            "Respond ONLY with the improved prompt, no explanations.\n\n"
            "Original prompt:"
        )

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": enhancement_instruction},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        improved_prompt_text = completion.choices[0].message.content.strip()

        return ImprovedPromptResponse(
            original_prompt=request.prompt,
            improved_prompt=improved_prompt_text
        )

    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/api/prompts", response_model=ShareResponse)
async def share_prompt(request: ShareRequest):
    if len(request.original_prompt) > 50000 or len(request.improved_prompt) > 50000:
        raise HTTPException(status_code=400, detail="Prompt too long. Maximum 50000 characters.")

    try:
        share_id = database.save_prompt(request.original_prompt, request.improved_prompt)
        return ShareResponse(share_id=share_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {str(e)}")

@app.get("/api/prompts/{prompt_id}", response_model=PromptDetails)
async def get_shared_prompt(prompt_id: str):
    prompt = database.get_prompt(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    return PromptDetails(
        id=prompt["id"],
        original_prompt=prompt["original_prompt"],
        improved_prompt=prompt["improved_prompt"]
    )

@app.post("/api/prompts/{prompt_id}/publish", status_code=204)
async def publish_shared_prompt(prompt_id: str):
    prompt = database.get_prompt(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found.")

    try:
        database.publish_prompt(prompt_id)
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish prompt: {str(e)}")

@app.get("/api/gallery", response_model=GalleryResponse)
async def get_gallery():
    try:
        prompts = database.get_public_prompts()
        return GalleryResponse(prompts=[GalleryItem(**dict(p)) for p in prompts])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve gallery: {str(e)}")
