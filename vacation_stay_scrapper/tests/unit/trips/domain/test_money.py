"""
Unit tests for the Money value object.

Amounts must always be Decimal: Postgres returns Decimal, request schemas
return float, and the two cannot be added together.
"""
from decimal import Decimal

from src.trips.domain.value_objects.money import Money


class TestMoneyAmountCoercion:

    def test_float_amount_is_stored_as_decimal(self):
        money = Money(0.0, "USD")

        assert isinstance(money.amount, Decimal)
        assert money.amount == Decimal("0")

    def test_int_amount_is_stored_as_decimal(self):
        assert isinstance(Money(5, "USD").amount, Decimal)

    def test_float_coercion_avoids_binary_float_noise(self):
        assert Money(150.1, "USD").amount == Decimal("150.1")

    def test_decimal_and_float_built_money_can_be_added(self):
        from_db = Money(Decimal("10.00"), "USD")
        from_request = Money(1.5, "USD")

        assert (Money.zero("USD") + from_db + from_request).amount == Decimal("11.50")
