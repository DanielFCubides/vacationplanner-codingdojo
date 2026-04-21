from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import BigInteger, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database.base import Base


class TripModel(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

    # Budget (value object inlined)
    budget_total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    budget_total_currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    budget_spent_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    budget_spent_currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)

    # Metadata
    created_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    updated_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    travelers: Mapped[List["TravelerModel"]] = relationship(
        "TravelerModel",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    flights: Mapped[List["FlightModel"]] = relationship(
        "FlightModel",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    accommodations: Mapped[List["AccommodationModel"]] = relationship(
        "AccommodationModel",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    activities: Mapped[List["ActivityModel"]] = relationship(
        "ActivityModel",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    budget_categories: Mapped[List["BudgetCategoryModel"]] = relationship(
        "BudgetCategoryModel",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


from src.trips.infrastructure.persistence.models.traveler_model import TravelerModel  # noqa: E402
from src.trips.infrastructure.persistence.models.flight_model import FlightModel  # noqa: E402
from src.trips.infrastructure.persistence.models.accommodation_model import AccommodationModel  # noqa: E402
from src.trips.infrastructure.persistence.models.activity_model import ActivityModel  # noqa: E402
from src.trips.infrastructure.persistence.models.budget_category_model import BudgetCategoryModel  # noqa: E402
