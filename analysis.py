"""Фільтрація, пошук і групування замовлень."""
from collections import defaultdict
from decimal import Decimal
from models import Order, Selection


class SalesAnalyzer:
    def __init__(self, orders: list[Order]):
        self.orders = orders

    def filter(self, criteria: Selection) -> list[Order]:
        result = []
        for order in self.orders:
            if criteria.city and order.city.casefold() != criteria.city.casefold():
                continue
            if criteria.start and order.order_date < criteria.start:
                continue
            if criteria.end and order.order_date > criteria.end:
                continue
            if criteria.category and not any(
                item.category.casefold() == criteria.category.casefold()
                for item in order.items
            ):
                continue
            result.append(order)
        return result

    @staticmethod
    def summarize(orders: list[Order], category: str | None = None) -> dict:
        """До виторгу входять лише завершені замовлення."""
        by_city: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        by_month: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        sold_units = 0
        revenue = Decimal("0")
        completed = cancelled = 0
        for order in orders:
            if order.status == "cancelled":
                cancelled += 1
                continue
            completed += 1
            for item in order.items:
                if category and item.category.casefold() != category.casefold():
                    continue
                amount = item.total
                sold_units += item.quantity
                revenue += amount
                by_city[order.city] += amount
                by_category[item.category] += amount
                by_month[order.order_date.strftime("%Y-%m")] += amount
        return {
            "all_orders": len(orders), "completed_orders": completed,
            "cancelled_orders": cancelled, "units": sold_units,
            "revenue": revenue,
            "by_city": dict(sorted(by_city.items())),
            "by_category": dict(sorted(by_category.items())),
            "by_month": dict(sorted(by_month.items())),
        }
