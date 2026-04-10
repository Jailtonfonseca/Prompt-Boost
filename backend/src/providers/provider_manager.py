"""
ProviderManager - Multi-provider management with fallback strategy
"""

import logging
from typing import Optional, Type

from src.config import settings
from src.providers.anthropic_provider import AnthropicProvider
from src.providers.base import CompletionResponse, LLMProvider
from src.providers.gemini_provider import GeminiProvider
from src.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    Manages LLM providers with fallback strategy.
    
    Automatically falls back to alternative providers if primary fails.
    """

    # Available providers
    PROVIDERS: dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
    }

    def __init__(
        self,
        primary: str = "openai",
        fallback_order: Optional[list[str]] = None,
    ):
        """
        Initialize provider manager.
        
        Args:
            primary: Primary provider name
            fallback_order: List of fallback providers (default: all others)
        """
        self.primary = primary
        self.current_provider = primary

        if fallback_order is None:
            fallback_order = [p for p in self.PROVIDERS.keys() if p != primary]

        self.fallback_order = [primary] + fallback_order
        self.providers: dict[str, Optional[LLMProvider]] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize all configured providers."""
        api_keys = {
            "openai": settings.OPENAI_API_KEY,
            "anthropic": settings.ANTHROPIC_API_KEY,
            "gemini": settings.GEMINI_API_KEY,
        }

        for provider_name in self.fallback_order:
            api_key = api_keys.get(provider_name, "")

            if not api_key:
                logger.warning(f"No API key for {provider_name}, skipping")
                self.providers[provider_name] = None
                continue

            try:
                provider_class = self.PROVIDERS[provider_name]
                self.providers[provider_name] = provider_class(api_key)
                logger.info(f"✓ Initialized {provider_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {provider_name}: {e}")
                self.providers[provider_name] = None

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        provider: Optional[str] = None,
        **kwargs,
    ) -> CompletionResponse:
        """
        Get completion with automatic fallback.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            provider: Specific provider to use (uses fallback if fails)
            **kwargs: Additional parameters
            
        Returns:
            CompletionResponse
            
        Raises:
            RuntimeError: If all providers fail
        """
        providers_to_try = [provider] if provider else self.fallback_order

        for prov_name in providers_to_try:
            if prov_name not in self.providers:
                logger.warning(f"Provider {prov_name} not available")
                continue

            prov = self.providers[prov_name]
            if prov is None:
                logger.warning(f"Provider {prov_name} not initialized")
                continue

            try:
                logger.info(f"Trying {prov_name}...")
                result = await prov.complete(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )
                self.current_provider = prov_name
                logger.info(f"✓ Success with {prov_name}")
                return result

            except Exception as e:
                logger.warning(f"✗ {prov_name} failed: {e}")
                if prov_name == providers_to_try[-1]:
                    raise RuntimeError(f"All providers failed. Last error: {e}")
                continue

        raise RuntimeError("No valid provider available")

    async def stream_complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        provider: Optional[str] = None,
        **kwargs,
    ):
        """
        Stream completion with automatic fallback.
        
        Yields text chunks, automatically falling back on error.
        """
        providers_to_try = [provider] if provider else self.fallback_order

        for prov_name in providers_to_try:
            if prov_name not in self.providers:
                logger.warning(f"Provider {prov_name} not available")
                continue

            prov = self.providers[prov_name]
            if prov is None:
                logger.warning(f"Provider {prov_name} not initialized")
                continue

            try:
                logger.info(f"Streaming with {prov_name}...")
                self.current_provider = prov_name
                async for chunk in prov.stream_complete(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                ):
                    yield chunk
                logger.info(f"✓ Streaming completed with {prov_name}")
                return

            except Exception as e:
                logger.warning(f"✗ {prov_name} streaming failed: {e}")
                if prov_name == providers_to_try[-1]:
                    raise RuntimeError(f"All providers failed. Last error: {e}")
                continue

        raise RuntimeError("No valid provider available for streaming")

    def get_current_provider(self) -> str:
        """Get currently active provider."""
        return self.current_provider

    def get_available_providers(self) -> list[str]:
        """Get list of available (initialized) providers."""
        return [
            name for name, prov in self.providers.items() if prov is not None
        ]

    def set_primary_provider(self, provider: str) -> None:
        """
        Set a specific provider as primary.
        
        Args:
            provider: Provider name
            
        Raises:
            ValueError: If provider not available
        """
        if provider not in self.get_available_providers():
            raise ValueError(
                f"Provider {provider} not available. "
                f"Available: {self.get_available_providers()}"
            )
        self.primary = provider
        self.current_provider = provider

    def get_provider_stats(self) -> dict:
        """Get statistics for all providers."""
        stats = {}
        for name, prov in self.providers.items():
            if prov:
                stats[name] = {
                    "model": prov.get_model_name(),
                    "total_tokens": prov.total_tokens_used,
                    "total_cost": prov.total_cost_usd,
                }
        return stats
