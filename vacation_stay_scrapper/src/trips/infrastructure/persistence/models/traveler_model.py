from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.trips.infrastructure.persistence.models.trip_model import TripModel


class TravelerModel(Base):
    __tablename__ = "travelers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    trip_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="viewer")
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    trip: Mapped["TripModel"] = relationship("TripModel", back_populates="travelers")
