"""Побудова двох діаграм; потрібна бібліотека matplotlib."""
from pathlib import Path


def make_plots(stats: dict, directory: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for field, title, name, kind in [
        ("by_category", "Виторг за категоріями", "revenue_by_category.png", "bar"),
        ("by_month", "Динаміка виторгу за місяцями", "revenue_by_month.png", "line"),
    ]:
        items = stats[field]
        fig, ax = plt.subplots(figsize=(8, 4.1))
        x = list(items)
        y = [float(v) for v in items.values()]
        if kind == "bar":
            ax.bar(x, y)
        else:
            ax.plot(x, y, marker="o", linewidth=2)
        ax.set_title(title)
        ax.set_ylabel("грн")
        ax.grid(axis="y", alpha=0.28)
        ax.tick_params(axis="x", labelrotation=25)
        fig.tight_layout()
        fig.savefig(directory / name, dpi=160)
        plt.close(fig)
