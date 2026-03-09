from datetime import UTC, datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)  # 'POP' or 'VIDEO'
    title: Mapped[str] = mapped_column(nullable=False)

    module: Mapped[str] = mapped_column(nullable=False)
    theme: Mapped[str | None] = mapped_column(nullable=True)
    subtheme: Mapped[str | None] = mapped_column(nullable=True)
    subsubtheme: Mapped[str | None] = mapped_column(nullable=True)

    keywords: Mapped[str | None] = mapped_column(nullable=True)
    summary: Mapped[str | None] = mapped_column(nullable=True)

    source_url: Mapped[str | None] = mapped_column(nullable=True)
    blob_path: Mapped[str | None] = mapped_column(nullable=True)

    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=utcnow, onupdate=utcnow
    )
