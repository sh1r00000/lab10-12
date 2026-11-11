"""Практична робота №10–12, варіант 5. Парсинг і аналіз XML."""
import argparse
from datetime import date
from pathlib import Path
import sys
from xml_repository import XMLSalesRepository, DataError
from models import Selection
from analysis import SalesAnalyzer
from exporters import SalesExporter
from plots import make_plots

BASE_DIR = Path(__file__).resolve().parent


def valid_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Невірна дата '{value}'; потрібен формат YYYY-MM-DD.") from exc


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Пошук та аналіз замовлень з XML")
    parser.add_argument("--xml", type=Path, default=BASE_DIR / "data" / "sales_2026.xml")
    parser.add_argument("--out", type=Path, default=BASE_DIR / "output")
    parser.add_argument("--city", help="Фільтр за містом (напр., Суми)")
    parser.add_argument("--category", help="Фільтр за категорією (напр., Книги)")
    parser.add_argument("--start", help="Початок періоду YYYY-MM-DD")
    parser.add_argument("--end", help="Кінець періоду YYYY-MM-DD")
    parser.add_argument("--interactive", action="store_true", help="Ввести фільтри з клавіатури")
    parser.add_argument("--no-chart", action="store_true", help="Не створювати PNG-графіки")
    return parser


def run(args: argparse.Namespace) -> dict:
    if args.interactive:
        print("Фільтри. Для пропуску натисніть Enter.")
        args.city = input("Місто: ").strip() or None
        args.category = input("Категорія: ").strip() or None
        args.start = input("Від (YYYY-MM-DD): ").strip() or None
        args.end = input("До (YYYY-MM-DD): ").strip() or None
    start, end = valid_date(args.start), valid_date(args.end)
    if start and end and start > end:
        raise ValueError("Дата початку не може бути пізнішою за дату завершення.")

    orders = XMLSalesRepository().load(args.xml)
    selection = Selection(args.city, args.category, start, end)
    chosen = SalesAnalyzer(orders).filter(selection)
    if not chosen:
        raise DataError("Немає записів, що задовольняють умову пошуку.")
    stats = SalesAnalyzer.summarize(chosen, category=args.category)
    args.out.mkdir(parents=True, exist_ok=True)
    SalesExporter.export_orders(chosen, args.out / "orders.csv", category=args.category)
    SalesExporter.export_summary(stats, args.out)
    if not args.no_chart:
        make_plots(stats, args.out)
    SalesExporter.export_html(stats, args.out, include_charts=not args.no_chart)

    print("ПРАКТИЧНА РОБОТА №10–12. АНАЛІЗ XML")
    print(f"XML-файл: {args.xml.name}; опрацьовано замовлень: {len(orders)}")
    if args.city or args.category or args.start or args.end:
        print(f"Пошук: місто={args.city or 'усі'}, категорія={args.category or 'усі'}, "
              f"період={args.start or '...'} — {args.end or '...'}")
    print(f"Знайдено: {stats['all_orders']} (завершені: {stats['completed_orders']}, "
          f"скасовані: {stats['cancelled_orders']})")
    print(f"Одиниць товару: {stats['units']}; виторг: {stats['revenue']:,.2f} грн")
    print("Категорія / виторг:")
    for k, v in stats["by_category"].items():
        print(f"  {k:<17}: {v:,.2f} грн")
    print(f"Файли збережено у: {args.out}")
    return stats


def main() -> int:
    try:
        run(create_parser().parse_args())
        return 0
    except (FileNotFoundError, PermissionError, DataError, ValueError, OSError,
            ImportError, EOFError, KeyboardInterrupt) as exc:
        print(f"Помилка: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
