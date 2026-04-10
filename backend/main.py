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
from pathlib import Path

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 30

rate_limit_store: Dict[str, List[float]] = defaultdict(list)

APP_DIR = Path(__file__).parent
CONFIG_FILE = APP_DIR / ".env"

CONFIG_DEFAULTS = {
    "OPENAI_API_KEY": "",
    "CORS_ORIGINS": "http://localhost:3000",
    "RATE_LIMIT": "30",
    "MODEL": "gpt-4o",
    "TEMPERATURE": "0.7",
    "MAX_TOKENS": "2000"
}

def load_config() -> dict:
    config_data = CONFIG_DEFAULTS.copy()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config_data[key.strip()] = value.strip()
    return config_data

def save_config(config_data: dict):
    with open(CONFIG_FILE, "w") as f:
        f.write("# Prompt-Boost Configuration\n\n")
        for key, value in config_data.items():
            if value:
                f.write(f"{key}={value}\n")

def check_rate_limit(client_ip: str) -> bool:
    global RATE_LIMIT_MAX_REQUESTS
    cfg = load_config()
    RATE_LIMIT_MAX_REQUESTS = int(cfg.get("RATE_LIMIT", 30))
    
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
    version="1.2.0",
    lifespan=lifespan
)

def get_cors_origins():
    cfg = load_config()
    origins = cfg.get("CORS_ORIGINS", "http://localhost:3000")
    return [o.strip() for o in origins.split(",") if o.strip()]

app.add_middleware(
    StarletteCORSMiddleware,
    allow_origins=get_cors_origins(),
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

class ConfigUpdate(BaseModel):
    openai_api_key: Optional[str] = None
    cors_origins: Optional[str] = None
    rate_limit: Optional[int] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class ConfigResponse(BaseModel):
    cors_origins: str
    rate_limit: int
    model: str
    temperature: float
    max_tokens: int
    api_key_configured: bool

class TestApiKeyRequest(BaseModel):
    api_key: str

class TestApiKeyResponse(BaseModel):
    success: bool
    message: str
    model: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "API is running", "version": "1.2.0"}

@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    cfg = load_config()
    return ConfigResponse(
        cors_origins=cfg.get("CORS_ORIGINS", "http://localhost:3000"),
        rate_limit=int(cfg.get("RATE_LIMIT", 30)),
        model=cfg.get("MODEL", "gpt-4o"),
        temperature=float(cfg.get("TEMPERATURE", 0.7)),
        max_tokens=int(cfg.get("MAX_TOKENS", 2000)),
        api_key_configured=bool(cfg.get("OPENAI_API_KEY", ""))
    )

@app.post("/api/config")
async def update_config(config_data: ConfigUpdate):
    cfg = load_config()
    
    if config_data.openai_api_key is not None:
        cfg["OPENAI_API_KEY"] = config_data.openai_api_key.strip()
    if config_data.cors_origins is not None:
        cfg["CORS_ORIGINS"] = config_data.cors_origins
    if config_data.rate_limit is not None:
        cfg["RATE_LIMIT"] = str(config_data.rate_limit)
    if config_data.model is not None:
        cfg["MODEL"] = config_data.model
    if config_data.temperature is not None:
        cfg["TEMPERATURE"] = str(config_data.temperature)
    if config_data.max_tokens is not None:
        cfg["MAX_TOKENS"] = str(config_data.max_tokens)
    
    save_config(cfg)
    
    return {"success": True, "message": "Configurações salvas com sucesso!"}

@app.post("/api/config/test", response_model=TestApiKeyResponse)
async def test_api_key(request: TestApiKeyRequest):
    if not request.api_key or not request.api_key.strip():
        return TestApiKeyResponse(success=False, message="API key não fornecida.")
    
    try:
        client = openai.OpenAI(api_key=request.api_key.strip())
        response = client.models.list()
        default_model = client.models.retrieve("gpt-4o")
        return TestApiKeyResponse(
            success=True,
            message="Conexão bem-sucedida!",
            model=default_model.id
        )
    except openai.AuthenticationError:
        return TestApiKeyResponse(success=False, message="API key inválida.")
    except openai.RateLimitError:
        return TestApiKeyResponse(success=False, message="Rate limit excedido.")
    except Exception as e:
        return TestApiKeyResponse(success=False, message=f"Erro: {str(e)}")

@app.post("/api/improve-prompt", response_model=ImprovedPromptResponse)
async def improve_prompt(request: PromptRequest, req: Request):
    client_ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    cfg = load_config()
    api_key = cfg.get("OPENAI_API_KEY", "")
    
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key não configurada. Acesse Configurações para adicionar."
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
            model=cfg.get("MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": enhancement_instruction},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=int(cfg.get("MAX_TOKENS", 2000)),
            temperature=float(cfg.get("TEMPERATURE", 0.7))
        )

        improved_prompt_text = completion.choices[0].message.content.strip()

        return ImprovedPromptResponse(
            original_prompt=request.prompt,
            improved_prompt=improved_prompt_text
        )

    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="API key da OpenAI inválida.")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit da OpenAI excedido.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.post("/api/prompts", response_model=ShareResponse)
async def share_prompt(request: ShareRequest):
    if len(request.original_prompt) > 50000 or len(request.improved_prompt) > 50000:
        raise HTTPException(status_code=400, detail="Prompt muito longo. Máximo 50000 caracteres.")

    try:
        share_id = database.save_prompt(request.original_prompt, request.improved_prompt)
        return ShareResponse(share_id=share_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar prompt: {str(e)}")

@app.get("/api/prompts/{prompt_id}", response_model=PromptDetails)
async def get_shared_prompt(prompt_id: str):
    prompt = database.get_prompt(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")
    return PromptDetails(
        id=prompt["id"],
        original_prompt=prompt["original_prompt"],
        improved_prompt=prompt["improved_prompt"]
    )

@app.post("/api/prompts/{prompt_id}/publish", status_code=204)
async def publish_shared_prompt(prompt_id: str):
    prompt = database.get_prompt(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")

    try:
        database.publish_prompt(prompt_id)
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao publicar prompt: {str(e)}")

@app.get("/api/gallery", response_model=GalleryResponse)
async def get_gallery():
    try:
        prompts = database.get_public_prompts()
        return GalleryResponse(prompts=[GalleryItem(**dict(p)) for p in prompts])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar galeria: {str(e)}")