"""
IterationRecord Model - Individual iterations within a session
"""

import json
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class IterationRecord(Base):
    """Iteration record - tracks each iteration within a session."""

    __tablename__ = "iteration_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("recursion_sessions.id"),
        nullable=False,
        index=True,
    )
    iteration: Mapped[int] = mapped_column(Integer, nullable=False)

    # State at this iteration
    current_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    candidates: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chosen: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Evaluation
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tokens_used: Mapped[int] = mapped_column(default=0, nullable=False)

    # Reasoning trace (for debugging)
    reasoning_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    session: Mapped["RecursionSession"] = relationship(back_populates="iterations")

    def get_candidates(self) -> list[str]:
        """Get candidates as list."""
        if self.candidates:
            return json.loads(self.candidates)
        return []

    def get_reasoning_trace(self) -> dict:
        """Get reasoning trace as dict."""
        if self.reasoning_trace:
            return json.loads(self.reasoning_trace)
        return {}

    def __repr__(self) -> str:
        return f"<IterationRecord(session_id={self.session_id}, iteration={self.iteration}, score={self.quality_score})>"


from src.models.session import RecursionSession  # noqa: E402