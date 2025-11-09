from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Text, String, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.base import Base

if TYPE_CHECKING:
    from modules.user.models import User


class TwoFactorAuth(Base):
    """
    Модель двофакторної аутентифікації (2FA).

    Зберігає налаштування 2FA для користувачів.
    """

    # Зв'язок з користувачем (один користувач - один 2FA)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="ID користувача"
    )

    # Секретний ключ для TOTP
    secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Секретний ключ для генерації кодів"
    )

    # Статус
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Чи увімкнена 2FA"
    )

    # Дата активації
    enabled_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Дата активації 2FA"
    )

    # Backup коди для відновлення доступу
    backup_codes: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="Backup коди (хешовані)"
    )

    # Дата останнього використання
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Дата останнього використання 2FA"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"TwoFactorAuth(id={self.id}, user_id={self.user_id}, enabled={self.is_enabled})"