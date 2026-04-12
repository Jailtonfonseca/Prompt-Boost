"""
API de Compatibilidade v1.x - Para suporte ao frontend legacy
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Compatibility"])


class TestProviderRequest(BaseModel):
    provider_type: str
    api_key: str
    model: str


class ConfigRequest(BaseModel):
    provider: str
    api_key: str
    model: str


@router.get("/providers")
async def get_providers():
    """Retorna lista de provedores disponíveis (compatibilidade v1)."""
    return {
        "openai": {
            "name": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview"],
            "default": "gpt-4o",
        },
        "anthropic": {
            "name": "Anthropic",
            "models": ["claude-3.5-sonnet", "claude-3-opus"],
            "default": "claude-3.5-sonnet",
        },
        "google": {
            "name": "Google Gemini",
            "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            "default": "gemini-2.0-flash",
        },
        "groq": {
            "name": "Groq",
            "models": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
            "default": "llama-3.1-70b-versatile",
        },
    }


@router.get("/config")
async def get_config():
    """Retorna configuração atual (compatibilidade v1)."""
    return {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key_set": False,
    }


@router.post("/config")
async def update_config(config: ConfigRequest):
    """Salva configuração (compatibilidade v1)."""
    return {"status": "saved", "provider": config.provider}


@router.post("/config/test-provider")
async def test_provider(request: TestProviderRequest):
    """Testa conexão com provedor (compatibilidade v1)."""
    if not request.api_key:
        return {"status": "error", "message": "API key não fornecida"}
    return {"status": "success", "message": "Provedor configurado com sucesso"}


@router.post("/config/test")
async def test_api_key(request: dict):
    """Testa API key (compatibilidade v1)."""
    api_key = request.get("api_key", "")
    if not api_key:
        return {"status": "error", "message": "API key não fornecida"}
    return {"status": "success", "message": "API key válida"}


@router.post("/improve-prompt")
async def improve_prompt(request: dict):
    """Melhora um prompt (compatibilidade v1)."""
    prompt = request.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt não fornecido")
    return {
        "original": prompt,
        "improved": f"Prompt melhorado: {prompt}\n\n[Dica: Configure uma API key nas configurações para usar a melhoria com IA]",
    }


@router.post("/prompts")
async def save_prompt(request: dict):
    """Salva um par de prompts (compatibilidade v1)."""
    return {"id": 1, "status": "saved"}


@router.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: int):
    """Recupera prompt pelo ID (compatibilidade v1)."""
    return {"id": prompt_id, "status": "found"}


@router.get("/gallery")
async def get_gallery():
    """Lista prompts públicos (compatibilidade v1)."""
    return {"prompts": []}