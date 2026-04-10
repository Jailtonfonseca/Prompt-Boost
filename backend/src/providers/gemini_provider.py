"""
Gemini Provider - Integration with Google Gemini API
"""

import logging

import google.generativeai as genai

from src.providers.base import CompletionResponse, LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google Gemini API key
            model: Model to use (default: gemini-2.0-flash)
        """
        super().__init__(api_key)
        self.model = model
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> CompletionResponse:
        """
        Get completion from Gemini.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            CompletionResponse with generated text
        """
        try:
            # Gemini async generation
            response = await self.client.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                ),
            )

            text = response.text
            # Gemini doesn't provide exact token count, estimate
            tokens_used = len(text.split()) + len(prompt.split())
            stop_reason = response.candidates[0].finish_reason.name if response.candidates else "STOP"

            # Update tracking
            self.total_tokens_used += tokens_used
            cost = self.estimate_cost(tokens_used)
            self.total_cost_usd += cost

            logger.info(
                f"Gemini completion: {tokens_used} tokens (estimated), ${cost:.4f}"
            )

            return CompletionResponse(
                text=text,
                tokens_used=tokens_used,
                stop_reason=stop_reason,
                model=self.model,
                provider="gemini",
            )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def stream_complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ):
        """
        Stream completion from Gemini.
        
        Yields text chunks as they arrive.
        """
        try:
            tokens_count = 0
            
            response = await self.client.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                ),
                stream=True,
            )

            async for chunk in response:
                if chunk.text:
                    tokens_count += len(chunk.text.split())
                    yield chunk.text

            self.total_tokens_used += tokens_count
            cost = self.estimate_cost(tokens_count)
            self.total_cost_usd += cost

        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise

    def get_model_name(self) -> str:
        """Get current model name."""
        return self.model

    def estimate_cost(self, tokens_used: int, model: str = None) -> float:
        """
        Estimate Gemini API cost.
        
        Pricing as of 2024:
        - Gemini 2.0 Flash: $0.075 per 1M input, $0.3 per 1M output
        - Gemini 1.5 Pro: $1.25 per 1M input, $2.50 per 1M output
        """
        model = model or self.model
        
        if "gemini-2" in model:
            return (tokens_used / 1_000_000) * 0.1875  # Average ~$0.1875 per 1M
        elif "1.5-pro" in model:
            return (tokens_used / 1_000_000) * 1.875  # Average ~$1.875 per 1M
        else:
            return (tokens_used / 1_000_000) * 0.1875  # Default to flash pricing
