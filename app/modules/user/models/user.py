from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from modules.user.models.relations import user_roles
if TYPE_CHECKING:
    from modules.user.models.roles import Role


class User(Base):
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
        comment="Email користувача (NULL для анонімних)"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=True,
        comment="Нікнейм користувача"
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=False,
        index=False,
        nullable=True,
        comment="Відображаєме ім'я"
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Хешований пароль",
    )

    # first_name: Mapped[Optional[str]] = mapped_column(
    #     String(50),
    #     nullable=True,
    #     comment="Ім'я"
    # )
    # last_name: Mapped[Optional[str]] = mapped_column(
    #     String(50),
    #     nullable=True,
    #     comment="Прізвище"
    # )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Номер телефону"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Чи активний користувач"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Чи верифікований email"
    )
    is_anonymous: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Чи це анонімний користувач"
    )
    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Чи заблокований користувач"
    )

    blocked_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Причина блокування"
    )
    blocked_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Дата блокування"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Остання дата входу"
    )

    roles: Mapped[List["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, is_anonymous={self.is_anonymous})"

    # @property
    # def full_name(self) -> str:
    #     if self.first_name and self.last_name:
    #         return f"{self.first_name} {self.last_name}"
    #     return self.first_name or self.last_name or self.username or "Anonymous"

    @property
    def is_superuser(self) -> bool:
        return any(role.name == "superuser" for role in self.roles)
