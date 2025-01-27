from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixin import UserRelationMixin


class Post(UserRelationMixin, Base):
    # _user_id_nullable: bool = False
    # _user_id_unique: bool = False
    _user_back_populates = "posts"

    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(Text, default="", server_default="")
