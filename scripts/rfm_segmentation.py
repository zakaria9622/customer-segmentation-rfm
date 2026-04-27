"""
RFM customer segmentation: scores, segments, metrics, and charts.
Run from project root: python scripts/rfm_segmentation.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "customer_orders.csv"
OUT_DIR = ROOT / "outputs"


def load_orders() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing {DATA_PATH}. Run: python scripts/generate_dataset.py"
        )
    return pd.read_csv(DATA_PATH, parse_dates=["order_date"])


def compute_rfm(df: pd.DataFrame, as_of: pd.Timestamp | None = None) -> pd.DataFrame:
    as_of = as_of or df["order_date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_id", as_index=False).agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "count"),
        monetary=("revenue", "sum"),
    )
    rfm["recency_days"] = (as_of - rfm["last_order_date"]).dt.days
    return rfm


def _quintile_score_high_best(values: pd.Series) -> pd.Series:
    """5 = best for metrics where larger values are better (frequency, monetary)."""
    ranked = values.rank(method="first", ascending=True)
    n = max(len(ranked), 1)
    pct = (ranked - 0.5) / n
    return pd.cut(pct, bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0], labels=[1, 2, 3, 4, 5]).astype(int)


def _quintile_score_low_best(values: pd.Series) -> pd.Series:
    """5 = best for recency (fewer days since last order is better)."""
    ranked = values.rank(method="first", ascending=True)
    n = max(len(ranked), 1)
    pct = (ranked - 0.5) / n
    return pd.cut(pct, bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0], labels=[5, 4, 3, 2, 1]).astype(int)


def add_rfm_scores(rfm: pd.DataFrame) -> pd.DataFrame:
    out = rfm.copy()
    out["R"] = _quintile_score_low_best(out["recency_days"])
    out["F"] = _quintile_score_high_best(out["frequency"])
    out["M"] = _quintile_score_high_best(out["monetary"])
    return out


def assign_segments_vectorized(df: pd.DataFrame) -> pd.Series:
    r, f, m = df["R"], df["F"], df["M"]
    vip = (r >= 4) & (f >= 4) & (m >= 4)
    lost = (r <= 2) & (f <= 2) & (m <= 2)
    at_risk = (r <= 2) & ((f >= 3) | (m >= 3)) & ~lost
    seg = pd.Series("Loyal", index=df.index, dtype=object)
    seg = seg.mask(at_risk, "At-risk")
    seg = seg.mask(lost, "Lost")
    seg = seg.mask(vip, "VIP")
    return seg


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    total_customers = len(rfm)
    total_revenue = rfm["monetary"].sum()
    g = rfm.groupby("segment", as_index=False).agg(
        customers=("customer_id", "count"),
        segment_revenue=("monetary", "sum"),
    )
    g["pct_customers"] = (100 * g["customers"] / total_customers).round(2)
    g["pct_revenue"] = (100 * g["segment_revenue"] / total_revenue).round(2)
    g["avg_revenue_per_customer"] = (g["segment_revenue"] / g["customers"]).round(2)
    order = ["VIP", "Loyal", "At-risk", "Lost"]
    g["segment"] = pd.Categorical(g["segment"], categories=order, ordered=True)
    return g.sort_values("segment").reset_index(drop=True)


def plot_charts(summary: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    order = ["VIP", "Loyal", "At-risk", "Lost"]
    colors = {"VIP": "#2ecc71", "Loyal": "#3498db", "At-risk": "#f39c12", "Lost": "#e74c3c"}

    s = summary.set_index("segment").reindex(order)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    ax0 = axes[0]
    bars = ax0.bar(s.index.astype(str), s["customers"], color=[colors[x] for x in order])
    ax0.set_title("Customers by segment")
    ax0.set_ylabel("Count")
    for rect, val in zip(bars, s["pct_customers"], strict=True):
        ax0.annotate(
            f"{val:.1f}%",
            xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax1 = axes[1]
    bars1 = ax1.bar(s.index.astype(str), s["segment_revenue"] / 1_000, color=[colors[x] for x in order])
    ax1.set_title("Revenue by segment")
    ax1.set_ylabel("Revenue (thousands)")
    for rect, val in zip(bars1, s["pct_revenue"], strict=True):
        ax1.annotate(
            f"{val:.1f}%",
            xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    fig.savefig(OUT_DIR / "segment_distribution_and_revenue.png", dpi=150)
    plt.close()

    fig2, axp = plt.subplots(figsize=(6, 6))
    axp.pie(
        s["customers"],
        labels=[f"{k}\n({v:.1f}%)" for k, v in zip(order, s["pct_customers"], strict=True)],
        colors=[colors[x] for x in order],
        startangle=90,
    )
    axp.set_title("Share of customers by segment")
    fig2.savefig(OUT_DIR / "segment_share_pie.png", dpi=150)
    plt.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    orders = load_orders()
    rfm = compute_rfm(orders)
    rfm = add_rfm_scores(rfm)
    rfm["segment"] = assign_segments_vectorized(rfm)

    summary = segment_summary(rfm)
    summary.to_csv(OUT_DIR / "segment_summary.csv", index=False)
    rfm.to_csv(OUT_DIR / "rfm_scores.csv", index=False)

    metrics = {
        "n_customers": int(rfm["customer_id"].nunique()),
        "n_orders": int(len(orders)),
        "total_revenue": float(orders["revenue"].sum()),
        "as_of_date": str(orders["order_date"].max().date()),
        "segment_summary": summary.to_dict(orient="records"),
    }
    (OUT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    plot_charts(summary)
    print(summary.to_string(index=False))
    print(f"\nSaved outputs under {OUT_DIR}")


if __name__ == "__main__":
    main()
