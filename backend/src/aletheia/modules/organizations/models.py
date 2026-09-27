import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column

from aletheia.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (CheckConstraint("length(btrim(name)) > 0", name="name_not_blank"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
