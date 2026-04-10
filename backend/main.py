import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, field_validator
from typing import List, Optional
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware
import database
import time
from collections import defaultdict
from typing import Dict
from pathlib import Path
import json

try:
    import recursion
    import openai
    import google.generativeai as genai
    from providers import create_provider, PROVIDER_MODELS
except ImportError:
    import sys
    sys.path.insert(0, '/app')
    import recursion
    import openai
    import google.generativeai as genai
    from providers import create_provider, PROVIDER_MODELS

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 30

rate_limit_store: Dict[str, List[float]] = defaultdict(list)

APP_DIR = Path(__file__).parent
CONFIG_FILE = APP_DIR / ".env"

CONFIG_DEFAULTS = {
    "CORS_ORIGINS": "http://localhost:3000",
    "RATE_LIMIT": "30",
    "TEMPERATURE": "0.7",
    "MAX_TOKENS": "2000",
    "RECURSION_TECHNIQUE": "none",
    "RECURSION_ITERATIONS": "3",
    "RECURSION_SHOW_ITERATIONS": "true",
    "SYSTEM_PROMPT": "",
    "PROVIDER_MAIN": "",
    "PROVIDER_CRITIQUE": ""
}

PROVIDER_CONFIG_DEFAULTS = {
    "provider_type": "openai",
    "model": "gpt-4o",
    "api_key": "",
    "base_url": ""
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

def load_provider_config(prefix: str) -> dict:
    cfg = load_config()
    return {
        "provider_type": cfg.get(f"{prefix}_PROVIDER_TYPE", "openai"),
        "model": cfg.get(f"{prefix}_MODEL", "gpt-4o"),
        "api_key": cfg.get(f"{prefix}_API_KEY", ""),
        "base_url": cfg.get(f"{prefix}_BASE_URL", "")
    }

def save_provider_config(prefix: str, provider_cfg: dict):
    cfg = load_config()
    for key, value in provider_cfg.items():
        cfg[f"{prefix}_{key.upper()}"] = value
    save_config(cfg)

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
    description="API para melhorar prompts usando técnicas de pensamento recursivo.",
    version="1.3.0",
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
    technique: str = "none"
    iterations: int = 1
    history: Optional[List[Dict]] = None

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

class ProviderConfigModel(BaseModel):
    provider_type: str = "openai"
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: Optional[str] = ""

class ConfigUpdate(BaseModel):
    cors_origins: Optional[str] = None
    rate_limit: Optional[int] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    recursion_technique: Optional[str] = None
    recursion_iterations: Optional[int] = None
    recursion_show_iterations: Optional[bool] = None
    system_prompt: Optional[str] = None
    provider_main: Optional[ProviderConfigModel] = None
    provider_critique: Optional[ProviderConfigModel] = None

class ConfigResponse(BaseModel):
    cors_origins: str
    rate_limit: int
    temperature: float
    max_tokens: int
    recursion_technique: str
    recursion_iterations: int
    recursion_show_iterations: bool
    system_prompt: str
    provider_main: ProviderConfigModel
    provider_critique: Optional[ProviderConfigModel] = None

class TestProviderRequest(BaseModel):
    provider_type: str
    api_key: str
    model: str
    base_url: Optional[str] = None

class TestProviderResponse(BaseModel):
    success: bool
    message: str
    models: Optional[List[str]] = None

@app.get("/")
def read_root():
    return {"status": "API is running", "version": "1.3.0"}

@app.get("/api/providers")
async def get_providers():
    return PROVIDER_MODELS

@app.post("/api/config/test-provider", response_model=TestProviderResponse)
async def test_provider(request: TestProviderRequest):
    try:
        provider = create_provider(
            request.provider_type,
            request.api_key,
            request.model,
            request.base_url
        )
        result = provider.test_connection()
        models = provider.list_models()
        return TestProviderResponse(
            success=result["success"],
            message=result["message"],
            models=models[:10]
        )
    except Exception as e:
        return TestProviderResponse(
            success=False,
            message=f"Erro: {str(e)}"
        )

@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    cfg = load_config()
    main_cfg = load_provider_config("MAIN")
    critique_cfg = load_provider_config("CRITIQUE")
    
    return ConfigResponse(
        cors_origins=cfg.get("CORS_ORIGINS", "http://localhost:3000"),
        rate_limit=int(cfg.get("RATE_LIMIT", 30)),
        temperature=float(cfg.get("TEMPERATURE", 0.7)),
        max_tokens=int(cfg.get("MAX_TOKENS", 2000)),
        recursion_technique=cfg.get("RECURSION_TECHNIQUE", "none"),
        recursion_iterations=int(cfg.get("RECURSION_ITERATIONS", 3)),
        recursion_show_iterations=cfg.get("RECURSION_SHOW_ITERATIONS", "true") == "true",
        system_prompt=cfg.get("SYSTEM_PROMPT", "You are an expert prompt engineer. Your task is to refine user prompts to be more clear, focused, and effective for Large Language Models. Respond ONLY with the improved prompt, no explanations."),
        provider_main=ProviderConfigModel(**main_cfg),
        provider_critique=ProviderConfigModel(**critique_cfg) if critique_cfg.get("api_key") else None
    )

@app.post("/api/config")
async def update_config(config_data: ConfigUpdate):
    cfg = load_config()
    
    if config_data.cors_origins is not None:
        cfg["CORS_ORIGINS"] = config_data.cors_origins
    if config_data.rate_limit is not None:
        cfg["RATE_LIMIT"] = str(config_data.rate_limit)
    if config_data.temperature is not None:
        cfg["TEMPERATURE"] = str(config_data.temperature)
    if config_data.max_tokens is not None:
        cfg["MAX_TOKENS"] = str(config_data.max_tokens)
    if config_data.recursion_technique is not None:
        cfg["RECURSION_TECHNIQUE"] = config_data.recursion_technique
    if config_data.recursion_iterations is not None:
        cfg["RECURSION_ITERATIONS"] = str(config_data.recursion_iterations)
    if config_data.recursion_show_iterations is not None:
        cfg["RECURSION_SHOW_ITERATIONS"] = "true" if config_data.recursion_show_iterations else "false"
    if config_data.system_prompt is not None:
        cfg["SYSTEM_PROMPT"] = config_data.system_prompt
    
    if config_data.provider_main is not None:
        save_provider_config("MAIN", config_data.provider_main.model_dump())
    
    if config_data.provider_critique is not None:
        save_provider_config("CRITIQUE", config_data.provider_critique.model_dump())
    
    save_config(cfg)
    
    return {"success": True, "message": "Configurações salvas com sucesso!"}

@app.post("/api/improve-prompt", response_model=ImprovedPromptResponse)
async def improve_prompt(request: PromptRequest, req: Request):
    client_ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    cfg = load_config()
    main_cfg = load_provider_config("MAIN")
    
    if not main_cfg.get("api_key"):
        raise HTTPException(
            status_code=500,
            detail="API key não configurada. Configure um provedor em Configurações."
        )
    
    try:
        main_provider = create_provider(
            main_cfg["provider_type"],
            main_cfg["api_key"],
            main_cfg["model"],
            main_cfg.get("base_url")
        )
        
        technique = cfg.get("RECURSION_TECHNIQUE", "none")
        iterations = int(cfg.get("RECURSION_ITERATIONS", 3))
        system_prompt = cfg.get("SYSTEM_PROMPT", "You are an expert prompt engineer. Your task is to refine user prompts to be more clear, focused, and effective for Large Language Models. Respond ONLY with the improved prompt, no explanations.")
        
        if technique == "self-refine":
            critique_cfg = load_provider_config("CRITIQUE")
            critique_provider = None
            if critique_cfg.get("api_key"):
                critique_provider = create_provider(
                    critique_cfg["provider_type"],
                    critique_cfg["api_key"],
                    critique_cfg["model"],
                    critique_cfg.get("base_url")
                )
            
            result = recursion.self_refine_loop(
                request.prompt,
                main_provider,
                iterations=iterations,
                system_prompt=system_prompt,
                critique_provider=critique_provider
            )
            
            return ImprovedPromptResponse(
                original_prompt=result["original"],
                improved_prompt=result["final"],
                technique="self-refine",
                iterations=iterations,
                history=result["history"]
            )
        
        elif technique == "toT":
            n_versions = min(iterations + 2, 5)
            result = recursion.tree_of_thoughts(
                request.prompt,
                main_provider,
                n_versions=n_versions,
                system_prompt=system_prompt
            )
            
            return ImprovedPromptResponse(
                original_prompt=result["original"],
                improved_prompt=result["final"],
                technique="toT",
                iterations=n_versions,
                history=result.get("versions")
            )
        
        else:
            result = recursion.basic_improve(
                request.prompt,
                main_provider,
                system_prompt=system_prompt
            )
            
            return ImprovedPromptResponse(
                original_prompt=result["original"],
                improved_prompt=result["final"],
                technique="none",
                iterations=1
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

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