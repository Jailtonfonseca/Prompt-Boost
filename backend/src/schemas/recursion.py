"""
Pydantic Schemas for API Requests and Responses
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================
# Request Schemas
# ============================================

class RecursionExecuteRequest(BaseModel):
    """Request to execute a recursive reasoning session."""

    technique: str = Field(
        ...,
        description="Reasoning technique (self_refine, tree_of_thoughts, etc.)",
    )
    prompt: str = Field(..., description="User input prompt")
    max_iterations: int = Field(5, ge=1, le=20, description="Max iterations")
    quality_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Quality threshold")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="LLM temperature")
    max_tokens_per_iteration: int = Field(2000, ge=100, le=4000, description="Max tokens per iteration")
    provider: Optional[str] = Field(None, description="LLM provider (openai, anthropic, gemini)")
    model: Optional[str] = Field(None, description="Specific model to use")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "technique": "self_refine",
                "prompt": "What is machine learning?",
                "max_iterations": 5,
                "quality_threshold": 0.8,
                "temperature": 0.7,
                "provider": "openai",
            }
        }
    }


class IterationSchema(BaseModel):
    """Single iteration record."""

    iteration_number: int
    prompt: str
    response: str
    quality_score: Optional[float] = None
    tokens_used: int = 0
    reasoning_trace: dict = Field(default_factory=dict)
    candidates: list[str] = Field(default_factory=list)


class RecursionExecuteResponse(BaseModel):
    """Response from executing recursive reasoning."""

    session_id: str = Field(..., description="Unique session ID")
    technique: str = Field(..., description="Technique used")
    status: str = Field(..., description="Session status (completed, failed, pending)")
    final_answer: str = Field(..., description="Final reasoning result")
    iterations: list[IterationSchema] = Field(..., description="All iterations")
    total_tokens_used: int = Field(..., description="Total tokens consumed")
    total_cost_usd: float = Field(..., description="Total cost in USD")
    quality_score: float = Field(..., description="Final quality score (0-1)")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class RecursionSessionResponse(BaseModel):
    """Response for session retrieval."""

    id: int = Field(..., description="Session database ID")
    session_id: str = Field(..., description="Unique session ID")
    technique: str = Field(..., description="Technique used")
    status: str = Field(..., description="Session status")
    initial_prompt: str = Field(..., description="Initial prompt")
    final_answer: Optional[str] = Field(None, description="Final answer")
    iterations_count: int = Field(..., description="Number of iterations")
    tokens_used: int = Field(..., description="Tokens used")
    quality_score: Optional[float] = Field(None, description="Quality score")
    cost_usd: float = Field(..., description="Cost in USD")
    execution_time_ms: Optional[int] = Field(None, description="Execution time")
    created_at: str = Field(..., description="Creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")


# ============================================
# WebSocket Schemas
# ============================================

class StreamMessage(BaseModel):
    """Message for WebSocket streaming."""

    type: str = Field(..., description="Message type (content, status, error, end)")
    data: str = Field(..., description="Message data")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class StreamStartMessage(BaseModel):
    """WebSocket message to start streaming."""

    type: str = "stream_start"
    session_id: str = Field(..., description="Session ID for tracking")
    technique: str = Field(..., description="Technique to use")
    prompt: str = Field(..., description="Input prompt")


# ============================================
# Error Response
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response."""

    status: str = "error"
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[dict[str, Any]] = Field(None, description="Additional details")


# ============================================
# Techniques List Response
# ============================================

class TechniqueInfoSchema(BaseModel):
    """Information about a reasoning technique."""

    name: str
    description: str
    best_for: str
    iterations: int


class TechniquesListResponse(BaseModel):
    """List of available techniques."""

    techniques: list[str]
    count: int
    details: Optional[dict[str, TechniqueInfoSchema]] = None


# ============================================
# Provider Status Response
# ============================================

class ProviderStatusSchema(BaseModel):
    """Status of an LLM provider."""

    name: str
    model: str
    tokens_used: int
    total_cost_usd: float


class ProvidersStatusResponse(BaseModel):
    """Status of all LLM providers."""

    primary: str
    available: list[str]
    providers: dict[str, ProviderStatusSchema]
