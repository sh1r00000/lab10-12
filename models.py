"""Моделі навчальної системи аналізу продажів із XML."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class SaleItem:
    sku: str
    name: str
    category: str
    quantity: int
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Order:
    order_id: str
    order_date: date
    city: str
    status: str
    items: tuple[SaleItem, ...]

    @property
    def amount(self) -> Decimal:
        return sum((item.total for item in self.items), Decimal("0"))


@dataclass(frozen=True)
class Selection:
    city: str | None = None
    category: str | None = None
    start: date | None = None
    end: date | None = None
