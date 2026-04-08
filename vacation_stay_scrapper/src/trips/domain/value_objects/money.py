"""
Money Value Object

Represents monetary values with currency.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """
    Immutable Money representation
    
    Value object for handling monetary amounts.
    """
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        """Validate money values"""
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency code is required")
    
    @classmethod
    def from_float(cls, amount: float, currency: str = "USD") -> "Money":
        """Create Money from float value"""
        return cls(amount=Decimal(str(amount)), currency=currency)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
    
    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency}')"
    
    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects"""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)
