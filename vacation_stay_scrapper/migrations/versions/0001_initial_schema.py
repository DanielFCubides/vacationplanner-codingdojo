"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trips",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("destination", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("budget_total_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("budget_total_currency", sa.String(3), nullable=True),
        sa.Column("budget_spent_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("budget_spent_currency", sa.String(3), nullable=True),
        sa.Column("created_at", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "travelers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="viewer"),
        sa.Column("avatar", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "flights",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("airline", sa.String(), nullable=False),
        sa.Column("flight_number", sa.String(), nullable=False),
        sa.Column("departure_airport_code", sa.String(10), nullable=False),
        sa.Column("departure_airport_city", sa.String(), nullable=False),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival_airport_code", sa.String(10), nullable=False),
        sa.Column("arrival_airport_city", sa.String(), nullable=False),
        sa.Column("arrival_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration", sa.String(), nullable=False),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("price_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("stops", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cabin_class", sa.String(), nullable=False, server_default="Economy"),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "accommodations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column("price_per_night_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("price_per_night_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("total_price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_price_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("amenities", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("image", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("cost_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("description", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "budget_categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("planned_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("planned_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("spent_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("spent_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("budget_categories")
    op.drop_table("activities")
    op.drop_table("accommodations")
    op.drop_table("flights")
    op.drop_table("travelers")
    op.drop_table("trips")
