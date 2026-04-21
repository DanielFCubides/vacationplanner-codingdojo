from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.trips.infrastructure.persistence.models.trip_model import TripModel


class BudgetCategoryModel(Base):
    __tablename__ = "budget_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String, nullable=False)

    # planned (Money value object flattened)
    planned_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    planned_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # spent (Money value object flattened)
    spent_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    spent_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    trip: Mapped["TripModel"] = relationship("TripModel", back_populates="budget_categories")
