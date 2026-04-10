"""
OpenAI Provider - Integration with OpenAI API
"""

import logging
from typing import Optional

from openai import AsyncOpenAI

from src.providers.base import CompletionResponse, LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
        """
        super().__init__(api_key)
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> CompletionResponse:
        """
        Get completion from OpenAI.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters (top_p, frequency_penalty, etc.)
            
        Returns:
            CompletionResponse with generated text
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            stop_reason = response.choices[0].finish_reason

            # Update tracking
            self.total_tokens_used += tokens_used
            cost = self.estimate_cost(tokens_used)
            self.total_cost_usd += cost

            logger.info(
                f"OpenAI completion: {tokens_used} tokens, ${cost:.4f}"
            )

            return CompletionResponse(
                text=text,
                tokens_used=tokens_used,
                stop_reason=stop_reason or "completed",
                model=self.model,
                provider="openai",
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def stream_complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ):
        """
        Stream completion from OpenAI.
        
        Yields text chunks as they arrive.
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs,
            )

            tokens_count = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    tokens_count += len(text.split())  # Rough estimate
                    yield text

            self.total_tokens_used += tokens_count
            cost = self.estimate_cost(tokens_count)
            self.total_cost_usd += cost

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise

    def get_model_name(self) -> str:
        """Get current model name."""
        return self.model

    def estimate_cost(self, tokens_used: int, model: str = None) -> float:
        """
        Estimate OpenAI API cost.
        
        Pricing as of 2024:
        - gpt-4: $0.03 per 1K input, $0.06 per 1K output
        - gpt-4o: $0.005 per 1K input, $0.015 per 1K output
        - gpt-3.5-turbo: $0.0005 per 1K input, $0.0015 per 1K output
        """
        model = model or self.model
        
        if "gpt-4o" in model:
            return (tokens_used / 1000) * 0.01  # Average ~$0.01 per 1K
        elif "gpt-4" in model:
            return (tokens_used / 1000) * 0.045  # Average ~$0.045 per 1K
        elif "gpt-3.5" in model:
            return (tokens_used / 1000) * 0.001  # Average ~$0.001 per 1K
        else:
            return 0.0
