from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import openai
import google.generativeai as genai

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        pass


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content.strip()
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            models = self.client.models.list()
            return {"success": True, "message": f"Conectado. {len(models.data)} modelos disponíveis."}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def list_models(self) -> List[str]:
        try:
            models = self.client.models.list()
            return [m.id for m in models.data if "gpt" in m.id.lower() or "o1" in m.id.lower()]
        except:
            return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]


class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2000)
            }
        )
        return response.text.strip()
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            model = genai.GenerativeModel(self.model)
            model.generate_content("Test")
            return {"success": True, "message": "Conectado ao Google Gemini."}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def list_models(self) -> List[str]:
        try:
            models = genai.list_models()
            return [m.name.split("/")[-1] for m in models if "generateContent" in m.supported_generation_methods]
        except:
            return ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]


class xAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "grok-2"):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content.strip()
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return {"success": True, "message": "Conectado ao xAI Grok."}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def list_models(self) -> List[str]:
        return ["grok-2", "grok-2-vision-1212", "grok-beta"]


class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "openai/gpt-4o", base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content.strip()
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            models = self.client.models.list()
            return {"success": True, "message": f"Conectado. {len(models.data)} modelos disponíveis."}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def list_models(self) -> List[str]:
        return [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.1-405b-instruct",
            "mistralai/mixtral-8x22b-instruct",
            "google/gemini-pro-1.5",
            "deepseek/deepseek-chat"
        ]


class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content.strip()
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return {"success": True, "message": "Conectado ao Groq."}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def list_models(self) -> List[str]:
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma-2-9b-it"
        ]


PROVIDER_MODELS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview", "o1-mini"]
    },
    "google": {
        "name": "Google Gemini",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b"]
    },
    "xai": {
        "name": "xAI Grok",
        "models": ["grok-2", "grok-2-vision-1212", "grok-beta"]
    },
    "openrouter": {
        "name": "OpenRouter",
        "models": [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.1-405b-instruct",
            "mistralai/mixtral-8x22b-instruct",
            "google/gemini-pro-1.5",
            "deepseek/deepseek-chat"
        ]
    },
    "groq": {
        "name": "Groq",
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma-2-9b-it"
        ]
    }
}


def create_provider(provider_type: str, api_key: str, model: str, base_url: Optional[str] = None) -> BaseProvider:
    if provider_type == "openai":
        return OpenAIProvider(api_key, model, base_url)
    elif provider_type == "google":
        return GoogleProvider(api_key, model)
    elif provider_type == "xai":
        return xAIProvider(api_key, model)
    elif provider_type == "openrouter":
        return OpenRouterProvider(api_key, model, base_url)
    elif provider_type == "groq":
        return GroqProvider(api_key, model)
    else:
        raise ValueError(f"Unknown provider: {provider_type}")