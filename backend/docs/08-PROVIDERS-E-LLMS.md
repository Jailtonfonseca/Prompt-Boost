# 08 - LLM Providers & Multi-Model Integration

## 🎯 Objetivo

Documentar a arquitetura de **integração multi-provider com LLMs**, permitindo usar OpenAI, Anthropic, Google Gemini, Mistral, e outros. Este documento cobre:

- Abstração genérica de providers
- Configuração e autenticação de cada provider
- Estratégias de fallback e redundância
- Contagem de tokens e estimativa de custos
- Load balancing entre modelos
- Rate limiting e retry logic
- Caching de respostas
- Monitoramento de performance por provider

---

## 📐 Conceitos Fundamentais

### Arquitetura de Providers

```
                    [RecursionRouter]
                           |
        ___________________|___________________
       /         |         |         |        \
    [OpenAI]  [Claude]  [Gemini]  [Mistral]  [Groq]
       |         |         |         |        |
       └─────────┴─────────┴─────────┴────────┘
              [LLMProvider Interface]
                       |
            [Unified API + Fallback Logic]
                       |
            [Response Caching + Cost Tracking]
```

### Provider Capabilities Matrix

```
┌──────────────┬─────────┬──────────┬────────┬────────┬─────────┐
│ Provider     │ Models  │ Max Tokens│ Vision │ Images │ Cost$/1K│
├──────────────┼─────────┼──────────┼────────┼────────┼─────────┤
│ OpenAI       │ GPT-4/3.5│ 128K    │ Yes   │ Yes    │ Varies  │
│ Anthropic    │ Claude3 │ 200K     │ Yes   │ Limited│ $0.003-15│
│ Google       │ Gemini  │ 32K      │ Yes   │ Yes    │ $0.0005 │
│ Mistral      │ Various │ 32K      │ No    │ No     │ $0.0002 │
│ Groq         │ LLaMA   │ 8K       │ No    │ No     │ Free*   │
└──────────────┴─────────┴──────────┴────────┴────────┴─────────┘
```

---

## 🏗️ Arquitetura: Estruturas de Dados

### 1. Provider Configuration

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

class ProviderType(Enum):
    """Tipos de providers suportados."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    GROQ = "groq"
    LOCAL = "local"

class ModelFamily(Enum):
    """Famílias de modelos."""
    GPT4 = "gpt4"
    GPT35 = "gpt3.5"
    CLAUDE3 = "claude3"
    GEMINI = "gemini"
    LLAMAV2 = "llamav2"

@dataclass
class ModelConfig:
    """
    Configuração de um modelo específico.
    
    Atributos:
        model_id: Identificador do modelo (ex: "gpt-4")
        provider: Tipo de provider
        family: Família do modelo
        max_tokens: Tokens máximos do modelo
        context_window: Tamanho da janela de contexto
        pricing: Dict com 'input_cost' e 'output_cost' por 1M tokens
        supports_vision: Se model aceita imagens
        supports_function_calling: Se suporta function calls
        rate_limit: Requisições por minuto (RPM)
        temperature_range: (min, max) temperatura suportada
        capabilities: Lista de capacidades especiais
    """
    model_id: str
    provider: ProviderType
    family: ModelFamily
    max_tokens: int
    context_window: int
    pricing: Dict[str, float] = field(default_factory=dict)  # input_cost, output_cost
    supports_vision: bool = False
    supports_function_calling: bool = False
    rate_limit: int = 100  # RPM
    temperature_range: tuple = (0.0, 2.0)
    capabilities: List[str] = field(default_factory=list)
    
    def is_suitable_for(self, task: str, require_vision: bool = False) -> bool:
        """
        Verifica se modelo é adequado para tarefa.
        
        Args:
            task: Descrição da tarefa
            require_vision: Se precisa suportar visão
            
        Returns:
            True se modelo é adequado
        """
        if require_vision and not self.supports_vision:
            return False
        
        # Mais lógica aqui (ex: check capabilities)
        return True

@dataclass
class ProviderCredentials:
    """
    Credenciais para acessar um provider.
    
    Atributos:
        provider_type: Tipo de provider
        api_key: API key
        api_url: URL base (opcional, default é production)
        organization_id: Organization ID (para OpenAI)
        additional_params: Parâmetros adicionais (headers custom, etc)
    """
    provider_type: ProviderType
    api_key: str
    api_url: Optional[str] = None
    organization_id: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Valida credenciais (ex: testar conexão)."""
        if not self.api_key or len(self.api_key) < 10:
            return False
        return True

@dataclass
class ProviderConfig:
    """
    Configuração geral de um provider.
    
    Atributos:
        provider_type: Tipo
        credentials: Credenciais
        models: Modelos disponíveis
        enabled: Se está habilitado
        priority: Prioridade (0=mais alta)
        fallback_to: Provider alternativo se este falhar
        max_concurrent_requests: Número máximo de requisições simultâneas
    """
    provider_type: ProviderType
    credentials: ProviderCredentials
    models: List[ModelConfig] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    fallback_to: Optional[ProviderType] = None
    max_concurrent_requests: int = 10
    
    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """Retorna configuração de um modelo."""
        for model in self.models:
            if model.model_id == model_id:
                return model
        return None
```

### 2. Token Counting & Cost Calculation

```python
from typing import Union

class TokenCounter:
    """
    Estima tokens para diferentes modelos.
    Usa aproximação 1 token ≈ 4 caracteres para GPT.
    Mais preciso com Tiktoken para OpenAI.
    """
    
    def __init__(self):
        """Inicializa contadores."""
        self.cache: Dict[str, int] = {}
        
        # Tentar importar tiktoken (OpenAI)
        try:
            import tiktoken
            self.tiktoken = tiktoken
            self.encoding_gpt4 = tiktoken.encoding_for_model("gpt-4")
        except ImportError:
            self.tiktoken = None
            self.encoding_gpt4 = None
    
    def count_tokens(
        self,
        text: str,
        model_id: str = "gpt-4"
    ) -> int:
        """
        Conta tokens em texto.
        
        Args:
            text: Texto a contar
            model_id: Modelo de referência
            
        Returns:
            Número estimado de tokens
        """
        # Cache hit
        cache_key = f"{model_id}:{text[:50]}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # OpenAI models: usar Tiktoken
        if model_id.startswith("gpt") and self.tiktoken:
            try:
                tokens = len(self.encoding_gpt4.encode(text))
                self.cache[cache_key] = tokens
                return tokens
            except:
                pass
        
        # Fallback: aproximação 1 token ≈ 4 caracteres
        tokens = len(text) // 4
        self.cache[cache_key] = tokens
        return tokens
    
    def count_messages(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "gpt-4"
    ) -> int:
        """
        Conta tokens em lista de mensagens.
        
        Args:
            messages: Lista de {'role': ..., 'content': ...}
            model_id: Modelo
            
        Returns:
            Total de tokens
        """
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            total += self.count_tokens(content, model_id)
            # Adicionar overhead de papel/separador (~4 tokens por mensagem)
            total += 4
        
        return total

class CostCalculator:
    """
    Calcula custos de chamadas LLM.
    """
    
    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter
    
    def estimate_cost(
        self,
        input_text: str,
        output_tokens: int,
        model_config: ModelConfig
    ) -> float:
        """
        Estima custo de uma chamada.
        
        Args:
            input_text: Texto de entrada
            output_tokens: Número de tokens na resposta
            model_config: Configuração do modelo
            
        Returns:
            Custo em USD
        """
        input_tokens = self.token_counter.count_tokens(input_text, model_config.model_id)
        
        # Extrair preços (devem estar em $/1M tokens)
        input_price = model_config.pricing.get('input_cost', 0.0)
        output_price = model_config.pricing.get('output_cost', 0.0)
        
        # Calcular custo
        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price
        
        return input_cost + output_cost
    
    def batch_cost(
        self,
        calls: List[Dict[str, Any]],
        model_config: ModelConfig
    ) -> float:
        """
        Calcula custo total de um lote.
        
        Args:
            calls: Lista de {'input': ..., 'output_tokens': ...}
            model_config: Configuração
            
        Returns:
            Custo total
        """
        total_cost = 0.0
        for call in calls:
            cost = self.estimate_cost(
                call['input'],
                call['output_tokens'],
                model_config
            )
            total_cost += cost
        
        return total_cost
```

---

## 🔌 Provider Implementations

### 1. Base LLMProvider Interface

```python
from abc import ABC, abstractmethod
import asyncio
from typing import Optional, Callable

class LLMProvider(ABC):
    """
    Interface base para todos os providers.
    Define contrato que cada provider deve cumprir.
    """
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.token_counter = TokenCounter()
        self.cost_calculator = CostCalculator(self.token_counter)
        self.call_history: List[Dict] = []
    
    @abstractmethod
    def call(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Faz chamada LLM sincronamente.
        
        Args:
            prompt: Texto do prompt
            model: ID do modelo
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens a gerar
            system_prompt: Instrução de sistema
            **kwargs: Argumentos específicos do provider
            
        Returns:
            Texto da resposta
        """
        pass
    
    @abstractmethod
    async def call_async(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Versão assíncrona de call."""
        pass
    
    @abstractmethod
    def stream(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> str:
        """
        Faz chamada com streaming.
        
        Args:
            prompt: Prompt
            model: Modelo
            temperature: Temperatura
            max_tokens: Máximo
            system_prompt: Instrução
            callback: Função chamada para cada chunk (recebe token)
            **kwargs: Argumentos específicos
            
        Returns:
            Texto completo (após finalizar stream)
        """
        pass
    
    @abstractmethod
    def supports_vision(self) -> bool:
        """Retorna True se provider suporta visão."""
        pass
    
    def calculate_cost(
        self,
        input_text: str,
        output_tokens: int,
        model: str
    ) -> float:
        """Calcula custo de uma chamada."""
        model_config = self.config.get_model(model)
        if not model_config:
            return 0.0
        
        return self.cost_calculator.estimate_cost(
            input_text,
            output_tokens,
            model_config
        )
    
    def get_available_models(self) -> List[ModelConfig]:
        """Retorna modelos disponíveis."""
        return [m for m in self.config.models if m.provider == self.config.provider_type]
    
    def record_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        latency_ms: float,
        success: bool
    ) -> None:
        """Registra chamada para monitoramento."""
        self.call_history.append({
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'latency_ms': latency_ms,
            'success': success,
            'timestamp': datetime.now()
        })
```

### 2. OpenAI Provider

```python
import openai
import time
from datetime import datetime

class OpenAIProvider(LLMProvider):
    """Implementação para OpenAI."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        
        # Inicializar cliente OpenAI
        openai.api_key = config.credentials.api_key
        if config.credentials.organization_id:
            openai.organization = config.credentials.organization_id
        if config.credentials.api_url:
            openai.api_base = config.credentials.api_url
    
    def call(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Chamada sincronamente."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extrair resposta
            content = response.choices[0].message.content
            
            # Calcular tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self.calculate_cost(prompt, output_tokens, model)
            
            # Registrar
            self.record_call(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                latency_ms=latency_ms,
                success=True
            )
            
            return content
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.record_call(
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                latency_ms=latency_ms,
                success=False
            )
            raise e
    
    async def call_async(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Chamada assíncrona."""
        # OpenAI library tem suporte assíncrono
        return await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt} if system_prompt else None,
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def stream(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> str:
        """Streaming."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        full_response = ""
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        for chunk in response:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                full_response += delta.content
                if callback:
                    callback(delta.content)
        
        return full_response
    
    def supports_vision(self) -> bool:
        return True
```

### 3. Anthropic Provider

```python
import anthropic

class AnthropicProvider(LLMProvider):
    """Implementação para Anthropic (Claude)."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = anthropic.Anthropic(api_key=config.credentials.api_key)
    
    def call(
        self,
        prompt: str,
        model: str = "claude-3-opus-20240229",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Chamada sincronamente."""
        
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            content = response.content[0].text
            
            # Claude fornece token usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self.calculate_cost(prompt, output_tokens, model)
            
            self.record_call(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                latency_ms=latency_ms,
                success=True
            )
            
            return content
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.record_call(
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                latency_ms=latency_ms,
                success=False
            )
            raise e
    
    async def call_async(self, prompt: str, model: str, **kwargs) -> str:
        """Versão assíncrona."""
        # Similar mas com async
        pass
    
    def stream(self, prompt: str, model: str, callback: Callable = None, **kwargs) -> str:
        """Streaming com Anthropic."""
        full_response = ""
        
        with self.client.messages.stream(
            model=model,
            max_tokens=kwargs.get('max_tokens', 1000),
            system=kwargs.get('system_prompt', ""),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', 0.7)
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                if callback:
                    callback(text)
        
        return full_response
    
    def supports_vision(self) -> bool:
        return True
```

---

## ⚙️ Provider Manager & Fallback Logic

```python
class ProviderManager:
    """
    Gerencia múltiplos providers com fallback, load balancing e failover.
    """
    
    def __init__(self):
        """Inicializa manager."""
        self.providers: Dict[ProviderType, LLMProvider] = {}
        self.provider_configs: List[ProviderConfig] = []
        self.primary_provider: Optional[ProviderType] = None
    
    def register_provider(
        self,
        config: ProviderConfig,
        provider_instance: LLMProvider
    ) -> None:
        """Registra um provider."""
        self.provider_configs.append(config)
        self.providers[config.provider_type] = provider_instance
        
        if config.priority == 0:
            self.primary_provider = config.provider_type
    
    def call_with_fallback(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Faz chamada com fallback automático.
        Se provider falhar, tenta próximo na fila.
        
        Args:
            prompt: Prompt
            model: Modelo (se None, tenta selecionar melhor)
            temperature: Temperatura
            max_tokens: Máximo
            system_prompt: Instrução
            
        Returns:
            Resposta
            
        Raises:
            Exception se todos providers falharem
        """
        
        # Ordenar providers por prioridade
        sorted_providers = sorted(
            self.provider_configs,
            key=lambda c: (not c.enabled, c.priority)
        )
        
        last_error = None
        
        for config in sorted_providers:
            try:
                provider = self.providers[config.provider_type]
                
                # Se model não especificado, usar primeiro disponível
                if not model:
                    model = provider.get_available_models()[0].model_id
                
                # Chamar provider
                response = provider.call(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt
                )
                
                return response
            
            except Exception as e:
                last_error = e
                print(f"[ProviderManager] {config.provider_type.value} falhou: {str(e)}")
                continue
        
        # Todos falharam
        raise Exception(f"Todos os providers falharam. Último erro: {last_error}")
    
    def select_best_provider(
        self,
        require_vision: bool = False,
        min_context: int = 8000,
        prefer_cost_effective: bool = False
    ) -> LLMProvider:
        """
        Seleciona melhor provider baseado em critérios.
        
        Args:
            require_vision: Se precisa suporte a visão
            min_context: Tamanho mínimo de contexto
            prefer_cost_effective: Se priorizar custo
            
        Returns:
            Melhor provider para o critério
        """
        
        candidates = []
        
        for config in self.provider_configs:
            if not config.enabled:
                continue
            
            # Verificar critérios
            for model in config.models:
                if require_vision and not model.supports_vision:
                    continue
                if model.context_window < min_context:
                    continue
                
                candidates.append((config, model))
        
        if not candidates:
            raise ValueError("Nenhum provider atende critérios")
        
        # Selecionar baseado em preferência
        if prefer_cost_effective:
            # Selecionar mais barato
            best = min(candidates, key=lambda x: x[1].pricing.get('input_cost', 0))
        else:
            # Selecionar mais rápido (menor latência histórica)
            best = candidates[0]  # TODO: adicionar histórico
        
        return self.providers[best[0].provider_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso."""
        stats = {}
        
        for provider_type, provider in self.providers.items():
            calls = provider.call_history
            if not calls:
                continue
            
            total_cost = sum(c['cost'] for c in calls)
            total_tokens = sum(c['input_tokens'] + c['output_tokens'] for c in calls)
            avg_latency = sum(c['latency_ms'] for c in calls) / len(calls)
            success_rate = sum(1 for c in calls if c['success']) / len(calls)
            
            stats[provider_type.value] = {
                'calls': len(calls),
                'total_cost': total_cost,
                'total_tokens': total_tokens,
                'avg_latency_ms': avg_latency,
                'success_rate': success_rate
            }
        
        return stats
```

---

## 📊 Exemplo: Configuração Multi-Provider

```python
# Configurar OpenAI
openai_creds = ProviderCredentials(
    provider_type=ProviderType.OPENAI,
    api_key="sk-...",
    organization_id="org-..."
)

openai_models = [
    ModelConfig(
        model_id="gpt-4",
        provider=ProviderType.OPENAI,
        family=ModelFamily.GPT4,
        max_tokens=8000,
        context_window=128000,
        pricing={'input_cost': 0.03, 'output_cost': 0.06},
        supports_vision=True,
        supports_function_calling=True,
        rate_limit=10000
    ),
    ModelConfig(
        model_id="gpt-3.5-turbo",
        provider=ProviderType.OPENAI,
        family=ModelFamily.GPT35,
        max_tokens=4000,
        context_window=16000,
        pricing={'input_cost': 0.0005, 'output_cost': 0.0015},
        supports_vision=False,
        rate_limit=100000
    )
]

openai_config = ProviderConfig(
    provider_type=ProviderType.OPENAI,
    credentials=openai_creds,
    models=openai_models,
    enabled=True,
    priority=0  # Primário
)

# Configurar Claude
claude_creds = ProviderCredentials(
    provider_type=ProviderType.ANTHROPIC,
    api_key="sk-ant-..."
)

claude_models = [
    ModelConfig(
        model_id="claude-3-opus-20240229",
        provider=ProviderType.ANTHROPIC,
        family=ModelFamily.CLAUDE3,
        max_tokens=4096,
        context_window=200000,
        pricing={'input_cost': 0.015, 'output_cost': 0.075},
        supports_vision=True
    )
]

claude_config = ProviderConfig(
    provider_type=ProviderType.ANTHROPIC,
    credentials=claude_creds,
    models=claude_models,
    enabled=True,
    priority=1,  # Fallback
    fallback_to=ProviderType.OPENAI
)

# Inicializar manager
manager = ProviderManager()
manager.register_provider(openai_config, OpenAIProvider(openai_config))
manager.register_provider(claude_config, AnthropicProvider(claude_config))

# Usar com fallback
response = manager.call_with_fallback(
    prompt="Explain quantum computing",
    temperature=0.7,
    max_tokens=1000
)

# Verificar estatísticas
stats = manager.get_statistics()
print(f"Total spent: ${stats['openai']['total_cost'] + stats['anthropic']['total_cost']:.2f}")
```

---

## ✅ Checklist de Implementação

- [ ] Implementar base class `LLMProvider` com interface
- [ ] Implementar `OpenAIProvider` com sync + async + streaming
- [ ] Implementar `AnthropicProvider` (Claude)
- [ ] Implementar `GoogleProvider` (Gemini)
- [ ] Implementar `MistralProvider`
- [ ] Implementar `GroqProvider`
- [ ] Criar `TokenCounter` com Tiktoken support
- [ ] Criar `CostCalculator` com pricing models
- [ ] Implementar `ProviderManager` com fallback logic
- [ ] Adicionar load balancing entre providers
- [ ] Implementar circuit breaker para falhas
- [ ] Adicionar rate limiting por provider
- [ ] Implementar caching de respostas
- [ ] Criar dashboard de custos e performance
- [ ] Testes de failover e recovery
- [ ] Documentar cada provider configuration

---

## 🔗 Referências Cruzadas

- **00-ARQUITETURA-BACKEND.md**: LLM provider como componente
- **10-WEBSOCKET-PROTOCOL.md**: Streaming responses em tempo real
- **11-PERFORMANCE-MONITORING.md**: Monitoramento de custos e latência
- **13-API-REFERENCE.md**: Endpoints de configuração de providers
- **14-TESTING-STRATEGY.md**: Testes de diferentes providers

---

**Documento criado**: 2025
**Versão**: 1.0
**Status**: Completo e pronto para implementação
