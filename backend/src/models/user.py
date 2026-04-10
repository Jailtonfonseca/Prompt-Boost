"""
User Model
"""

import secrets
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.models.base import Base, UserMixin


class User(Base, UserMixin):
    """User model for authentication and API access."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Usage tracking
    total_tokens_used: Mapped[int] = mapped_column(default=0, nullable=False)
    sessions_count: Mapped[int] = mapped_column(default=0, nullable=False)
    max_monthly_tokens: Mapped[int] = mapped_column(default=100000, nullable=False)

    # Relationships
    sessions: Mapped[list["RecursionSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: dict) -> None:
        """Initialize user with generated API key if not provided."""
        if not kwargs.get("api_key"):
            kwargs["api_key"] = secrets.token_urlsafe(32)
        super().__init__(**kwargs)

    def is_within_quota(self, tokens: int) -> bool:
        """Check if user is within their token quota."""
        return (self.total_tokens_used + tokens) <= self.max_monthly_tokens

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', api_key='{self.api_key[:8]}...')"


from src.models.session import RecursionSession  # noqa: E402