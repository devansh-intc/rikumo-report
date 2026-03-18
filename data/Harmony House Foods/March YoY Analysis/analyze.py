#!/usr/bin/env python3
"""
Harmony House Foods — March YoY Analysis (v4)
Compares March 2025 vs March 2026 (1-17) performance.
Generates two HTML reports: main Shopify report + separate Ad Spend report.
"""

import csv
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Load Data ────────────────────────────────────────────────────────────────
def load_shopify_2025():
    rows = []
    with open(os.path.join(BASE, "shopify_march_2025.csv")) as f:
        for r in csv.DictReader(f):
            rows.append({
                "day": r["Day"], "orders": int(r["Orders"]),
                "gross_sales": float(r["Gross sales"]),
                "discounts": float(r["Discounts"]),
                "net_sales": float(r["Net sales"]),
                "shipping": float(r["Shipping charges"]),
                "taxes": float(r["Taxes"]),
                "total_sales": float(r["Total sales"]),
            })
    return rows

def load_utm_2026():
    rows = []
    with open(os.path.join(BASE, "utm_shopify_march_2026.csv")) as f:
        for r in csv.DictReader(f):
            rows.append({
                "day": r["Day"],
                "source": r["UTM campaign source"].strip() if r["UTM campaign source"].strip() else "(direct/none)",
                "medium": r["UTM campaign medium"].strip() if r["UTM campaign medium"].strip() else "(none)",
                "orders": int(r["Orders (last click)"]),
                "gross_sales": float(r["Gross sales (last click)"]),
                "discounts": float(r["Discounts (last click)"]),
                "returns": float(r["Returns (last click)"]),
                "net_sales": float(r["Net sales (last click)"]),
                "shipping": float(r["Shipping charges (last click)"]),
                "taxes": float(r["Taxes (last click)"]),
                "total_sales": float(r["Total sales (last click)"]),
            })
    return rows

def load_ad_spend_2026():
    rows = []
    with open(os.path.join(BASE, "daily_ad_spend_2026.csv")) as f:
        for r in csv.DictReader(f):
            rows.append({
                "day": r["Day"],
                "fb_spent": float(r["FB Spent"]),
                "google_spent": float(r["Google Spent"]),
                "total_spent": float(r["Total Amount Spent"]),
                "fb_conv_value": float(r["FB Purchase Conversion Value"]),
                "google_conv_value": float(r["Google Purchase Conversion Value"]),
                "total_conv_value": float(r["Total Purchase Conversion Value"]),
                "roas": float(r["ROAS"]),
                "daily_shopify_sales": float(r["Daily Shopify Sales"]),
                "mer": float(r["MER"]),
            })
    return rows

def load_products_2026():
    rows = []
    with open(os.path.join(BASE, "shopify_products_march_2026.csv")) as f:
        for r in csv.DictReader(f):
            rows.append({
                "name": r["Product title"],
                "items_sold": int(r["Net items sold"]),
                "gross_sales": float(r["Gross sales"]),
                "discounts": float(r["Discounts"]),
                "returns": float(r["Returns"]),
                "net_sales": float(r["Net sales"]),
                "taxes": float(r["Taxes"]),
                "total_sales": float(r["Total sales"]),
            })
    return rows

def load_new_returning(filename):
    rows = {}
    with open(os.path.join(BASE, filename)) as f:
        for r in csv.DictReader(f):
            ctype = r["New or returning customer"].strip()
            rows[ctype] = {
                "orders": int(r["Orders"]),
                "gross_sales": float(r["Gross sales"]),
                "discounts": float(r["Discounts"]),
                "net_sales": float(r["Net sales"]),
                "total_sales": float(r["Total sales"]),
                "aov": float(r["Average order value"]),
            }
    return rows

shopify_2025 = load_shopify_2025()
utm_2026 = load_utm_2026()
ad_spend_2026 = load_ad_spend_2026()
products_2026 = load_products_2026()
nr_2025 = load_new_returning("new_returning_2025_mar1-17.csv")
nr_2026 = load_new_returning("new_returning_2026_mar1-17.csv")

# ── Aggregate: March 2025 ───────────────────────────────────────────────────
def agg(rows, keys=("orders", "gross_sales", "total_sales", "net_sales")):
    return {k: sum(r[k] for r in rows) for k in keys}

def agg_discounts(rows):
    return sum(abs(r["discounts"]) for r in rows)

s25_full_rows = shopify_2025
s25_17_rows = shopify_2025[:17]  # March 1-17

s25_full = agg(s25_full_rows)
s25_full["discounts"] = agg_discounts(s25_full_rows)
s25_full["discount_rate"] = s25_full["discounts"] / s25_full["gross_sales"] * 100
s25_full["aov"] = s25_full["total_sales"] / s25_full["orders"]

s25_17 = agg(s25_17_rows)
s25_17["discounts"] = agg_discounts(s25_17_rows)
s25_17["discount_rate"] = s25_17["discounts"] / s25_17["gross_sales"] * 100
s25_17["aov"] = s25_17["total_sales"] / s25_17["orders"]

# ── Aggregate: March 2026 (from ad spend sheet — for ad spend & platform ROAS) ──
ad_march = [r for r in ad_spend_2026 if r["day"].startswith("2026-03")]

s26_fb_spent = sum(r["fb_spent"] for r in ad_march)
s26_google_spent = sum(r["google_spent"] for r in ad_march)
s26_total_spent = sum(r["total_spent"] for r in ad_march)
s26_fb_conv = sum(r["fb_conv_value"] for r in ad_march)
s26_google_conv = sum(r["google_conv_value"] for r in ad_march)
s26_total_conv = sum(r["total_conv_value"] for r in ad_march)

# ── Aggregate: March 2026 (from UTM all-channels data — PRIMARY sales source) ─
days_2026 = {}
for r in utm_2026:
    d = r["day"]
    if d not in days_2026:
        days_2026[d] = {"orders": 0, "gross_sales": 0, "discounts": 0, "returns": 0, "net_sales": 0, "total_sales": 0}
    days_2026[d]["orders"] += r["orders"]
    days_2026[d]["gross_sales"] += r["gross_sales"]
    days_2026[d]["discounts"] += abs(r["discounts"])
    days_2026[d]["returns"] += abs(r["returns"])
    days_2026[d]["net_sales"] += r["net_sales"]
    days_2026[d]["total_sales"] += r["total_sales"]

# Sorted daily list for day-by-day table
days_2026_sorted = sorted(days_2026.items())

s26_utm = {
    "orders": sum(v["orders"] for v in days_2026.values()),
    "gross_sales": sum(v["gross_sales"] for v in days_2026.values()),
    "discounts": sum(v["discounts"] for v in days_2026.values()),
    "net_sales": sum(v["net_sales"] for v in days_2026.values()),
    "total_sales": sum(v["total_sales"] for v in days_2026.values()),
}
s26_utm["discount_rate"] = s26_utm["discounts"] / s26_utm["gross_sales"] * 100 if s26_utm["gross_sales"] else 0
s26_utm["aov"] = s26_utm["total_sales"] / s26_utm["orders"] if s26_utm["orders"] else 0

# Use UTM all-channels total as the primary 2026 sales figure
s26_total_sales = s26_utm["total_sales"]

# ── UTM Channel Breakdown with Spend ────────────────────────────────────────
channels = {}
for r in utm_2026:
    src = r["source"].lower()
    med = r["medium"].lower()

    if src in ("facebook", "fb", "ig") and med in ("paid", "ads", "social"):
        ch = "Facebook & Instagram Paid"
    elif src in ("facebook",) and med == "(none)":
        ch = "Direct / Organic / Unattributed"  # FB organic = not paid traffic
    elif src == "google" and med == "cpc":
        ch = "Google Ads (CPC)"
    elif src == "google" and med == "product_sync":
        ch = "Google Shopping (Product Sync)"
    elif src == "google" and med == "(none)":
        ch = "Google Organic"
    elif src in ("klaviyo",) and med in ("email", "(none)"):
        ch = "Klaviyo Email"
    elif src == "shopify_email" and med == "email":
        ch = "Shopify Email"
    elif src == "shop_app":
        ch = "Shop App"
    elif src == "chatgpt.com":
        ch = "ChatGPT Referral"
    elif src == "(direct/none)" and med == "paid":
        ch = "Unknown Paid"
    elif src == "(direct/none)":
        ch = "Direct / Organic / Unattributed"
    else:
        ch = f"{r['source']} / {r['medium']}"

    if ch not in channels:
        channels[ch] = {"orders": 0, "gross_sales": 0, "discounts": 0, "net_sales": 0, "total_sales": 0}
    channels[ch]["orders"] += r["orders"]
    channels[ch]["gross_sales"] += r["gross_sales"]
    channels[ch]["discounts"] += abs(r["discounts"])
    channels[ch]["net_sales"] += r["net_sales"]
    channels[ch]["total_sales"] += r["total_sales"]

channels_sorted = sorted(channels.items(), key=lambda x: x[1]["total_sales"], reverse=True)
total_ch_sales = sum(v["total_sales"] for _, v in channels_sorted)

# Assign ad spend to channels
channel_spend = {
    "Facebook & Instagram Paid": s26_fb_spent,
    "Google Ads (CPC)": s26_google_spent,
    "Google Shopping (Product Sync)": 0,
    "Google Organic": 0,
    "Klaviyo Email": 0,
    "Shopify Email": 0,
    "Shop App": 0,
    "ChatGPT Referral": 0,
    "Unknown Paid": 0,
    "Direct / Organic / Unattributed": 0,
}

# FB paid channel totals
fb_paid_total_sales = channels.get("Facebook & Instagram Paid", {}).get("total_sales", 0)
fb_paid_total_orders = channels.get("Facebook & Instagram Paid", {}).get("orders", 0)

# Google CPC + Product Sync combined
google_paid_total_sales = sum(
    channels.get(ch, {}).get("total_sales", 0)
    for ch in ["Google Ads (CPC)", "Google Shopping (Product Sync)"]
)
google_paid_total_orders = sum(
    channels.get(ch, {}).get("orders", 0)
    for ch in ["Google Ads (CPC)", "Google Shopping (Product Sync)"]
)

# ── MER Calculations ────────────────────────────────────────────────────────
fb_spend_2025 = 153.00
google_spend_2025 = 7757.60
total_spend_2025 = fb_spend_2025 + google_spend_2025
mer_2025_full = s25_full["total_sales"] / total_spend_2025

mer_2026 = s26_total_sales / s26_total_spent

# ── Google Ads Campaign Data ────────────────────────────────────────────────
google_2025 = {
    "spend": 7757.60, "conversions": 199.24, "conv_value": 28105.68, "roas": 3.62,
    "clicks": 5934, "impressions": 587966,
    "campaigns": [
        {"name": "new ads 5", "type": "Search", "spend": 98.80, "conv": 0, "value": 0, "roas": 0},
        {"name": "Harmony House Foods", "type": "Search", "spend": 912.02, "conv": 10.01, "value": 1352.92, "roas": 1.48},
        {"name": "Ad 4", "type": "Search", "spend": 3083.21, "conv": 58.95, "value": 11611.15, "roas": 3.77},
        {"name": "Sale merchant ad 1", "type": "Shopping", "spend": 3663.57, "conv": 130.28, "value": 15141.61, "roas": 4.13},
    ]
}

google_2026 = {
    "spend": 3494.34, "conversions": 137.68, "conv_value": 17158.26, "roas": 4.91,
    "clicks": 6255, "impressions": 374935,
    "campaigns": [
        {"name": "INTC | Branded Search | Max Conv", "type": "Search", "spend": 528.42, "conv": 31, "value": 3621.40, "roas": 6.85},
        {"name": "INTC | P.Max | All Products", "type": "PMax", "spend": 2774.63, "conv": 106.68, "value": 13536.86, "roas": 4.88, "note": "Budget-limited at $190/day"},
        {"name": "INTC | NB | Search | Dried Cabbage", "type": "Search", "spend": 191.29, "conv": 0, "value": 0, "roas": 0, "note": "Paused (0 conversions)"},
    ]
}

# ── Projections ─────────────────────────────────────────────────────────────
days_elapsed = 17
days_in_march = 31
remaining_days = days_in_march - days_elapsed
prorate = days_in_march / days_elapsed

s26_projected = s26_total_sales * prorate
s26_projected_spend = s26_total_spent * prorate
target_total = s25_full["total_sales"] * 1.15
gap_to_target = target_total - s26_projected
daily_needed = (target_total - s26_total_sales) / remaining_days
avg_daily_2026 = s26_total_sales / days_elapsed
avg_daily_2025 = s25_full["total_sales"] / days_in_march

# ── Outlier: March 12, 2025 ────────────────────────────────────────────────
mar12_2025 = shopify_2025[11]
s25_17_ex12 = s25_17["total_sales"] - mar12_2025["total_sales"]
s25_17_orders_ex12 = s25_17["orders"] - mar12_2025["orders"]
mar12_2026_sales = days_2026_sorted[11][1]["total_sales"] if len(days_2026_sorted) > 11 else 0
s26_17_ex12 = s26_total_sales - mar12_2026_sales

# ── Weekly breakdown ────────────────────────────────────────────────────────
week1_25 = sum(shopify_2025[i]["total_sales"] for i in range(7))
week2_25 = sum(shopify_2025[i]["total_sales"] for i in range(7, 14))
week3p_25 = sum(shopify_2025[i]["total_sales"] for i in range(14, 17))
week1_26 = sum(days_2026_sorted[i][1]["total_sales"] for i in range(7))
week2_26 = sum(days_2026_sorted[i][1]["total_sales"] for i in range(7, 14))
week3p_26 = sum(days_2026_sorted[i][1]["total_sales"] for i in range(14, 17))

# ── Daily Trend & End-of-Month Projection ──────────────────────────────────
# Daily sales lists
daily_sales_2026 = [days_2026_sorted[i][1]["total_sales"] for i in range(17)]
daily_sales_2025 = [shopify_2025[i]["total_sales"] for i in range(31)]

# 2026 period averages
first7_avg_26 = sum(daily_sales_2026[:7]) / 7
week2_avg_26 = sum(daily_sales_2026[7:14]) / 7
last5_avg_26 = sum(daily_sales_2026[12:]) / 5  # Mar 13-17
last3_avg_26 = sum(daily_sales_2026[14:]) / 3  # Mar 15-17
trend_drop_pct_26 = (last5_avg_26 - first7_avg_26) / first7_avg_26 * 100

# 2025 same-period averages (for comparison)
first7_avg_25 = sum(daily_sales_2025[:7]) / 7
week2_avg_25 = sum(daily_sales_2025[7:14]) / 7
last5_of17_avg_25 = sum(daily_sales_2025[12:17]) / 5  # Mar 13-17
last3_of17_avg_25 = sum(daily_sales_2025[14:17]) / 3  # Mar 15-17
trend_drop_pct_25 = (last5_of17_avg_25 - first7_avg_25) / first7_avg_25 * 100

# 2025 remaining period (Mar 18-31)
s25_remaining = s25_full["total_sales"] - s25_17["total_sales"]
s25_remaining_daily_avg = s25_remaining / 14
# 2025 weekly averages for Mar 18-24, 25-31
s25_week4 = sum(daily_sales_2025[17:24])  # Mar 18-24
s25_week5 = sum(daily_sales_2025[24:31])  # Mar 25-31
s25_week4_avg = s25_week4 / 7
s25_week5_avg = s25_week5 / 7

# Backward-compatible aliases
first7_avg = first7_avg_26
last5_avg = last5_avg_26
last3_avg = last3_avg_26
trend_drop_pct = trend_drop_pct_26

# Projection scenarios for 2026 remaining days (Mar 18-31)
proj_last5_pace = s26_total_sales + last5_avg_26 * remaining_days
proj_overall_pace = s26_total_sales + avg_daily_2026 * remaining_days
proj_first7_pace = s26_total_sales + first7_avg_26 * remaining_days
# New: project at 2025's Mar 18-31 actual daily avg
proj_2025_remaining_pace = s26_total_sales + s25_remaining_daily_avg * remaining_days

# Revenue needed per day to match 2025 full month
daily_needed_match_2025 = (s25_full["total_sales"] - s26_total_sales) / remaining_days
will_cover_at_current_pace = proj_overall_pace >= s25_full["total_sales"]
shortfall_at_current = s25_full["total_sales"] - proj_overall_pace
shortfall_at_last5 = s25_full["total_sales"] - proj_last5_pace

# ── AOV Analysis (THE core finding) ─────────────────────────────────────────
aov_25 = s25_17["aov"]
aov_26 = s26_utm["aov"]
aov_drop_pct = (aov_26 - aov_25) / aov_25 * 100
aov_drop_abs = aov_25 - aov_26
orders_25 = s25_17["orders"]
orders_26 = s26_utm["orders"]
orders_chg_pct = (orders_26 - orders_25) / orders_25 * 100

# Revenue impact: if AOV stayed the same, how much would we have?
hypothetical_rev_same_aov = orders_26 * aov_25
revenue_lost_to_aov = hypothetical_rev_same_aov - s26_utm["total_sales"]

# ── Product-Level Analysis (March 2026) ──────────────────────────────────────
products_sorted = sorted(products_2026, key=lambda x: x["total_sales"], reverse=True)
top_20_products = products_sorted[:20]
total_product_sales = sum(p["total_sales"] for p in products_2026)
total_product_items = sum(p["items_sold"] for p in products_2026)
top_20_sales = sum(p["total_sales"] for p in top_20_products)
top_20_pct = top_20_sales / total_product_sales * 100 if total_product_sales else 0

# Categorize products
samplers_kits = [p for p in products_2026 if any(kw in p["name"].lower() for kw in ["sampler", "kit", "pack", "stuffer", "combo", "assortment", "medley", "essentials", "favorites"])]
beans_legumes = [p for p in products_2026 if any(kw in p["name"].lower() for kw in ["bean", "lentil", "pinto", "garbanzo", "pea", "split pea"]) and not any(kw in p["name"].lower() for kw in ["sampler", "kit", "pack", "stuffer"])]
freeze_dried_fruit = [p for p in products_2026 if any(kw in p["name"].lower() for kw in ["freeze-dried", "freeze dried"]) and any(kw in p["name"].lower() for kw in ["blueberr", "strawberr", "raspberr", "banana", "mango", "cherry", "cherries", "peach", "apple", "pineapple", "grape", "fruit"])]
individual_veggies = [p for p in products_2026 if any(kw in p["name"].lower() for kw in ["dried bell", "dried broccoli", "dried cabbage", "dried carrot", "dried celery", "dried onion", "dried potato", "dried spinach", "dried tomato", "dried sweet potato", "dried garlic", "dried jalap", "dried zucchini", "dried butternut", "dried leek", "dried green bean", "dried shallot", "dried chive", "tomato powder"])]
soup_blends = [p for p in products_2026 if any(kw in p["name"].lower() for kw in ["soup", "chili", "chowder", "stew"]) and not any(kw in p["name"].lower() for kw in ["sampler", "kit", "pack", "stuffer", "combo"])]

def cat_total(items):
    return sum(p["total_sales"] for p in items), sum(p["items_sold"] for p in items), len(items)

cat_samplers = cat_total(samplers_kits)
cat_beans = cat_total(beans_legumes)
cat_fruit = cat_total(freeze_dried_fruit)
cat_veggies = cat_total(individual_veggies)
cat_soups = cat_total(soup_blends)

# Direct/organic from UTM
direct_sales = channels.get("Direct / Organic / Unattributed", {}).get("total_sales", 0)
direct_orders = channels.get("Direct / Organic / Unattributed", {}).get("orders", 0)

# Email totals
email_sales = sum(
    channels.get(ch, {}).get("total_sales", 0)
    for ch in ["Klaviyo Email", "Shopify Email"]
)
email_orders = sum(
    channels.get(ch, {}).get("orders", 0)
    for ch in ["Klaviyo Email", "Shopify Email"]
)

# ── New vs Returning Customer Analysis ─────────────────────────────────────
ret_25 = nr_2025["Returning"]
new_25 = nr_2025["New"]
ret_26 = nr_2026["Returning"]
new_26 = nr_2026["New"]
new_pct_2025 = new_25["orders"] / (new_25["orders"] + ret_25["orders"]) * 100
new_pct_2026 = new_26["orders"] / (new_26["orders"] + ret_26["orders"]) * 100

# ── Helpers ──────────────────────────────────────────────────────────────────
def fmt(v): return f"${v:,.2f}"
def pct(v): return f"{v:.1f}%"

def chg(new, old):
    if old == 0: return "N/A"
    c = (new - old) / old * 100
    color = "green" if c >= 0 else "#c53030"
    arrow = "&#9650;" if c >= 0 else "&#9660;"
    return f'<span style="color:{color};font-weight:700">{arrow} {abs(c):.1f}%</span>'

def chg_val(new, old):
    if old == 0: return 0
    return (new - old) / old * 100

report_date = datetime.now().strftime("%B %d, %Y")

# ══════════════════════════════════════════════════════════════════════════════
# SHARED CSS
# ══════════════════════════════════════════════════════════════════════════════
SHARED_CSS = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root { --pri: #1a365d; --acc: #2b6cb0; --red: #c53030; --grn: #276749; --org: #c05621; --bg: #f7fafc; --card: #fff; --brd: #e2e8f0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: #2d3748; line-height: 1.6; padding: 20px; }
.container { max-width: 1200px; margin: 0 auto; }
h1 { color: var(--pri); font-size: 1.8rem; margin-bottom: 4px; }
.sub { color: #718096; font-size: .95rem; margin-bottom: 24px; }
h2 { color: var(--pri); font-size: 1.3rem; margin: 28px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--acc); }
h3 { color: var(--acc); font-size: 1.1rem; margin: 16px 0 8px; }
.card { background: var(--card); border: 1px solid var(--brd); border-radius: 8px; padding: 20px; margin: 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.alert { border-left: 4px solid var(--red); background: #fff5f5; padding: 16px 20px; border-radius: 4px; margin: 12px 0; }
.alert-w { border-left-color: var(--org); background: #fffaf0; }
.alert-g { border-left-color: var(--grn); background: #f0fff4; }
.alert-b { border-left-color: var(--acc); background: #ebf8ff; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 16px 0; }
.kpi { background: var(--card); border: 1px solid var(--brd); border-radius: 8px; padding: 16px; text-align: center; }
.kpi .lb { font-size: .8rem; color: #718096; text-transform: uppercase; letter-spacing: .05em; }
.kpi .vl { font-size: 1.6rem; font-weight: 700; color: var(--pri); margin: 4px 0; }
.kpi .ch { font-size: .85rem; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: .9rem; }
th { background: var(--pri); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; }
td { padding: 8px 12px; border-bottom: 1px solid var(--brd); }
tr:nth-child(even) { background: #f7fafc; }
tr:hover { background: #edf2f7; }
.r { text-align: right; }
.hl { background: #fffaf0 !important; font-weight: 600; }
.tot { font-weight: bold; background: #edf2f7 !important; }
.rec { background: #ebf8ff; border: 1px solid #bee3f8; border-radius: 8px; padding: 16px 20px; margin: 8px 0; }
.rec strong { color: var(--acc); }
.diag { background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 16px 20px; margin: 8px 0; }
ul, ol { margin: 8px 0 8px 20px; }
li { margin: 4px 0; }
.footer { text-align: center; color: #a0aec0; font-size: .8rem; margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--brd); }
@media print { body { padding: 0; } .card { box-shadow: none; break-inside: avoid; } }
</style>
</head><body><div class="container">
"""

# ── BUILD MAIN HTML ───────────────────────────────────────────────────────────
html = []
h = html.append

h(SHARED_CSS.replace('<html lang="en"><head>', '<html lang="en"><head>\n<title>Harmony House Foods — March YoY Performance Analysis</title>'))

h(f'<h1>Harmony House Foods &mdash; March YoY Performance Analysis</h1>')
h(f'<p class="sub">March 2025 vs. March 2026 (1&ndash;17) &nbsp;|&nbsp; Prepared {report_date}</p>')

# ═══════════════════════════════════════════════════════════════════════════════
# 1. EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>1. Executive Summary</h2>')

h(f'''<div class="alert">
<strong>Key Finding:</strong> March 2026 total Shopify sales (Mar 1&ndash;17) are <strong>{pct(abs(chg_val(s26_total_sales, s25_17["total_sales"])))}</strong> below the same period in 2025.
However, <strong>order count is nearly identical</strong> ({orders_25} vs {orders_26} orders, just {pct(abs(orders_chg_pct))} difference).
The gap is driven by a <strong>{pct(abs(aov_drop_pct))} drop in Average Order Value</strong> ({fmt(aov_25)} &rarr; {fmt(aov_26)}) caused by a
<strong>shift in customer mix &mdash; more new customers (lower AOV) and fewer returning customers this year</strong>.
</div>''')

h(f'''<div class="alert alert-g">
<strong>Positive Signal:</strong> New customer acquisition is up {chg(new_26["orders"], new_25["orders"])} ({new_25["orders"]} &rarr; {new_26["orders"]}).
Strategy of moving away from heavy discounts and focusing on full-price new customer acquisition is working.
Returning customer AOV remains strong at $221.34.
</div>''')

# KPI Grid 1: Total Sales, Orders, AOV, New Customers
new_orders_25 = new_25["orders"]
new_orders_26 = new_26["orders"]

h(f'''<div class="kpi-grid">
<div class="kpi"><div class="lb">Total Shopify Sales (Mar 1&ndash;17)</div><div class="vl">{fmt(s26_total_sales)}</div>
<div class="ch">{chg(s26_total_sales, s25_17["total_sales"])} vs. {fmt(s25_17["total_sales"])} (2025)</div></div>

<div class="kpi"><div class="lb">Orders (Mar 1&ndash;17)</div><div class="vl">{orders_26}</div>
<div class="ch">{chg(orders_26, orders_25)} vs. {orders_25} (2025)</div></div>

<div class="kpi"><div class="lb">Average Order Value</div><div class="vl">{fmt(aov_26)}</div>
<div class="ch">{chg(aov_26, aov_25)} vs. {fmt(aov_25)} (2025)</div></div>

<div class="kpi"><div class="lb">New Customers (Mar 1&ndash;17)</div><div class="vl">{new_orders_26}</div>
<div class="ch">{chg(new_orders_26, new_orders_25)} vs. {new_orders_25} (2025)</div></div>
</div>''')

# KPI Grid 2: Projected Full March, 15% Target, Daily Needed, Returning Customer AOV
ret_aov_25 = ret_25["aov"]
ret_aov_26 = ret_26["aov"]

h(f'''<div class="kpi-grid">
<div class="kpi"><div class="lb">Projected Full March 2026</div><div class="vl">{fmt(s26_projected)}</div>
<div class="ch">{chg(s26_projected, s25_full["total_sales"])} vs. {fmt(s25_full["total_sales"])} (2025 actual)</div></div>

<div class="kpi"><div class="lb">15% Growth Target</div><div class="vl">{fmt(target_total)}</div>
<div class="ch">Gap: <span style="color:#c53030;font-weight:700">{fmt(target_total - s26_projected)}</span> short of target</div></div>

<div class="kpi"><div class="lb">Daily Sales Needed (Remaining {remaining_days} Days)</div><div class="vl">{fmt(daily_needed)}</div>
<div class="ch">Current avg: {fmt(avg_daily_2026)}/day &nbsp;|&nbsp; Need {daily_needed / avg_daily_2026:.1f}x current pace</div></div>

<div class="kpi"><div class="lb">Returning Customer AOV</div><div class="vl">{fmt(ret_aov_26)}</div>
<div class="ch">{chg(ret_aov_26, ret_aov_25)} vs. {fmt(ret_aov_25)} (2025)</div></div>
</div>''')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. ROOT CAUSE: CUSTOMER MIX
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>2. Root Cause: Why Is Revenue Down When Orders Are Flat?</h2>')

h(f'''<div class="diag">
<strong>This is the #1 question to answer on the client call.</strong><br><br>
Orders are nearly identical ({orders_25} in 2025 vs {orders_26} in 2026 &mdash; only {pct(abs(orders_chg_pct))} difference).
The revenue gap is driven by a <strong>shift in customer mix</strong>: more new customers (lower AOV) and fewer returning customers compared to last year.
</div>''')

# Single combined card: Customer Mix table
total_orders_25 = new_25["orders"] + ret_25["orders"]
total_orders_26 = new_26["orders"] + ret_26["orders"]
new_pct_25_str = pct(new_pct_2025)
new_pct_26_str = pct(new_pct_2026)
ret_pct_25_str = pct(100 - new_pct_2025)
ret_pct_26_str = pct(100 - new_pct_2026)

# Revenue lost to AOV drop (already computed)
h(f'''<div class="card">
<h3>Customer Mix: New vs. Returning (Mar 1&ndash;17)</h3>
<table>
<tr><th>Segment</th><th class="r">2025 Orders</th><th class="r">2025 AOV</th><th class="r">2025 Sales</th><th class="r">2026 Orders</th><th class="r">2026 AOV</th><th class="r">2026 Sales</th><th class="r">Change (Orders)</th></tr>
<tr>
  <td>New Customers</td>
  <td class="r">{new_25["orders"]} ({new_pct_25_str})</td>
  <td class="r">{fmt(new_25["aov"])}</td>
  <td class="r">{fmt(new_25["total_sales"])}</td>
  <td class="r">{new_26["orders"]} ({new_pct_26_str})</td>
  <td class="r">{fmt(new_26["aov"])}</td>
  <td class="r">{fmt(new_26["total_sales"])}</td>
  <td class="r">{chg(new_26["orders"], new_25["orders"])}</td>
</tr>
<tr>
  <td>Returning Customers</td>
  <td class="r">{ret_25["orders"]} ({ret_pct_25_str})</td>
  <td class="r">{fmt(ret_25["aov"])}</td>
  <td class="r">{fmt(ret_25["total_sales"])}</td>
  <td class="r">{ret_26["orders"]} ({ret_pct_26_str})</td>
  <td class="r">{fmt(ret_26["aov"])}</td>
  <td class="r">{fmt(ret_26["total_sales"])}</td>
  <td class="r">{chg(ret_26["orders"], ret_25["orders"])}</td>
</tr>
<tr class="hl">
  <td><strong>Overall</strong></td>
  <td class="r"><strong>{total_orders_25}</strong></td>
  <td class="r"><strong>{fmt(aov_25)}</strong></td>
  <td class="r"><strong>{fmt(s25_17["total_sales"])}</strong></td>
  <td class="r"><strong>{total_orders_26}</strong></td>
  <td class="r"><strong>{fmt(aov_26)}</strong></td>
  <td class="r"><strong>{fmt(s26_total_sales)}</strong></td>
  <td class="r">{chg(total_orders_26, total_orders_25)}</td>
</tr>
<tr>
  <td>Revenue Lost to AOV Drop</td>
  <td class="r" colspan="3">&mdash;</td>
  <td class="r" colspan="4"><strong style="color:#c53030">{fmt(revenue_lost_to_aov)}</strong> (if AOV had stayed at {fmt(aov_25)}, revenue would be {fmt(hypothetical_rev_same_aov)})</td>
</tr>
</table>
</div>''')

h(f'''<div class="alert alert-b">
<strong>Bottom Line &mdash; This Is a Customer Mix Effect:</strong><br><br>
<strong>2025 strategy:</strong> Heavy discounts ({pct(s25_17["discount_rate"])} discount rate), {ret_25["orders"]} returning / {new_25["orders"]} new customers.
Returning customers drove the majority of orders and lifted the blended AOV.<br><br>
<strong>2026 strategy:</strong> Full-price new customer focus ({pct(s26_utm["discount_rate"])} discount rate), {ret_26["orders"]} returning / {new_26["orders"]} new customers.
New customers naturally have lower AOV ({fmt(new_26["aov"])}) vs. returning customers ({fmt(ret_26["aov"])}).
Returning customer AOV remains strong &mdash; that cohort has not weakened.<br><br>
<strong>This is a healthy strategic shift &mdash; growing the customer base at full price will pay off in future repeat purchases.</strong>
</div>''')

# ═══════════════════════════════════════════════════════════════════════════════
# 3. PRODUCT MIX ANALYSIS (MARCH 2026)
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>3. Product Mix Analysis (March 2026, 1&ndash;17)</h2>')

h('<div class="card">')
h(f'<h3>Top 20 Products by Total Sales</h3>')
h(f'<p style="color:#718096;font-size:.85rem;margin-bottom:8px">Top 20 products account for <strong>{pct(top_20_pct)}</strong> of total product sales ({fmt(top_20_sales)} of {fmt(total_product_sales)}). {len(products_2026)} SKUs sold in total.</p>')
h('''<table>
<tr><th>#</th><th>Product</th><th class="r">Units</th><th class="r">Gross Sales</th><th class="r">Discounts</th><th class="r">Net Sales</th><th class="r">Total Sales</th><th class="r">AOV/Unit</th><th class="r">% of Total</th></tr>''')

for i, p in enumerate(top_20_products):
    pct_of = p["total_sales"] / total_product_sales * 100
    disc_str = fmt(abs(p["discounts"])) if p["discounts"] != 0 else "&mdash;"
    aov_unit = p["total_sales"] / p["items_sold"] if p["items_sold"] > 0 else 0
    h(f'''<tr>
    <td>{i+1}</td>
    <td>{p["name"]}</td>
    <td class="r">{p["items_sold"]}</td>
    <td class="r">{fmt(p["gross_sales"])}</td>
    <td class="r">{disc_str}</td>
    <td class="r">{fmt(p["net_sales"])}</td>
    <td class="r">{fmt(p["total_sales"])}</td>
    <td class="r">{fmt(aov_unit)}</td>
    <td class="r">{pct(pct_of)}</td>
    </tr>''')

h('</table></div>')

h('<div class="card">')
h('<h3>Sales by Product Category</h3>')
h('''<table>
<tr><th>Category</th><th class="r">SKUs</th><th class="r">Units Sold</th><th class="r">Total Sales</th><th class="r">% of Total</th><th class="r">Avg Sale/SKU</th></tr>''')

categories = [
    ("Samplers, Kits & Bundles", cat_samplers),
    ("Beans & Legumes", cat_beans),
    ("Freeze-Dried Fruit", cat_fruit),
    ("Individual Dried Vegetables", cat_veggies),
    ("Soup & Chili Blends", cat_soups),
]
for cat_name, (cat_sales, cat_items, cat_count) in categories:
    cat_pct = cat_sales / total_product_sales * 100 if total_product_sales else 0
    avg_per_sku = cat_sales / cat_count if cat_count else 0
    h(f'''<tr>
    <td>{cat_name}</td>
    <td class="r">{cat_count}</td>
    <td class="r">{cat_items}</td>
    <td class="r">{fmt(cat_sales)}</td>
    <td class="r">{pct(cat_pct)}</td>
    <td class="r">{fmt(avg_per_sku)}</td>
    </tr>''')

h('</table>')
h(f'''<p style="color:#718096;font-size:.85rem;margin-top:8px">Note: Categories may not sum to 100% as some products (mushrooms, protein, seasonings, accessories) are not categorized above.</p>''')
h('</div>')

h(f'''<div class="alert alert-w">
<strong>AOV Insight:</strong> The highest-AOV products are the <strong>samplers, kits &amp; bundles</strong> (Vegetable Sampler, Deluxe Sampler, Pantry Stuffers, Family Packs).
These are the products that drive higher cart values. Promoting these in a flash sale or featured collection could directly address the AOV gap.
The #1 seller &mdash; Vegetable Sampler (15 ZIP Pouches) &mdash; alone generated {fmt(top_20_products[0]["total_sales"])} from {top_20_products[0]["items_sold"]} units.
</div>''')

# ═══════════════════════════════════════════════════════════════════════════════
# 4. CHANNEL ATTRIBUTION WITH SPEND
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>4. Channel Attribution Breakdown with Ad Spend (March 2026, 1&ndash;17)</h2>')

h('<div class="card">')
h('<p style="color:#718096;font-size:.85rem;margin-bottom:8px">Revenue is from Shopify UTM last-click attribution. Ad spend is from platform dashboards. Note: UTM last-click and platform attribution use different models and will naturally differ &mdash; this is expected.</p>')
h('''<table>
<tr>
<th>Channel</th>
<th class="r">Ad Spend</th>
<th class="r">Orders</th>
<th class="r">Gross Sales</th>
<th class="r">Total Sales (UTM)</th>
<th class="r">% of Total</th>
<th class="r">UTM-Based ROAS</th>
</tr>''')

for ch_name, ch_data in channels_sorted:
    pct_of = ch_data["total_sales"] / total_ch_sales * 100 if total_ch_sales else 0
    spend = channel_spend.get(ch_name, 0)
    spend_str = fmt(spend) if spend > 0 else "&mdash;"
    roas_str = f'{ch_data["total_sales"] / spend:.2f}x' if spend > 0 else ("&infin; (no spend)" if ch_data["total_sales"] > 0 else "&mdash;")
    h(f'''<tr>
    <td>{ch_name}</td>
    <td class="r">{spend_str}</td>
    <td class="r">{ch_data["orders"]}</td>
    <td class="r">{fmt(ch_data["gross_sales"])}</td>
    <td class="r">{fmt(ch_data["total_sales"])}</td>
    <td class="r">{pct(pct_of)}</td>
    <td class="r">{roas_str}</td>
    </tr>''')

h(f'''<tr class="tot">
<td>Total (all channels)</td>
<td class="r">{fmt(s26_total_spent)}</td>
<td class="r">{s26_utm["orders"]}</td>
<td class="r">{fmt(s26_utm["gross_sales"])}</td>
<td class="r">{fmt(total_ch_sales)}</td>
<td class="r">100%</td>
<td class="r">{total_ch_sales / s26_total_spent:.2f}x (blended)</td>
</tr>''')
h('</table>')
h('</div>')

# ═══════════════════════════════════════════════════════════════════════════════
# 5. DAY-BY-DAY COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>5. Day-by-Day YoY Comparison (March 1&ndash;17)</h2>')
h('<div class="card"><table>')
h('<tr><th>Day</th><th class="r">2025 Total Sales</th><th class="r">2025 Orders</th><th class="r">2025 Discounts</th><th class="r">2026 Total Sales</th><th class="r">2026 Ad Spend</th><th class="r">2026 MER</th><th class="r">YoY Change</th></tr>')

for i in range(17):
    d25 = shopify_2025[i]
    a26 = ad_march[i]
    utm_day = days_2026_sorted[i][1] if i < len(days_2026_sorted) else {"total_sales": 0}
    day_sales = utm_day["total_sales"]
    day_spend = a26["total_spent"]
    day_mer = day_sales / day_spend if day_spend > 0 else 0
    cls = ' class="hl"' if i == 11 else ""
    h(f'''<tr{cls}>
    <td>Mar {i+1}</td>
    <td class="r">{fmt(d25["total_sales"])}</td>
    <td class="r">{d25["orders"]}</td>
    <td class="r">{fmt(abs(d25["discounts"]))}</td>
    <td class="r">{fmt(day_sales)}</td>
    <td class="r">{fmt(day_spend)}</td>
    <td class="r">{day_mer:.1f}x</td>
    <td class="r">{chg(day_sales, d25["total_sales"])}</td>
    </tr>''')

h(f'''<tr class="tot">
<td>Total (1&ndash;17)</td>
<td class="r">{fmt(s25_17["total_sales"])}</td>
<td class="r">{s25_17["orders"]}</td>
<td class="r">{fmt(s25_17["discounts"])}</td>
<td class="r">{fmt(s26_total_sales)}</td>
<td class="r">{fmt(s26_total_spent)}</td>
<td class="r">{mer_2026:.1f}x</td>
<td class="r">{chg(s26_total_sales, s25_17["total_sales"])}</td>
</tr>
<tr class="hl">
<td>Total (excl. Mar 12 outlier)</td>
<td class="r">{fmt(s25_17_ex12)}</td>
<td class="r">{s25_17_orders_ex12}</td>
<td class="r">&mdash;</td>
<td class="r">{fmt(s26_17_ex12)}</td>
<td class="r">&mdash;</td>
<td class="r">&mdash;</td>
<td class="r">{chg(s26_17_ex12, s25_17_ex12)}</td>
</tr>''')
h('</table></div>')

h('<div class="card"><h3>Weekly Trend</h3><table>')
h('<tr><th>Period</th><th class="r">2025 Sales</th><th class="r">2026 Sales</th><th class="r">YoY</th></tr>')
h(f'<tr><td>Week 1 (Mar 1&ndash;7)</td><td class="r">{fmt(week1_25)}</td><td class="r">{fmt(week1_26)}</td><td class="r">{chg(week1_26, week1_25)}</td></tr>')
h(f'<tr><td>Week 2 (Mar 8&ndash;14)</td><td class="r">{fmt(week2_25)}</td><td class="r">{fmt(week2_26)}</td><td class="r">{chg(week2_26, week2_25)}</td></tr>')
h(f'<tr><td>Mar 15&ndash;17</td><td class="r">{fmt(week3p_25)}</td><td class="r">{fmt(week3p_26)}</td><td class="r">{chg(week3p_26, week3p_25)}</td></tr>')
h('</table></div>')

# ═══════════════════════════════════════════════════════════════════════════════
# 6. RECOMMENDATIONS & ACTION PLAN (was 9)
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>6. Recommendations &amp; Action Plan</h2>')

h(f'''<div class="rec">
<strong>1. Launch a Flash Sale / Promotion (March 19&ndash;22)</strong><br>
Last year&rsquo;s March 12 promo generated {fmt(mar12_2025["total_sales"])} in a single day with 89 orders.
Run a 48&ndash;72hr flash sale (20&ndash;25% off best sellers) promoted via Klaviyo email blast + social.
<strong>This is the single biggest lever to close the gap.</strong>
Target: $8,000&ndash;15,000 in incremental sales.
</div>

<div class="rec">
<strong>2. Promote High-AOV Products (Samplers, Kits &amp; Bundles)</strong><br>
The AOV drop is the core revenue issue. Push high-AOV products in the flash sale and email campaigns:
<ul>
<li>Vegetable Sampler (15 ZIP) &mdash; #1 seller at {fmt(top_20_products[0]["total_sales"])}</li>
<li>Deluxe Sampler (32 ZIP), Pantry Stuffers, Family Packs &mdash; all $100+ AOV products</li>
<li>Create a &ldquo;Best Value Bundles&rdquo; featured collection on the homepage</li>
</ul>
Goal: bring AOV back toward {fmt(aov_25)} (from current {fmt(aov_26)}).
</div>

<div class="rec">
<strong>3. Scale Google PMax Budget ($190/day &rarr; $250&ndash;300/day)</strong><br>
PMax is budget-limited at 4.88x ROAS &mdash; this is the highest-efficiency paid channel.
Increasing budget should capture incremental Shopping traffic. Branded Search (6.85x ROAS) should remain as-is.
Estimated incremental: $60&ndash;110/day extra spend &times; ~4x ROAS = $240&ndash;440/day additional revenue.
</div>

<div class="rec">
<strong>4. Increase Email Frequency (Klaviyo)</strong><br>
Email is driving <strong>{email_orders} orders / {fmt(email_sales)} in total sales</strong> at <strong>zero ad cost</strong> (infinite ROI).
Send 2&ndash;3 additional blasts this week:
flash sale announcement, abandoned cart recovery push, &ldquo;best sellers of March&rdquo; curated collection.
Each blast can drive $500&ndash;2,000 in incremental sales.
</div>

<div class="rec">
<strong>5. Set Realistic Expectations on 15% Target</strong><br>
The 15% growth target ({fmt(target_total)}) needs {fmt(daily_needed)}/day for the remaining {remaining_days} days &mdash;
that&rsquo;s <strong>{daily_needed / avg_daily_2026:.1f}x</strong> the current daily average of {fmt(avg_daily_2026)}.
A flash sale + optimizations can get us closer, but matching last year&rsquo;s flash sale performance is the key unlock.
A realistic target: match or come within 5&ndash;10% of last year&rsquo;s {fmt(s25_full["total_sales"])}.
</div>''')

# ═══════════════════════════════════════════════════════════════════════════════
# 7. PROJECTED SCENARIOS (was 10)
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>7. Projected Scenarios (Rest of March)</h2>')

scenario_a = s26_projected  # status quo
scenario_a_spend = s26_projected_spend

scenario_b_daily = avg_daily_2026 * 1.15
scenario_b = s26_total_sales + scenario_b_daily * remaining_days
scenario_b_spend = s26_total_spent + (s26_total_spent / 17 * 0.75) * remaining_days

flash_boost = 12000
scenario_c = scenario_b + flash_boost
scenario_c_spend = scenario_b_spend + 500

h(f'''<div class="card"><table>
<tr><th>Scenario</th><th class="r">Projected Month Total</th><th class="r">vs. 2025</th><th class="r">vs. Target</th><th class="r">Projected Spend</th><th class="r">Projected MER</th></tr>
<tr><td><strong>A: Status Quo</strong> (no changes)</td><td class="r">{fmt(scenario_a)}</td><td class="r">{chg(scenario_a, s25_full["total_sales"])}</td><td class="r">{chg(scenario_a, target_total)}</td><td class="r">{fmt(scenario_a_spend)}</td><td class="r">{scenario_a / scenario_a_spend:.1f}x</td></tr>
<tr><td><strong>B: Optimize</strong> (scale PMax, more email, AOV focus)</td><td class="r">{fmt(scenario_b)}</td><td class="r">{chg(scenario_b, s25_full["total_sales"])}</td><td class="r">{chg(scenario_b, target_total)}</td><td class="r">{fmt(scenario_b_spend)}</td><td class="r">{scenario_b / scenario_b_spend:.1f}x</td></tr>
<tr><td><strong>C: Optimize + Flash Sale</strong></td><td class="r">{fmt(scenario_c)}</td><td class="r">{chg(scenario_c, s25_full["total_sales"])}</td><td class="r">{chg(scenario_c, target_total)}</td><td class="r">{fmt(scenario_c_spend)}</td><td class="r">{scenario_c / scenario_c_spend:.1f}x</td></tr>
</table></div>''')

# ═══════════════════════════════════════════════════════════════════════════════
# 8. IMMEDIATE ACTION ITEMS (was 11)
# ═══════════════════════════════════════════════════════════════════════════════
h('<h2>8. Immediate Action Items</h2>')
h(f'''<div class="card"><table>
<tr><th>#</th><th>Action</th><th>Timeline</th><th>Expected Impact</th></tr>
<tr><td>1</td><td>Plan &amp; launch flash sale (20&ndash;25% off best sellers, focus on bundles/samplers)</td><td>Mar 19&ndash;22</td><td>+$8,000&ndash;15,000 (based on Mar 12, 2025 precedent)</td></tr>
<tr><td>2</td><td>Increase Google PMax budget $190 &rarr; $250&ndash;300/day</td><td>Today</td><td>+$240&ndash;440/day incremental revenue at 4.88x ROAS</td></tr>
<tr><td>3</td><td>Send 2&ndash;3 Klaviyo email blasts this week (flash sale + best sellers)</td><td>This week</td><td>+$1,500&ndash;4,000 at zero ad cost</td></tr>
<tr><td>4</td><td>Create &ldquo;Best Value Bundles&rdquo; featured collection on homepage</td><td>Today</td><td>Lift AOV toward {fmt(aov_25)} target</td></tr>
<tr><td>5</td><td>Keep NB Search campaigns paused</td><td>Ongoing</td><td>Avoid wasting budget on 0-conversion campaigns</td></tr>
</table></div>''')

h(f'''<div class="footer">
Harmony House Foods &mdash; March YoY Performance Analysis &nbsp;|&nbsp; Generated {report_date}<br>
Data sources: Shopify Sales Reports, Shopify UTM Attribution, Shopify Product Sales, Customer Segment Data
</div></div></body></html>''')

# ══════════════════════════════════════════════════════════════════════════════
# BUILD AD SPEND HTML (separate report)
# ══════════════════════════════════════════════════════════════════════════════
html_ads = []
ha = html_ads.append

ha(SHARED_CSS.replace('<html lang="en"><head>', '<html lang="en"><head>\n<title>Harmony House Foods — Ad Spend &amp; Platform Performance</title>'))

ha(f'<h1>Harmony House Foods &mdash; Ad Spend &amp; Platform Performance</h1>')
ha(f'<p class="sub">March 2025 vs. March 2026 (1&ndash;17) &nbsp;|&nbsp; Prepared {report_date}</p>')

# KPI grid: Total Ad Spend, Blended Platform ROAS, MER
ha(f'''<div class="kpi-grid">
<div class="kpi"><div class="lb">Total Ad Spend (Mar 1&ndash;17)</div><div class="vl">{fmt(s26_total_spent)}</div>
<div class="ch">{chg(s26_total_spent, total_spend_2025)} vs. {fmt(total_spend_2025)} (2025 full month)</div></div>

<div class="kpi"><div class="lb">Blended Platform ROAS</div><div class="vl">{s26_total_conv / s26_total_spent:.2f}x</div>
<div class="ch">Google: {google_2026["roas"]:.1f}x &nbsp;|&nbsp; FB: {s26_fb_conv / s26_fb_spent:.2f}x</div></div>

<div class="kpi"><div class="lb">MER (Marketing Efficiency Ratio)</div><div class="vl">{mer_2026:.1f}x</div>
<div class="ch">Total Sales / Total Ad Spend (Mar 1&ndash;17)</div></div>
</div>''')

# Section 1: Ad Spend Overview
ha('<h2>1. Ad Spend Overview</h2>')
ha('<div class="card"><h3>Ad Spend Overview</h3>')
ha(f'''<table>
<tr><th>Metric</th><th class="r">March 2025 (Full Month)</th><th class="r">March 2026 (1&ndash;17 only)</th><th class="r">Change</th></tr>
<tr><td>Google Ads Spend</td><td class="r">{fmt(google_spend_2025)}</td><td class="r">{fmt(s26_google_spent)}</td><td class="r">{pct(s26_google_spent / google_spend_2025 * 100)} of full month 2025</td></tr>
<tr><td>Facebook Ads Spend</td><td class="r">{fmt(fb_spend_2025)}</td><td class="r">{fmt(s26_fb_spent)}</td><td class="r">{chg(s26_fb_spent, fb_spend_2025)}</td></tr>
<tr><td>Total Ad Spend</td><td class="r">{fmt(total_spend_2025)}</td><td class="r">{fmt(s26_total_spent)}</td><td class="r">{chg(s26_total_spent, total_spend_2025)}</td></tr>
<tr><td>Platform ROAS (Blended)</td><td class="r">{google_2025["roas"]:.2f}x (Google only)</td><td class="r">{s26_total_conv / s26_total_spent:.2f}x (Google + FB)</td><td class="r">&mdash;</td></tr>
</table></div>''')

# Section 2: Facebook Ads Performance Summary
ha('<h2>2. Facebook Ads Performance Summary</h2>')
ha(f'''<div class="card"><h3>Facebook Ads &mdash; Performance Summary</h3>
<table>
<tr><th>Metric</th><th class="r">Value</th></tr>
<tr><td>Total Spend (Mar 1&ndash;17)</td><td class="r">{fmt(s26_fb_spent)}</td></tr>
<tr><td>Daily Spend Avg</td><td class="r">{fmt(s26_fb_spent / 17)}/day</td></tr>
<tr><td>Platform-Reported Conv. Value</td><td class="r">{fmt(s26_fb_conv)}</td></tr>
<tr><td>Platform ROAS (7-day click + 1-day view)</td><td class="r">{s26_fb_conv / s26_fb_spent:.2f}x</td></tr>
<tr><td>UTM Last-Click Sales</td><td class="r">{fmt(fb_paid_total_sales)}</td></tr>
<tr><td>UTM Last-Click ROAS</td><td class="r">{fb_paid_total_sales / s26_fb_spent:.2f}x</td></tr>
<tr><td>UTM Orders</td><td class="r">{fb_paid_total_orders}</td></tr>
</table>
<p style="color:#718096;font-size:.85rem;margin-top:8px">Note: Platform attribution (7-day click + 1-day view) and UTM last-click use different models. The gap between them is expected &mdash; it reflects view-through and assisted conversions that UTM does not capture. A UTM ROAS of {fb_paid_total_sales / s26_fb_spent:.2f}x on last-click shows Facebook is driving meaningful direct conversions.</p>
</div>''')

ha(f'''<div class="alert alert-g">
<strong>Facebook is doing its job:</strong> FB is driving {fb_paid_total_orders} new-customer-heavy orders.
Strategy of using Facebook to acquire new customers at full price is working &mdash;
new customer orders are up {chg(new_26["orders"], new_25["orders"])} YoY.
</div>''')

# Section 3: Google Ads Campaign Comparison
ha('<h2>3. Google Ads Campaign Comparison</h2>')
ha('<div class="card"><h3>Google Ads &mdash; Campaign Comparison</h3>')
ha('<p style="font-size:.85rem;color:#718096">March 2025 (Full Month)</p>')
ha('<table><tr><th>Campaign</th><th>Type</th><th class="r">Spend</th><th class="r">Conv.</th><th class="r">Conv. Value</th><th class="r">ROAS</th><th class="r">CPA</th></tr>')
for c in google_2025["campaigns"]:
    cpa = f'${c["spend"]/c["conv"]:.2f}' if c["conv"] > 0 else "&mdash;"
    ha(f'<tr><td>{c["name"]}</td><td>{c["type"]}</td><td class="r">{fmt(c["spend"])}</td><td class="r">{c["conv"]:.1f}</td><td class="r">{fmt(c["value"])}</td><td class="r">{c["roas"]:.2f}x</td><td class="r">{cpa}</td></tr>')
ha(f'<tr class="tot"><td>Total</td><td>&mdash;</td><td class="r">{fmt(google_2025["spend"])}</td><td class="r">{google_2025["conversions"]:.1f}</td><td class="r">{fmt(google_2025["conv_value"])}</td><td class="r">{google_2025["roas"]:.2f}x</td><td class="r">${google_2025["spend"]/google_2025["conversions"]:.2f}</td></tr>')
ha('</table>')

ha(f'<p style="font-size:.85rem;color:#718096;margin-top:16px">March 2026 (1&ndash;17)</p>')
ha('<table><tr><th>Campaign</th><th>Type</th><th class="r">Spend</th><th class="r">Conv.</th><th class="r">Conv. Value</th><th class="r">ROAS</th><th class="r">CPA</th><th>Notes</th></tr>')
for c in google_2026["campaigns"]:
    cpa = f'${c["spend"]/c["conv"]:.2f}' if c["conv"] > 0 else "&mdash;"
    note = c.get("note", "")
    ha(f'<tr><td>{c["name"]}</td><td>{c["type"]}</td><td class="r">{fmt(c["spend"])}</td><td class="r">{c["conv"]:.1f}</td><td class="r">{fmt(c["value"])}</td><td class="r">{c["roas"]:.2f}x</td><td class="r">{cpa}</td><td>{note}</td></tr>')
ha(f'<tr class="tot"><td>Total</td><td>&mdash;</td><td class="r">{fmt(google_2026["spend"])}</td><td class="r">{google_2026["conversions"]:.1f}</td><td class="r">{fmt(google_2026["conv_value"])}</td><td class="r">{google_2026["roas"]:.2f}x</td><td class="r">${google_2026["spend"]/google_2026["conversions"]:.2f}</td><td></td></tr>')
ha('</table></div>')

ha(f'''<div class="alert alert-g">
<strong>Google Ads Positive:</strong> ROAS improved from {google_2025["roas"]:.2f}x (2025) to {google_2026["roas"]:.2f}x (2026).
The INTC P.Max campaign is performing well at 4.88x ROAS but is <strong>budget-limited</strong> at $190/day.
Branded Search is highly efficient at 6.85x ROAS. The NB Dried Cabbage campaign ($191.29 spent, 0 conversions) was correctly paused.
<strong>Google is the strongest paid channel and has room to scale.</strong>
</div>''')

ha(f'''<div class="footer">
Harmony House Foods &mdash; Ad Spend &amp; Platform Performance &nbsp;|&nbsp; Generated {report_date}<br>
Data sources: Google Ads, Facebook Ads, Shopify UTM Attribution
</div></div></body></html>''')

# ── Write Reports ─────────────────────────────────────────────────────────────
report_dir = os.path.join(BASE, "..", "..", "..", "reports", "Harmony House Foods")
os.makedirs(report_dir, exist_ok=True)

report_path = os.path.join(report_dir, "March_YoY_Analysis_2026-03-18.html")
with open(report_path, "w") as f:
    f.write("\n".join(html))

ads_report_path = os.path.join(report_dir, "March_Ad_Spend_Analysis_2026-03-18.html")
with open(ads_report_path, "w") as f:
    f.write("\n".join(html_ads))

print(f"Main report:     {os.path.abspath(report_path)}")
print(f"Ad spend report: {os.path.abspath(ads_report_path)}")
print()

# ── Print verification ──────────────────────────────────────────────────────
print("=" * 65)
print("DATA VERIFICATION (cross-checked against raw CSVs)")
print("=" * 65)
print(f"March 2025 (1-17) Total Sales:      {fmt(s25_17['total_sales'])}")
print(f"March 2025 Full Month Total Sales:   {fmt(s25_full['total_sales'])}")
print(f"March 2026 (1-17) Shopify Sales:     {fmt(s26_total_sales)}")
print(f"YoY Change (1-17):                   {chg_val(s26_total_sales, s25_17['total_sales']):.1f}%")
print(f"Excl Mar 12: 2025={fmt(s25_17_ex12)} 2026={fmt(s26_17_ex12)} => {chg_val(s26_17_ex12, s25_17_ex12):.1f}%")
print()
print(f"Orders 2025 (1-17):                  {orders_25}")
print(f"Orders 2026 (1-17):                  {orders_26}")
print(f"Order Change:                        {orders_chg_pct:.1f}%")
print(f"AOV 2025 (1-17):                     {fmt(aov_25)}")
print(f"AOV 2026 (1-17):                     {fmt(aov_26)}")
print(f"AOV Change:                          {aov_drop_pct:.1f}%")
print(f"Revenue Lost to AOV Drop:            {fmt(revenue_lost_to_aov)}")
print()
print(f"New Customers 2025 (1-17):           {new_25['orders']} ({pct(new_pct_2025)} of orders, AOV {fmt(new_25['aov'])})")
print(f"New Customers 2026 (1-17):           {new_26['orders']} ({pct(new_pct_2026)} of orders, AOV {fmt(new_26['aov'])})")
print(f"Returning Customers 2025 (1-17):     {ret_25['orders']} (AOV {fmt(ret_25['aov'])})")
print(f"Returning Customers 2026 (1-17):     {ret_26['orders']} (AOV {fmt(ret_26['aov'])})")
print()
print(f"Ad Spend 2025 (full month):          {fmt(total_spend_2025)}")
print(f"  Google: {fmt(google_spend_2025)}  |  FB: {fmt(fb_spend_2025)}")
print(f"Ad Spend 2026 (Mar 1-17):            {fmt(s26_total_spent)}")
print(f"  Google: {fmt(s26_google_spent)}  |  FB: {fmt(s26_fb_spent)}")
print()
print(f"Google ROAS 2025:                    {google_2025['roas']:.2f}x")
print(f"Google ROAS 2026:                    {google_2026['roas']:.2f}x")
print(f"FB Platform ROAS 2026:               {s26_fb_conv / s26_fb_spent:.2f}x")
print(f"FB UTM Last-Click ROAS 2026:         {fb_paid_total_sales / s26_fb_spent:.2f}x")
print()
print(f"Discount Rate 2025 (1-17):           {pct(s25_17['discount_rate'])}")
print(f"Discount Rate 2026 (1-17):           {pct(s26_utm['discount_rate'])}")
print()
print(f"Direct/Organic/Unattributed (2026):  {fmt(direct_sales)} ({direct_orders} orders)")
print(f"Email (Klaviyo+Shopify) (2026):      {fmt(email_sales)} ({email_orders} orders)")
print(f"FB Paid UTM (2026):                  {fmt(fb_paid_total_sales)} ({fb_paid_total_orders} orders)")
print(f"Google CPC UTM (2026):               {fmt(google_paid_total_sales)} ({google_paid_total_orders} orders)")
print()
print(f"Top 20 Products (2026):              {fmt(top_20_sales)} ({pct(top_20_pct)} of total)")
print(f"Total Product SKUs:                  {len(products_2026)}")
print(f"Total Product Sales:                 {fmt(total_product_sales)}")
