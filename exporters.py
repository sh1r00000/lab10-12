"""Збереження даних у CSV, JSON та зручний HTML-звіт."""
import csv
from decimal import Decimal
from html import escape
import json
from pathlib import Path
from models import Order


class SalesExporter:
    @staticmethod
    def export_orders(orders: list[Order], out: Path, category: str | None = None) -> None:
        with out.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Номер", "Дата", "Місто", "Статус", "SKU", "Категорія",
                        "Товар", "Кількість", "Ціна, грн", "Сума, грн"])
            for order in orders:
                for item in order.items:
                    if category and item.category.casefold() != category.casefold():
                        continue
                    w.writerow([order.order_id, order.order_date.isoformat(), order.city,
                                order.status, item.sku, item.category, item.name,
                                item.quantity, item.unit_price, item.total])

    @staticmethod
    def export_summary(stats: dict, directory: Path) -> None:
        with (directory / "summary.json").open("w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        for name, key in [("by_city.csv", "by_city"), ("by_category.csv", "by_category"),
                          ("by_month.csv", "by_month")]:
            with (directory / name).open("w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Група", "Виторг, грн"])
                writer.writerows(stats[key].items())

    @staticmethod
    def export_html(stats: dict, directory: Path, include_charts: bool = True) -> None:
        def table(items: dict) -> str:
            rows = "".join(
                f"<tr><td>{escape(str(k))}</td><td>{v:,.2f}</td></tr>" for k, v in items.items()
            )
            return f"<table><thead><tr><th>Група</th><th>Виторг, грн</th></tr></thead><tbody>{rows}</tbody></table>"

        charts = ("<figure><img src='revenue_by_category.png' alt='Діаграма за категоріями'></figure>"
                  "<figure><img src='revenue_by_month.png' alt='Динаміка за місяцями'></figure>") if include_charts else ""
        template = f"""<!doctype html><html lang='uk'><head><meta charset='utf-8'>
<title>Аналіз XML-замовлень</title><style>
body{{font:16px Arial,sans-serif;max-width:960px;margin:40px auto;color:#243044}}
h1{{color:#183e65}}table{{border-collapse:collapse;width:100%;margin:12px 0 24px}}
th,td{{padding:9px;border:1px solid #cdd7e2;text-align:left}}th{{background:#e6eef7}}
figure{{margin:16px 0}}img{{width:100%;max-width:800px}}.muted{{color:#566}}
</style></head><body>
<h1>Результати аналізу XML-продажів</h1>
<p class='muted'>Демонстраційний набір даних (суми у гривнях).</p>
<p>Замовлень: <b>{stats['all_orders']}</b>; завершених: <b>{stats['completed_orders']}</b>;
скасованих: <b>{stats['cancelled_orders']}</b>; продано одиниць: <b>{stats['units']}</b>;
виторг: <b>{stats['revenue']:,.2f} грн</b>.</p>
<h2>За категоріями</h2>{table(stats['by_category'])}
<h2>За містами</h2>{table(stats['by_city'])}
<h2>За місяцями</h2>{table(stats['by_month'])}
{charts}
</body></html>"""
        (directory / "report.html").write_text(template, encoding="utf-8")
