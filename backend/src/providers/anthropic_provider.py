"""
Anthropic Provider - Integration with Anthropic Claude API
"""

import logging

from anthropic import AsyncAnthropic

from src.providers.base import CompletionResponse, LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-5-sonnet)
        """
        super().__init__(api_key)
        self.model = model
        self.client = AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> CompletionResponse:
        """
        Get completion from Anthropic Claude.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            CompletionResponse with generated text
        """
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
                **kwargs,
            )

            text = message.content[0].text
            tokens_used = message.usage.output_tokens + message.usage.input_tokens
            stop_reason = message.stop_reason

            # Update tracking
            self.total_tokens_used += tokens_used
            cost = self.estimate_cost(tokens_used)
            self.total_cost_usd += cost

            logger.info(
                f"Anthropic completion: {tokens_used} tokens, ${cost:.4f}"
            )

            return CompletionResponse(
                text=text,
                tokens_used=tokens_used,
                stop_reason=stop_reason or "completed",
                model=self.model,
                provider="anthropic",
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def stream_complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ):
        """
        Stream completion from Anthropic Claude.
        
        Yields text chunks as they arrive.
        """
        try:
            tokens_count = 0
            
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
                **kwargs,
            ) as stream:
                for text in stream.text_stream:
                    tokens_count += len(text.split())  # Rough estimate
                    yield text

            self.total_tokens_used += tokens_count
            cost = self.estimate_cost(tokens_count)
            self.total_cost_usd += cost

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise

    def get_model_name(self) -> str:
        """Get current model name."""
        return self.model

    def estimate_cost(self, tokens_used: int, model: str = None) -> float:
        """
        Estimate Anthropic API cost.
        
        Pricing as of 2024:
        - claude-3-5-sonnet: $0.003 per 1K input, $0.015 per 1K output
        - claude-3-opus: $0.015 per 1K input, $0.075 per 1K output
        - claude-3-sonnet: $0.003 per 1K input, $0.015 per 1K output
        """
        model = model or self.model
        
        if "opus" in model:
            return (tokens_used / 1000) * 0.045  # Average ~$0.045 per 1K
        elif "sonnet" in model:
            return (tokens_used / 1000) * 0.009  # Average ~$0.009 per 1K
        elif "haiku" in model:
            return (tokens_used / 1000) * 0.00075  # Average ~$0.00075 per 1K
        else:
            return 0.0
