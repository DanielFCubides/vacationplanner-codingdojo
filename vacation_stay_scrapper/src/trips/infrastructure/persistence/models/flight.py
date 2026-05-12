from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.trips.infrastructure.persistence.models.trip import Trip


class Flight(Base):
    __tablename__ = "flights"

    id_: Mapped[str] = mapped_column("id", String, primary_key=True)
    trip_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    airline: Mapped[str] = mapped_column(String, nullable=False)
    flight_number: Mapped[str] = mapped_column(String, nullable=False)

    # Departure airport (Airport value object flattened)
    departure_airport_code: Mapped[str] = mapped_column(String(10), nullable=False)
    departure_airport_city: Mapped[str] = mapped_column(String, nullable=False)
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Arrival airport (Airport value object flattened)
    arrival_airport_code: Mapped[str] = mapped_column(String(10), nullable=False)
    arrival_airport_city: Mapped[str] = mapped_column(String, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    duration: Mapped[str] = mapped_column(String, nullable=False)

    # Price (Money value object flattened)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    stops: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cabin_class: Mapped[str] = mapped_column(String, nullable=False, default="Economy")
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")

    trip: Mapped["Trip"] = relationship("Trip", back_populates="flights")
