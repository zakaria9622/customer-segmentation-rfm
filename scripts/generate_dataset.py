"""
Generate a realistic e-commerce order-level dataset for RFM analysis.
Run from project root: python scripts/generate_dataset.py
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "data" / "customer_orders.csv"


def main() -> None:
    n_customers = 5_000
    end_date = datetime(2026, 4, 1)
    start_date = end_date - timedelta(days=730)

    customer_ids = np.arange(1, n_customers + 1)
    # Mix of segments via latent "behavior type"
    types = RNG.choice(["vip", "loyal", "casual", "dormant", "churned"], size=n_customers, p=[0.08, 0.22, 0.35, 0.20, 0.15])

    rows: list[dict] = []
    order_id = 1

    for cid, ctype in zip(customer_ids, types, strict=True):
        if ctype == "vip":
            n_orders = int(RNG.integers(18, 45))
            last_offset = int(RNG.integers(1, 21))
            base_amount = RNG.uniform(80, 250)
        elif ctype == "loyal":
            n_orders = int(RNG.integers(8, 22))
            last_offset = int(RNG.integers(1, 60))
            base_amount = RNG.uniform(45, 140)
        elif ctype == "casual":
            n_orders = int(RNG.integers(2, 8))
            last_offset = int(RNG.integers(1, 120))
            base_amount = RNG.uniform(25, 90)
        elif ctype == "dormant":
            n_orders = int(RNG.integers(3, 12))
            last_offset = int(RNG.integers(120, 400))
            base_amount = RNG.uniform(30, 100)
        else:  # churned
            n_orders = int(RNG.integers(1, 5))
            last_offset = int(RNG.integers(300, 700))
            base_amount = RNG.uniform(15, 55)

        last_purchase = end_date - timedelta(days=last_offset)
        # Spread orders backward from last_purchase
        span_days = min(int((last_purchase - start_date).days) - 1, 540)
        span_days = max(span_days, n_orders)

        offsets = sorted(RNG.choice(np.arange(1, span_days + 1), size=n_orders, replace=False))
        for off in offsets:
            dt = last_purchase - timedelta(days=int(off))
            if dt < start_date:
                continue
            noise = RNG.normal(0, base_amount * 0.15)
            revenue = round(float(max(9.99, base_amount + noise)), 2)
            rows.append(
                {
                    "customer_id": int(cid),
                    "order_id": order_id,
                    "order_date": dt.strftime("%Y-%m-%d"),
                    "revenue": revenue,
                }
            )
            order_id += 1

    df = pd.DataFrame(rows)
    df = df.sort_values(["customer_id", "order_date", "order_id"]).reset_index(drop=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(df):,} orders for {df['customer_id'].nunique():,} customers -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
