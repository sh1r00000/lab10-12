"""Відтворюване створення НАВЧАЛЬНОГО набору з 48 XML-замовлень."""
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from random import Random
import xml.etree.ElementTree as ET


def generate(path: Path) -> None:
    root = ET.Element("salesReport", {"year": "2026", "currency": "UAH",
                                      "dataset": "Навчальний приклад"})
    cities = ["Суми", "Київ", "Львів", "Харків", "Одеса"]
    products = [
        ("BK-101", "Книга «Python для початківців»", "Книги", 390),
        ("BK-102", "Довідник з алгоритмів", "Книги", 540),
        ("EL-201", "Бездротова миша", "Електроніка", 640),
        ("EL-202", "USB-накопичувач 64 ГБ", "Електроніка", 420),
        ("ST-301", "Набір олівців", "Канцтовари", 125),
        ("ST-302", "Блокнот А5", "Канцтовари", 95),
        ("AC-401", "Папка для документів", "Аксесуари", 175),
        ("AC-402", "Рюкзак міський", "Аксесуари", 1190),
    ]
    random = Random(512)
    for index in range(1, 49):
        order_date = date(2026, 1, 1) + timedelta(days=(index * 3 + random.randrange(3)) % 180)
        node = ET.SubElement(root, "order", {
            "id": f"ORD-{index:04d}", "date": order_date.isoformat(),
            "city": cities[(index + 2) % len(cities)],
            "status": "cancelled" if index % 9 == 0 else "completed",
        })
        for pos in random.sample(range(len(products)), random.randrange(1, 4)):
            sku, name, category, price = products[pos]
            item = ET.SubElement(node, "item", {"sku": sku, "category": category})
            ET.SubElement(item, "name").text = name
            ET.SubElement(item, "quantity").text = str(random.randrange(1, 5))
            ET.SubElement(item, "unit_price").text = f"{Decimal(price):.2f}"
    ET.indent(root, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    generate(Path(__file__).resolve().parent / "data" / "sales_2026.xml")
    print("Навчальний XML-файл створено.")
