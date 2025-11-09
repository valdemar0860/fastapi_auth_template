from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Text, String, ForeignKey, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.base import Base

if TYPE_CHECKING:
    from modules.user.models import User


class OAuthAccount(Base):
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID користувача"
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Назва OAuth провайдера"
    )

    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="ID користувача у провайдера"
    )

    provider_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Email отриманий від провайдера"
    )

    access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Access token від провайдера"
    )

    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Refresh token від провайдера"
    )

    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Дата закінчення access token"
    )

    provider_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Додаткові дані від провайдера (JSON)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Чи активний OAuth акаунт"
    )

    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"OAuthAccount(id={self.id}, provider={self.provider}, user_id={self.user_id})"

    class Config:
        __table_args__ = (
            UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
            {"comment": "OAuth акаунти користувачів"},
        )
