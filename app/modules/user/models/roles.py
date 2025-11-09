from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.base import Base

from modules.user.models.relations import user_roles, role_permissions
if TYPE_CHECKING:
    from modules.user.models.user import User
    from modules.user.models.permissions import Permission


class Role(Base):
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Назва ролі (англійською, lowercase)"
    )
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Відображувана назва ролі"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Опис ролі"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Чи активна роль"
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Чи це системна роль (не можна видалити)"
    )

    users: Mapped[List["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"Role(id={self.id}, name={self.name})"

    def has_permission(self, permission_name: str) -> bool:
        """Перевіряє чи роль має певний дозвіл."""
        return any(perm.name == permission_name for perm in self.permissions)