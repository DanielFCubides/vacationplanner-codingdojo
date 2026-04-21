from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Date, Float, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.trips.infrastructure.persistence.models.trip_model import TripModel


class AccommodationModel(Base):
    __tablename__ = "accommodations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    trip_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)

    # price_per_night (Money value object flattened)
    price_per_night_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_per_night_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # total_price (Money value object flattened)
    total_price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_price_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    rating: Mapped[float] = mapped_column(Float, nullable=False)
    amenities: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    trip: Mapped["TripModel"] = relationship("TripModel", back_populates="accommodations")
