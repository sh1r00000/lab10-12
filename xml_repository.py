"""Читання і перевірка навчального XML-файлу засобами ElementTree."""
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import xml.etree.ElementTree as ET
from models import SaleItem, Order


class DataError(ValueError):
    """Некоректні дані XML або неприпустимий формат файлу."""


class XMLSalesRepository:
    MAX_BYTES = 5_000_000
    ALLOWED_STATUSES = {"completed", "cancelled"}

    def load(self, filename: str | Path) -> list[Order]:
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError(f"XML-файл не знайдено: {path}")
        if path.stat().st_size > self.MAX_BYTES:
            raise DataError("XML-файл завеликий (максимум 5 МБ).")
        raw = path.read_bytes()
        # Працюємо лише з локальним XML без DTD/зовнішніх сутностей.
        if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
            raise DataError("DTD та оголошення ENTITY не підтримуються.")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise DataError(f"Пошкоджений XML: {exc}") from exc
        if root.tag != "salesReport":
            raise DataError("Кореневим тегом має бути <salesReport>.")
        if root.get("currency") != "UAH":
            raise DataError("Для цього прикладу валюта повинна бути UAH.")

        orders: list[Order] = []
        identifiers: set[str] = set()
        for node in root.findall("./order"):
            order_id = self._required_attr(node, "id")
            if order_id in identifiers:
                raise DataError(f"Повторюється ідентифікатор замовлення: {order_id}")
            identifiers.add(order_id)
            try:
                order_date = date.fromisoformat(self._required_attr(node, "date"))
            except ValueError as exc:
                raise DataError(f"Замовлення {order_id}: некоректна дата.") from exc
            city = self._required_attr(node, "city")
            status = self._required_attr(node, "status")
            if status not in self.ALLOWED_STATUSES:
                raise DataError(f"Замовлення {order_id}: невідомий статус {status}.")
            items: list[SaleItem] = []
            for item in node.findall("./item"):
                sku = self._required_attr(item, "sku")
                category = self._required_attr(item, "category")
                name = (item.findtext("name") or "").strip()
                if not name:
                    raise DataError(f"Замовлення {order_id}: товар без назви.")
                try:
                    quantity = int((item.findtext("quantity") or "").strip())
                    price = Decimal((item.findtext("unit_price") or "").strip())
                except (ValueError, InvalidOperation) as exc:
                    raise DataError(f"Замовлення {order_id}: помилка кількості/ціни.") from exc
                if quantity <= 0 or not price.is_finite() or price < 0:
                    raise DataError(f"Замовлення {order_id}: кількість/ціна поза межами.")
                items.append(SaleItem(sku, name, category, quantity, price))
            if not items:
                raise DataError(f"Замовлення {order_id} не містить товарів.")
            orders.append(Order(order_id, order_date, city, status, tuple(items)))
        if not orders:
            raise DataError("XML не містить жодного замовлення.")
        return orders

    @staticmethod
    def _required_attr(node: ET.Element, attr: str) -> str:
        value = (node.get(attr) or "").strip()
        if not value:
            raise DataError(f"У тегу <{node.tag}> немає обов'язкового атрибута '{attr}'.")
        return value
