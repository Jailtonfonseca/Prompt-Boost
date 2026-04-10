"""
Recursion API Routes - REST endpoints for recursive reasoning
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.engines import EngineConfig
from src.models import (
    AsyncSessionLocal,
    IterationRecord,
    RecursionSession,
    SessionStatus,
    TechniqueEnum,
    User,
)
from src.providers import ProviderManager
from src.schemas.recursion import (
    ErrorResponse,
    RecursionExecuteRequest,
    RecursionExecuteResponse,
    RecursionSessionResponse,
    TechniquesListResponse,
    IterationSchema,
)
from src.services.recursion_router import RecursionRouter

router = APIRouter(prefix="/api/recursion", tags=["Recursion"])
provider_manager = ProviderManager()


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/techniques", response_model=TechniquesListResponse)
async def list_techniques() -> TechniquesListResponse:
    """Get list of available recursive reasoning techniques."""
    techniques = RecursionRouter.list_techniques()
    details = {
        tech: RecursionRouter.get_technique_info(tech)
        for tech in techniques
    }
    return TechniquesListResponse(
        techniques=techniques,
        count=len(techniques),
        details=details,
    )


@router.post("/execute", response_model=RecursionExecuteResponse)
async def execute_recursion(
    request: RecursionExecuteRequest,
    db: AsyncSession = Depends(get_db),
) -> RecursionExecuteResponse:
    """
    Execute recursive reasoning session.
    
    Creates a new session with the specified technique and returns the result.
    """
    try:
        # Validate technique
        if request.technique not in RecursionRouter.list_techniques():
            raise HTTPException(
                status_code=400,
                detail=f"Unknown technique: {request.technique}",
            )

        # Create engine config
        config = EngineConfig(
            max_iterations=request.max_iterations,
            temperature=request.temperature,
            max_tokens_per_iteration=request.max_tokens_per_iteration,
            quality_threshold=request.quality_threshold,
            provider=request.provider or "openai",
            model=request.model or "gpt-4",
        )

        # Execute engine
        result = await RecursionRouter.execute(
            request.technique,
            request.prompt,
            config,
        )

        # Create session record
        session_id = str(uuid.uuid4())
        session_obj = RecursionSession(
            session_id=session_id,
            user_id=1,  # Default user for now
            technique=TechniqueEnum[request.technique.upper()],
            initial_prompt=request.prompt,
            final_answer=result.final_answer,
            status=SessionStatus[result.status.value.upper()],
            iterations_count=len(result.iterations),
            tokens_used=result.total_tokens_used,
            quality_score=result.quality_score,
            cost_usd=result.total_cost_usd,
            execution_time_ms=result.execution_time_ms,
        )
        db.add(session_obj)
        await db.commit()

        # Convert iterations
        iterations_response = [
            IterationSchema(
                iteration_number=it.iteration_number,
                prompt=it.prompt,
                response=it.response,
                quality_score=it.quality_score,
                tokens_used=it.tokens_used,
                reasoning_trace=it.reasoning_trace,
                candidates=it.candidates,
            )
            for it in result.iterations
        ]

        return RecursionExecuteResponse(
            session_id=session_id,
            technique=request.technique,
            status=result.status.value,
            final_answer=result.final_answer,
            iterations=iterations_response,
            total_tokens_used=result.total_tokens_used,
            total_cost_usd=result.total_cost_usd,
            quality_score=result.quality_score,
            execution_time_ms=result.execution_time_ms,
            error_message=result.error_message,
            metadata=request.metadata or {},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=RecursionSessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> RecursionSessionResponse:
    """
    Retrieve a recursion session by ID.
    
    Returns the complete session record from database.
    """
    try:
        stmt = select(RecursionSession).where(
            RecursionSession.session_id == session_id
        )
        result = await db.execute(stmt)
        session_obj = result.scalar_one_or_none()

        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found")

        return RecursionSessionResponse(
            id=session_obj.id,
            session_id=session_obj.session_id,
            technique=session_obj.technique.value,
            status=session_obj.status.value,
            initial_prompt=session_obj.initial_prompt,
            final_answer=session_obj.final_answer,
            iterations_count=session_obj.iterations_count,
            tokens_used=session_obj.tokens_used,
            quality_score=session_obj.quality_score,
            cost_usd=session_obj.cost_usd,
            execution_time_ms=session_obj.execution_time_ms,
            created_at=session_obj.started_at.isoformat() if session_obj.started_at else "",
            completed_at=session_obj.completed_at.isoformat() if session_obj.completed_at else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    technique: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    List recursion sessions with optional filtering.
    
    Supports pagination and filtering by technique.
    """
    try:
        query = select(RecursionSession)

        if technique:
            query = query.where(RecursionSession.technique == technique)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        sessions = result.scalars().all()

        return {
            "sessions": [
                {
                    "id": s.id,
                    "session_id": s.session_id,
                    "technique": s.technique.value,
                    "status": s.status.value,
                    "quality_score": s.quality_score,
                    "tokens_used": s.tokens_used,
                    "created_at": s.started_at.isoformat() if s.started_at else "",
                }
                for s in sessions
            ],
            "total": len(sessions),
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
