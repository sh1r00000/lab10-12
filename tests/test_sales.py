"""Автоматичні перевірки практичної роботи №10–12."""
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import Selection
from xml_repository import XMLSalesRepository, DataError
from analysis import SalesAnalyzer
from exporters import SalesExporter

ROOT = Path(__file__).resolve().parents[1]


class SalesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orders = XMLSalesRepository().load(ROOT / "data" / "sales_2026.xml")
        cls.a = SalesAnalyzer(cls.orders)

    def test_count(self):
        self.assertEqual(len(self.orders), 48)

    def test_stats_completed_only(self):
        s = self.a.summarize(self.orders)
        self.assertEqual(s["completed_orders"], 43)
        self.assertEqual(s["cancelled_orders"], 5)
        self.assertEqual(s["revenue"], Decimal("95600"))

    def test_categories_sum_to_total(self):
        s = self.a.summarize(self.orders)
        self.assertEqual(sum(s["by_category"].values()), s["revenue"])

    def test_city_filter_case_insensitive(self):
        res = self.a.filter(Selection(city="сУмИ"))
        self.assertTrue(res)
        self.assertTrue(all(x.city == "Суми" for x in res))

    def test_date_filter(self):
        res = self.a.filter(Selection(start=date(2026, 3, 1), end=date(2026, 3, 31)))
        self.assertTrue(res)
        self.assertTrue(all(x.order_date.month == 3 for x in res))

    def test_category_filter_and_export(self):
        sel = self.a.filter(Selection(category="Книги"))
        self.assertTrue(all(any(i.category == "Книги" for i in o.items) for o in sel))
        with tempfile.TemporaryDirectory() as temp:
            f = Path(temp) / "orders.csv"
            SalesExporter.export_orders(sel, f, category="Книги")
            with f.open(encoding="utf-8-sig", newline="") as data:
                rows = list(csv.DictReader(data))
            self.assertTrue(rows)
            self.assertTrue(all(row["Категорія"] == "Книги" for row in rows))

    def test_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            XMLSalesRepository().load(ROOT / "data" / "missing.xml")

    def test_malformed_xml(self):
        with tempfile.TemporaryDirectory() as temp:
            f = Path(temp) / "bad.xml"
            f.write_text("<salesReport><order></salesReport>", encoding="utf-8")
            with self.assertRaises(DataError):
                XMLSalesRepository().load(f)

    def test_invalid_quantity(self):
        with tempfile.TemporaryDirectory() as temp:
            f = Path(temp) / "bad.xml"
            f.write_text('''<salesReport currency="UAH"><order id="A" date="2026-01-01" city="Суми" status="completed">
              <item sku="P" category="Книги"><name>Тест</name><quantity>0</quantity><unit_price>10</unit_price></item>
              </order></salesReport>''', encoding="utf-8")
            with self.assertRaises(DataError):
                XMLSalesRepository().load(f)

    def test_duplicate_id(self):
        with tempfile.TemporaryDirectory() as temp:
            source = ROOT / "data" / "sales_2026.xml"
            content = source.read_text(encoding="utf-8")
            content = content.replace('id="ORD-0002"', 'id="ORD-0001"', 1)
            f = Path(temp) / "dupes.xml"
            f.write_text(content, encoding="utf-8")
            with self.assertRaises(DataError):
                XMLSalesRepository().load(f)

    def test_empty_selection(self):
        self.assertEqual(self.a.filter(Selection(city="Невідоме місто")), [])

if __name__ == "__main__":
    unittest.main(verbosity=2)
