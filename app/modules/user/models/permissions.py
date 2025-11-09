from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from modules.user.models.relations import role_permissions
if TYPE_CHECKING:
    from modules.user.models.roles import Role


class Permission(Base):
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Назва дозволу (формат: resource.action)"
    )
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Відображувана назва дозволу"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Опис дозволу"
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Категорія дозволу (users, products, orders, etc.)"
    )

    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"Permission(id={self.id}, name={self.name})"