from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.trips.infrastructure.persistence.models.trip import Trip


class Activity(Base):
    __tablename__ = "activities"

    id_: Mapped[str] = mapped_column("id", String, primary_key=True)
    trip_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # cost (Money value object flattened)
    cost_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    category: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="activities")
