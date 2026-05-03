# Customer segmentation with RFM (CRM analytics)

Portfolio piece for **junior Data Analyst** and **CRM Analyst** roles: start from orders, end with **who matters for revenue**, **who needs a different journey**, and **where to cap spend**—using definitions a business team can audit, not a black-box model.

---

## Story at a glance (this repo’s run)

All figures below are copied from **`outputs/metrics.json`** (same run as the tables and charts in `outputs/`).

| Question | Answer from the data |
|----------|----------------------|
| How big is the base? | **5,000** customers, **45,356** orders, **4,522,014.07** revenue (sum of order lines), last order **2026-03-29** |
| Who carries revenue? | **VIP**: **1,395** customers (**27.9%**) → **3,409,494.17** revenue (**75.4%** of total) |
| Who is large but light on revenue? | **Lost**: **1,181** customers (**23.62%**) → **133,528.73** revenue (**2.95%** of total) |
| Who should CRM worry about *before* they look “Lost”? | **At-risk**: **819** (**16.38%** of customers), **402,223.16** revenue (**8.89%**); **491.11** avg revenue per customer vs **359.36** for **Loyal** |
| Who is the “grow the middle” file? | **Loyal**: **1,605** (**32.1%** of customers), **576,768.01** revenue (**12.75%**) |

That contrast—**75.4%** of revenue from **27.9%** of customers, while **23.62%** of customers produce **2.95%** of revenue—is the core CRM story in one glance.

---

## Business problem

When **retention and CRM** are not tied to **value and lifecycle stage**, teams usually see the same failure mode:

- **Budget and sends** spread evenly, so **high-value** buyers get under-served and **low-value** dormant profiles get over-mailed.  
- **Win-back** starts too late: by the time “everyone” notices churn, the customer already matches **Lost** behavior.  
- **Leadership** lacks a single view of “revenue concentration” and “rescue opportunity,” so prioritization in weekly CRM standups becomes opinion-driven.

This project answers four practical questions for Marketing / CRM / leadership—using only the transactional extract in `data/` and reproducible rules in `scripts/rfm_segmentation.py`:

1. Who already **drives most revenue** today?  
2. Who is **quiet but historically strong** (defend revenue before it disappears)?  
3. Who is the **broad engaged middle** where growth tactics (cross-sell, frequency) fit best?  
4. Where should we **avoid expensive** one-size-fits-all reactivation?

---

## Segmentation logic (how labels are built)

**Step 1 — RFM metrics (per customer)**

| Metric | Definition |
|--------|------------|
| **Recency** | Days from last order to the day after the latest order in the data (reference **2026-03-30**; last observed order **2026-03-29**) |
| **Frequency** | Count of orders |
| **Monetary** | Sum of order revenue |

**Step 2 — Scores 1–5 (quintiles)**  

Each of **R**, **F**, and **M** is scored **1** (weak) to **5** (strong) with **rank-based quintiles** on the full customer base: **shorter** time since last order → **higher R**; **more orders** → **higher F**; **more revenue** → **higher M**.

**Step 3 — Business segments (priority order)**  

Labels are **mutually exclusive** and applied in this order (see `scripts/rfm_segmentation.py`):

1. **VIP** — `R ≥ 4` **and** `F ≥ 4` **and** `M ≥ 4`: top tier on all three dimensions *within this cohort’s distribution*.  
2. **Lost** — `R ≤ 2` **and** `F ≤ 2` **and** `M ≤ 2`: weak on recency, frequency, and monetary.  
3. **At-risk** — `R ≤ 2`, **not** Lost, and **`F ≥ 3` or `M ≥ 3`**: poor recency but **enough** past frequency or spend to justify a **focused** win-back path (before they fully match Lost).  
4. **Loyal** — everyone else: not VIP, not Lost, not At-risk.

**Why priority order matters for the business:** VIP is evaluated **first** so your “best of the best” is not overwritten by a weaker rule. Lost is defined **before** At-risk so “weak everywhere” is not double-counted as “recoverable.”

---

## Key customer insights (grounded in segment outputs)

Summary table (same numbers as `metrics.json`):

| Segment | Customers | % customers | Segment revenue | % revenue | Avg revenue / customer |
|---------|-----------:|-------------|----------------:|----------:|-----------------------:|
| VIP | 1,395 | 27.90 | 3,409,494.17 | 75.40 | 2,444.08 |
| Loyal | 1,605 | 32.10 | 576,768.01 | 12.75 | 359.36 |
| At-risk | 819 | 16.38 | 402,223.16 | 8.89 | 491.11 |
| Lost | 1,181 | 23.62 | 133,528.73 | 2.95 | 113.06 |

**1. Revenue concentration (VIP)**  
**1,395** customers (**27.9%**) generate **3,409,494.17** of **4,522,014.07** total revenue (**75.4%**). Any CRM or service disruption here hits the bulk of historical value.

**2. At-risk = smaller list, meaningful dollars, higher average than Loyal**  
**819** customers (**16.38%**), **402,223.16** revenue (**8.89%**). Average revenue per customer **491.11** exceeds Loyal **359.36**—so “Loyal” in name is not always “higher value per head” in this snapshot; At-risk deserves **its own** treatment and reporting line.

**3. Loyal = share of wallet / frequency opportunity**  
**1,605** customers (**32.1%**) but **12.75%** of revenue (**576,768.01**). Natural place for **structured** cross-sell and habit-building—not the same incentives as VIP.

**4. Lost = many profiles, little revenue**  
**1,181** customers (**23.62%**), **133,528.73** revenue (**2.95%**). Segment-level average revenue **113.06** vs VIP **2,444.08** is a ratio of **2,444.08 ÷ 113.06 ≈ 21.6** (derived from the two published averages—useful for explaining *magnitude*, not a second hidden dataset).

---

## Recommended CRM actions by segment

| Segment | Business intent | CRM / lifecycle actions (examples) |
|---------|-----------------|--------------------------------------|
| **VIP** | Protect LTV, avoid silent churn | Tiered benefits, early access, high-touch service paths, **discount discipline**; monitor downgrade into At-risk |
| **Loyal** | Grow orders and basket | Cross-sell / bundles, replenishment, referrals; **test** incentives with margin guardrails |
| **At-risk** | Recover before rules label them Lost | Short win-back journeys, time-bound offers, **frequency caps**, suppress non-openers; prioritize highest **M** / **F** within At-risk in tooling |
| **Lost** | Cheap or no-touch; hygiene | Long cadence or sunset, clearance-style messaging, suppress from paid if policy allows; avoid cloning this profile in acquisition |

---

## Expected business impact (qualitative—no fabricated lift %)

There is **no** randomized holdout in this repo, so impact stays **directional**—how hiring managers expect a junior analyst to speak without inventing “+X% revenue.”

| Segment | What “good” would look like if CRM acts on this |
|---------|--------------------------------------------------|
| **VIP** | Fewer unexplained drops in recency/F/M among the group that currently represents **75.4%** of revenue; CRM and service effort aligned to **27.9%** of customers who matter most |
| **At-risk** | Part of the **8.89%** revenue pool and **402,223.16** segment total reactivated **without** blasting the whole file—measured by re-purchase and margin after offer |
| **Loyal** | Gradual lift in orders or revenue per customer from the **32.1%** base (**12.75%** of revenue today) via journeys, not one-off batch sends |
| **Lost** | Lower cost-to-serve on CRM and paid for the **23.62%** of customers who only represent **2.95%** of revenue at segment level; cleaner list health |

**KPIs to report in standup (no targets invented):** segment **counts**, **% customers**, **% revenue**, **avg revenue per customer**, and week-over-week **migration** between segments after campaigns (definitions unchanged).

---

## What I would present to a business team

**Slide 1 — Why we’re here**  
One list / one discount strategy misaligns spend with value; we need a **shared** view of who drives revenue and who is sliding.

**Slide 2 — What I built (trust)**  
Order → customer-level **R, F, M** → quintile scores **1–5** → **transparent** segment rules (this README + `scripts/rfm_segmentation.py`). Anyone can challenge thresholds.

**Slide 3 — The headline (numbers from this run)**  
- **75.4%** of revenue from **27.9%** of customers (**3,409,494.17 / 4,522,014.07**).  
- **2.95%** of revenue from **23.62%** of customers (**133,528.73 / 4,522,014.07**).

**Slide 4 — The “do this next” segment**  
At-risk: **16.38%** of customers, **8.89%** of revenue, **491.11** avg revenue per customer **>** Loyal **359.36** → **prioritized win-back** design, not a generic blast.

**Slide 5 — Ask**  
Approve **four journeys** (VIP / Loyal / At-risk / Lost), align ESP or CRM audiences to these definitions, and review **segment summary** weekly from `outputs/segment_summary.csv` (or the warehouse equivalent).

**Artifacts on the table:** `outputs/segment_distribution_and_revenue.png`, `outputs/segment_share_pie.png`, `outputs/segment_summary.csv`, `outputs/metrics.json`.

**Questions I’d expect—and how I’d answer**  
- *“Why quintiles?”* → Same scale across R/F/M for a **first** segmentation layer; thresholds can be recalibrated with leadership.  
- *“Why not ML?”* → Start with **interpretable** rules CRM can implement; ML can layer on later with governance.  
- *“Can we trust synthetic data?”* → This repo proves **pipeline** and **storytelling**; production uses the same logic on **real** extracts.

---

## Technical stack and outputs

- **Python**, **pandas** (RFM aggregation and scoring), **matplotlib** (charts).  
- **Outputs:** `outputs/rfm_scores.csv`, `outputs/segment_summary.csv`, `outputs/metrics.json`, PNG charts under `outputs/`.

```text
02_customer_segmentation/
├── README.md
├── requirements.txt
├── data/customer_orders.csv
├── scripts/generate_dataset.py
├── scripts/rfm_segmentation.py
└── outputs/
```

**Re-run:** `pip install -r requirements.txt` → `python scripts/generate_dataset.py` → `python scripts/rfm_segmentation.py`. Regenerating data **changes** outputs; refresh numbers from **`outputs/metrics.json`** after a new run.

---

## One-line interview pitch

> I built RFM quintiles and priority-based segment rules, then showed **75.4%** of revenue from **27.9%** of customers while **23.62%** of customers contribute **2.95%** of revenue—so CRM should **protect VIPs**, **win back At-risk with caps**, **grow Loyal with structured journeys**, and **limit spend on Lost**.
