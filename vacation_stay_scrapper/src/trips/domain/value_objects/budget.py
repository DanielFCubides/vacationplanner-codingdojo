"""
Budget Value Object

Represents trip budget with categories.
"""
from dataclasses import dataclass, field
from typing import List

from .money import Money


@dataclass(frozen=True)
class BudgetCategory:
    """
    Budget category with planned and spent amounts
    """
    category: str
    planned: Money
    spent: Money
    
    @property
    def remaining(self) -> Money:
        """Calculate remaining budget"""
        return self.planned - self.spent
    
    @property
    def is_over_budget(self) -> bool:
        """Check if category is over budget"""
        return self.spent.amount > self.planned.amount


@dataclass
class Budget:
    """
    Trip budget with total and category breakdown
    
    Tracks planned vs actual spending across categories.
    """
    total: Money
    spent: Money
    categories: List[BudgetCategory] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate budget data"""
        if self.total.amount < 0:
            raise ValueError("Total budget cannot be negative")
        if self.spent.amount < 0:
            raise ValueError("Spent amount cannot be negative")
    
    @property
    def remaining(self) -> Money:
        """Calculate remaining budget"""
        return Money(
            amount=self.total.amount - self.spent.amount,
            currency=self.total.currency
        )
    
    @property
    def percentage_spent(self) -> float:
        """Calculate percentage of budget spent"""
        if self.total.amount == 0:
            return 0.0
        return (self.spent.amount / self.total.amount) * 100
    
    @property
    def is_over_budget(self) -> bool:
        """Check if over total budget"""
        return self.spent.amount > self.total.amount
    
    def recalculate_spent(self, flights, accommodations, activities) -> "Budget":
        """
        Return a new Budget whose ``spent`` is derived from committed children.

        ``spent`` = confirmed flights + confirmed accommodations + booked
        activities (see ADR-003). Pending and cancelled children are excluded.
        ``total`` and ``categories`` are carried over unchanged.
        """
        total_spent = Money.zero(self.total.currency)
        for flight in flights:
            if flight.is_confirmed():
                total_spent = total_spent + flight.price
        for accommodation in accommodations:
            if accommodation.is_confirmed():
                total_spent = total_spent + accommodation.total_price
        for activity in activities:
            if activity.is_booked():
                total_spent = total_spent + activity.cost
        return Budget(
            total=self.total,
            spent=total_spent,
            categories=self.categories,
        )

    def add_category(self, category: BudgetCategory):
        """Add a budget category"""
        # Note: This creates a new Budget since it's frozen
        # In practice, you'd create a new Budget instance
        pass
    
    def __str__(self) -> str:
        return f"Budget: {self.spent} / {self.total} ({self.percentage_spent:.1f}%)"
