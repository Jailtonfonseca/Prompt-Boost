"""
LLM Provider Base - Abstract base class for LLM integrations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class CompletionResponse:
    """Response from LLM completion."""
    text: str
    tokens_used: int
    stop_reason: str
    model: str
    provider: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str):
        """Initialize provider with API key."""
        self.api_key = api_key
        self.total_tokens_used = 0
        self.total_cost_usd = 0.0

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> CompletionResponse:
        """
        Get completion from LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Provider-specific parameters
            
        Returns:
            CompletionResponse with generated text and metadata
        """
        pass

    @abstractmethod
    async def stream_complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ):
        """
        Stream completion from LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters
            
        Yields:
            Streamed text chunks
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name being used."""
        pass

    def get_provider_name(self) -> str:
        """Get provider name."""
        return self.__class__.__name__.replace("Provider", "").lower()

    def estimate_cost(self, tokens_used: int, model: str = None) -> float:
        """
        Estimate cost of tokens.
        
        Args:
            tokens_used: Number of tokens
            model: Model name (if different from default)
            
        Returns:
            Estimated cost in USD
        """
        # Override in subclasses with actual pricing
        return 0.0
