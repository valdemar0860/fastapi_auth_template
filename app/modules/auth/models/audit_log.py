from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Text, String, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.base import Base

if TYPE_CHECKING:
    from modules.user.models import User


class AuditLog(Base):
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID користувача (NULL якщо видалений)"
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Тип дії (user.login, user.register, role.assign, etc.)"
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Категорія події (auth, users, roles, etc.)"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Опис події"
    )

    # Додаткові дані в JSON форматі
    other_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Додаткові дані події (JSON)"
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        index=True,
        comment="IP адреса"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User Agent"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="Статус виконання (success, failed, warning)"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Повідомлення про помилку (якщо була)"
    )

    user: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})"
