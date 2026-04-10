"""
RecursionSession Model - Tracks recursive reasoning sessions
"""

from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.models.base import Base


class TechniqueEnum(PyEnum):
    """Supported recursion techniques."""

    SELF_REFINE = "self_refine"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    GRAPH_OF_THOUGHTS = "graph_of_thoughts"
    MCTS = "mcts"
    MULTI_AGENT_DEBATE = "multi_agent_debate"
    ALIGNMENT = "alignment"
    AUTOFORMAL = "autoformal"


class SessionStatus(PyEnum):
    """Session status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecursionSession(Base):
    """Recursion session model - tracks each execution."""

    __tablename__ = "recursion_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # Request details
    technique: Mapped[str] = mapped_column(
        Enum(TechniqueEnum),
        nullable=False,
        index=True,
    )
    initial_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Response details
    final_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(SessionStatus),
        default=SessionStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Metrics
    iterations_count: Mapped[int] = mapped_column(default=0, nullable=False)
    tokens_used: Mapped[int] = mapped_column(default=0, nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rer_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_usd: Mapped[float] = mapped_column(default=0.0, nullable=False)

    # Timing
    started_at: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    iterations: Mapped[list["IterationRecord"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<RecursionSession(id={self.id}, technique='{self.technique.value}', "
            f"status='{self.status.value}', quality={self.quality_score})>"
        )


from src.models.user import User  # noqa: E402
from src.models.iteration import IterationRecord  # noqa: E402