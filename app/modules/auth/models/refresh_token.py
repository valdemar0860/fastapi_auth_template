from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Text, String, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.base import Base

if TYPE_CHECKING:
    from modules.user.models import User


class RefreshToken(Base):
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID користувача"
    )

    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
        comment="Refresh токен (хешований)"
    )

    device_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="ID пристрою користувача"
    )
    device_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Назва пристрою (iPhone, Chrome на Windows, etc.)"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP адреса при створенні токена"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User Agent браузера"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Чи активний токен"
    )
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
        comment="Дата закінчення токена"
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Остання дата використання токена"
    )

    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"RefreshToken(id={self.id}, user_id={self.user_id}, device={self.device_name})"

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired