#!/usr/bin/env python3
"""
Harmony House Foods — March YoY Analysis
Compares March 2025 vs March 2026 (1-17) performance.
Generates an HTML report with insights for client call.
"""

import csv
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Load Shopify March 2025 ──────────────────────────────────────────────────
def load_shopify_2025():
    rows = []
    with open(os.path.join(BASE, "shopify_march_2025.csv")) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "day": r["Day"],
                "orders": int(r["Orders"]),
                "gross_sales": float(r["Gross sales"]),
                "discounts": float(r["Discounts"]),
                "returns": float(r["Returns"]),
                "net_sales": float(r["Net sales"]),
                "shipping": float(r["Shipping charges"]),
                "taxes": float(r["Taxes"]),
                "total_sales": float(r["Total sales"]),
            })
    return rows

# ── Load UTM Shopify March 2026 ─────────────────────────────────────────────
def load_utm_2026():
    rows = []
    with open(os.path.join(BASE, "utm_shopify_march_2026.csv")) as f:
        reader = csv.DictReader(f)
        for r in reader:
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

# ── Load daily ad spend 2026 ────────────────────────────────────────────────
def load_ad_spend_2026():
    rows = []
    with open(os.path.join(BASE, "daily_ad_spend_2026.csv")) as f:
        reader = csv.DictReader(f)
        for r in reader:
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

# ── Calculations ─────────────────────────────────────────────────────────────
shopify_2025 = load_shopify_2025()
utm_2026 = load_utm_2026()
ad_spend_2026 = load_ad_spend_2026()

# --- March 2025 full month ---
s25_full = {
    "orders": sum(r["orders"] for r in shopify_2025),
    "gross_sales": sum(r["gross_sales"] for r in shopify_2025),
    "discounts": sum(abs(r["discounts"]) for r in shopify_2025),
    "net_sales": sum(r["net_sales"] for r in shopify_2025),
    "total_sales": sum(r["total_sales"] for r in shopify_2025),
}
s25_full["discount_rate"] = s25_full["discounts"] / s25_full["gross_sales"] * 100 if s25_full["gross_sales"] else 0
s25_full["avg_order_value"] = s25_full["total_sales"] / s25_full["orders"] if s25_full["orders"] else 0

# --- March 2025 first 17 days (for apples-to-apples) ---
s25_17 = shopify_2025[:17]  # March 1–17
s25_17_totals = {
    "orders": sum(r["orders"] for r in s25_17),
    "gross_sales": sum(r["gross_sales"] for r in s25_17),
    "discounts": sum(abs(r["discounts"]) for r in s25_17),
    "net_sales": sum(r["net_sales"] for r in s25_17),
    "total_sales": sum(r["total_sales"] for r in s25_17),
}
s25_17_totals["discount_rate"] = s25_17_totals["discounts"] / s25_17_totals["gross_sales"] * 100 if s25_17_totals["gross_sales"] else 0
s25_17_totals["avg_order_value"] = s25_17_totals["total_sales"] / s25_17_totals["orders"] if s25_17_totals["orders"] else 0

# --- March 2026 (1-17) from ad spend sheet (Shopify daily sales) ---
ad_march = [r for r in ad_spend_2026 if r["day"].startswith("2026-03")]
s26_17_shopify_total = sum(r["daily_shopify_sales"] for r in ad_march)
s26_17_fb_spent = sum(r["fb_spent"] for r in ad_march)
s26_17_google_spent = sum(r["google_spent"] for r in ad_march)
s26_17_total_spent = sum(r["total_spent"] for r in ad_march)
s26_17_fb_conv = sum(r["fb_conv_value"] for r in ad_march)
s26_17_google_conv = sum(r["google_conv_value"] for r in ad_march)
s26_17_total_conv = sum(r["total_conv_value"] for r in ad_march)

# --- March 2026 from UTM data (aggregate by day for totals) ---
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

s26_17_totals = {
    "orders": sum(v["orders"] for v in days_2026.values()),
    "gross_sales": sum(v["gross_sales"] for v in days_2026.values()),
    "discounts": sum(v["discounts"] for v in days_2026.values()),
    "net_sales": sum(v["net_sales"] for v in days_2026.values()),
    "total_sales": sum(v["total_sales"] for v in days_2026.values()),
}
s26_17_totals["discount_rate"] = s26_17_totals["discounts"] / s26_17_totals["gross_sales"] * 100 if s26_17_totals["gross_sales"] else 0
s26_17_totals["avg_order_value"] = s26_17_totals["total_sales"] / s26_17_totals["orders"] if s26_17_totals["orders"] else 0

# --- UTM Channel breakdown 2026 ---
channels = {}
for r in utm_2026:
    # Normalize channel
    src = r["source"].lower()
    med = r["medium"].lower()
    if src in ("facebook", "fb") or (src == "(direct/none)" and med == "(none)" and False):
        if med in ("paid", "ads"):
            ch = "Facebook/Instagram Paid"
        elif med == "social" and src == "ig":
            ch = "Instagram Organic"
        else:
            ch = "Facebook Organic/Other"
    elif src == "ig":
        if med in ("ads",):
            ch = "Facebook/Instagram Paid"
        else:
            ch = "Instagram Organic"
    elif src == "google":
        if med == "cpc":
            ch = "Google Ads (CPC)"
        elif med == "product_sync":
            ch = "Google Shopping (Product Sync)"
        else:
            ch = "Google Organic/Other"
    elif src in ("klaviyo", "shopify_email"):
        ch = "Email (Klaviyo/Shopify)"
    elif src == "shop_app":
        ch = "Shop App"
    elif src == "chatgpt.com":
        ch = "ChatGPT Referral"
    elif src == "(direct/none)":
        ch = "Direct / Organic / Unattributed"
    else:
        ch = f"{src} / {med}"

    if ch not in channels:
        channels[ch] = {"orders": 0, "gross_sales": 0, "discounts": 0, "net_sales": 0, "total_sales": 0}
    channels[ch]["orders"] += r["orders"]
    channels[ch]["gross_sales"] += r["gross_sales"]
    channels[ch]["discounts"] += abs(r["discounts"])
    channels[ch]["net_sales"] += r["net_sales"]
    channels[ch]["total_sales"] += r["total_sales"]

# Sort channels by total_sales desc
channels_sorted = sorted(channels.items(), key=lambda x: x[1]["total_sales"], reverse=True)
total_ch_sales = sum(v["total_sales"] for _, v in channels_sorted)

# --- MER calculations ---
# 2025: user said FB spend = ~$153, Google = $7,757.60
fb_spend_2025 = 153.00
google_spend_2025 = 7757.60
total_spend_2025 = fb_spend_2025 + google_spend_2025
mer_2025_full = s25_full["total_sales"] / total_spend_2025

# 2026 March 1-17
mer_2026_17 = s26_17_shopify_total / s26_17_total_spent if s26_17_total_spent else 0

# --- Google Ads comparison ---
google_2025 = {
    "spend": 7757.60,
    "conversions": 199.24,
    "conv_value": 28105.68,
    "roas": 3.62,
    "clicks": 5934,
    "impressions": 587966,
    "campaigns": {
        "new ads 5 (Search)": {"spend": 98.80, "conv": 0, "value": 0, "roas": 0},
        "Harmony House Foods (Search)": {"spend": 912.02, "conv": 10.01, "value": 1352.92, "roas": 1.48},
        "Ad 4 (Search)": {"spend": 3083.21, "conv": 58.95, "value": 11611.15, "roas": 3.77},
        "Sale merchant ad 1 (Shopping)": {"spend": 3663.57, "conv": 130.28, "value": 15141.61, "roas": 4.13},
    }
}

google_2026 = {
    "spend": 3494.34,
    "conversions": 137.68,
    "conv_value": 17158.26,
    "roas": 4.91,
    "clicks": 6255,
    "impressions": 374935,
    "campaigns": {
        "INTC | Branded Search | Max Conv": {"spend": 528.42, "conv": 31, "value": 3621.40, "roas": 6.85},
        "INTC | P.Max | All Products": {"spend": 2774.63, "conv": 106.68, "value": 13536.86, "roas": 4.88},
        "INTC | NB | Search | Dried Cabbage": {"spend": 191.29, "conv": 0, "value": 0, "roas": 0},
    }
}

# --- Prorated March 2026 full month estimate ---
days_elapsed = 17
days_in_march = 31
prorate_factor = days_in_march / days_elapsed
s26_projected_full = s26_17_shopify_total * prorate_factor
s26_projected_spend = s26_17_total_spent * prorate_factor
s26_projected_mer = s26_projected_full / s26_projected_spend if s26_projected_spend else 0

# Target: 15% YoY growth
target_total = s25_full["total_sales"] * 1.15
gap_to_target = target_total - s26_projected_full
remaining_days = days_in_march - days_elapsed
daily_needed = (target_total - s26_17_shopify_total) / remaining_days if remaining_days > 0 else 0
avg_daily_so_far_2026 = s26_17_shopify_total / days_elapsed
avg_daily_2025 = s25_full["total_sales"] / days_in_march

# --- Day-by-day comparison ---
daily_comparison = []
for i in range(17):
    d25 = shopify_2025[i]
    ad26 = ad_march[i]
    daily_comparison.append({
        "day_num": i + 1,
        "date_2025": d25["day"],
        "date_2026": ad26["day"],
        "sales_2025": d25["total_sales"],
        "sales_2026": ad26["daily_shopify_sales"],
        "orders_2025": d25["orders"],
        "discounts_2025": abs(d25["discounts"]),
        "gross_2025": d25["gross_sales"],
    })

# --- Excluding March 12 outlier ---
s25_17_ex12 = {
    "orders": s25_17_totals["orders"] - shopify_2025[11]["orders"],  # index 11 = March 12
    "total_sales": s25_17_totals["total_sales"] - shopify_2025[11]["total_sales"],
    "gross_sales": s25_17_totals["gross_sales"] - shopify_2025[11]["gross_sales"],
    "discounts": s25_17_totals["discounts"] - abs(shopify_2025[11]["discounts"]),
}
s26_17_ex12 = s26_17_shopify_total - ad_march[11]["daily_shopify_sales"]  # March 12, 2026

# --- Week-by-week breakdown ---
week1_2025 = sum(shopify_2025[i]["total_sales"] for i in range(7))  # Mar 1-7
week2_2025 = sum(shopify_2025[i]["total_sales"] for i in range(7, 14))  # Mar 8-14
week3_partial_2025 = sum(shopify_2025[i]["total_sales"] for i in range(14, 17))  # Mar 15-17

week1_2026 = sum(ad_march[i]["daily_shopify_sales"] for i in range(7))
week2_2026 = sum(ad_march[i]["daily_shopify_sales"] for i in range(7, 14))
week3_partial_2026 = sum(ad_march[i]["daily_shopify_sales"] for i in range(14, 17))

# ── Generate HTML Report ─────────────────────────────────────────────────────
def fmt(val):
    return f"${val:,.2f}"

def pct(val):
    return f"{val:.1f}%"

def change_pct(new, old):
    if old == 0:
        return "N/A"
    ch = (new - old) / old * 100
    color = "green" if ch >= 0 else "red"
    arrow = "▲" if ch >= 0 else "▼"
    return f'<span style="color:{color};font-weight:bold">{arrow} {abs(ch):.1f}%</span>'

def change_pct_plain(new, old):
    if old == 0:
        return 0
    return (new - old) / old * 100

report_date = datetime.now().strftime("%B %d, %Y")

# Pre-compute values that have dict lookups to avoid f-string escaping issues
direct_channel = channels.get("Direct / Organic / Unattributed", {"total_sales": 0, "orders": 0})
direct_pct_of_total = direct_channel["total_sales"] / total_ch_sales * 100 if total_ch_sales else 0
email_channel = channels.get("Email (Klaviyo/Shopify)", {"total_sales": 0, "orders": 0})
email_orders = email_channel["orders"]
email_sales = email_channel["total_sales"]

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Harmony House Foods — March YoY Performance Analysis</title>
<style>
    :root {{
        --primary: #1a365d;
        --accent: #2b6cb0;
        --red: #c53030;
        --green: #276749;
        --orange: #c05621;
        --bg: #f7fafc;
        --card-bg: #ffffff;
        --border: #e2e8f0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: var(--bg);
        color: #2d3748;
        line-height: 1.6;
        padding: 20px;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{
        color: var(--primary);
        font-size: 1.8rem;
        margin-bottom: 4px;
    }}
    .subtitle {{
        color: #718096;
        font-size: 0.95rem;
        margin-bottom: 24px;
    }}
    h2 {{
        color: var(--primary);
        font-size: 1.3rem;
        margin: 28px 0 12px;
        padding-bottom: 6px;
        border-bottom: 2px solid var(--accent);
    }}
    h3 {{
        color: var(--accent);
        font-size: 1.1rem;
        margin: 16px 0 8px;
    }}
    .card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .alert {{
        border-left: 4px solid var(--red);
        background: #fff5f5;
        padding: 16px 20px;
        border-radius: 4px;
        margin: 12px 0;
    }}
    .alert-warning {{
        border-left-color: var(--orange);
        background: #fffaf0;
    }}
    .alert-success {{
        border-left-color: var(--green);
        background: #f0fff4;
    }}
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin: 16px 0;
    }}
    .kpi-box {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }}
    .kpi-box .label {{ font-size: 0.8rem; color: #718096; text-transform: uppercase; letter-spacing: 0.05em; }}
    .kpi-box .value {{ font-size: 1.6rem; font-weight: 700; color: var(--primary); margin: 4px 0; }}
    .kpi-box .change {{ font-size: 0.85rem; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 0.9rem;
    }}
    th {{
        background: var(--primary);
        color: white;
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
    }}
    td {{
        padding: 8px 12px;
        border-bottom: 1px solid var(--border);
    }}
    tr:nth-child(even) {{ background: #f7fafc; }}
    tr:hover {{ background: #edf2f7; }}
    .text-right {{ text-align: right; }}
    .highlight-row {{ background: #fffaf0 !important; font-weight: 600; }}
    .section-intro {{ color: #4a5568; margin-bottom: 12px; }}
    ul {{ margin: 8px 0 8px 20px; }}
    li {{ margin: 4px 0; }}
    .rec-box {{
        background: #ebf8ff;
        border: 1px solid #bee3f8;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 8px 0;
    }}
    .rec-box strong {{ color: var(--accent); }}
    .footer {{
        text-align: center;
        color: #a0aec0;
        font-size: 0.8rem;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
    }}
    @media print {{
        body {{ padding: 0; }}
        .card {{ box-shadow: none; break-inside: avoid; }}
    }}
</style>
</head>
<body>
<div class="container">

<h1>Harmony House Foods — March YoY Performance Analysis</h1>
<p class="subtitle">March 2025 vs. March 2026 (1–17) &nbsp;|&nbsp; Prepared {report_date}</p>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>1. Executive Summary</h2>

<div class="alert">
<strong>Key Finding:</strong> March 2026 total sales are tracking <strong>{pct(abs(change_pct_plain(s26_17_shopify_total, s25_17_totals['total_sales'])))}</strong> below the same period last year,
while ad spend has already exceeded last year's <em>full month</em> budget ({fmt(total_spend_2025)}) in just 17 days ({fmt(s26_17_total_spent)}).
MER has collapsed from <strong>{mer_2025_full:.1f}x</strong> to <strong>{mer_2026_17:.1f}x</strong>.
</div>

<div class="alert alert-warning">
<strong>Important Context:</strong> March 12, 2025 saw a massive spike — 89 orders and {fmt(shopify_2025[11]["total_sales"])} in a single day (likely a flash sale/promo).
Excluding that outlier, the true YoY gap (Mar 1–17) narrows from ~{pct(abs(change_pct_plain(s26_17_shopify_total, s25_17_totals['total_sales'])))} to ~{pct(abs(change_pct_plain(s26_17_ex12, s25_17_ex12['total_sales'])))}.
</div>

<div class="kpi-grid">
    <div class="kpi-box">
        <div class="label">Total Sales (Mar 1–17)</div>
        <div class="value">{fmt(s26_17_shopify_total)}</div>
        <div class="change">{change_pct(s26_17_shopify_total, s25_17_totals['total_sales'])} vs. {fmt(s25_17_totals['total_sales'])} (2025)</div>
    </div>
    <div class="kpi-box">
        <div class="label">Total Ad Spend (Mar 1–17)</div>
        <div class="value">{fmt(s26_17_total_spent)}</div>
        <div class="change">{change_pct(s26_17_total_spent, total_spend_2025)} vs. {fmt(total_spend_2025)} (2025 full month)</div>
    </div>
    <div class="kpi-box">
        <div class="label">MER (Revenue / Spend)</div>
        <div class="value">{mer_2026_17:.1f}x</div>
        <div class="change">{change_pct(mer_2026_17, mer_2025_full)} vs. {mer_2025_full:.1f}x (2025)</div>
    </div>
    <div class="kpi-box">
        <div class="label">Blended ROAS (Platform)</div>
        <div class="value">{s26_17_total_conv / s26_17_total_spent:.2f}x</div>
        <div class="change">Google: {google_2026['roas']:.1f}x &nbsp;|&nbsp; FB: {s26_17_fb_conv / s26_17_fb_spent:.2f}x</div>
    </div>
</div>

<div class="kpi-grid">
    <div class="kpi-box">
        <div class="label">Projected Full March 2026</div>
        <div class="value">{fmt(s26_projected_full)}</div>
        <div class="change">{change_pct(s26_projected_full, s25_full['total_sales'])} vs. {fmt(s25_full['total_sales'])} (2025 actual)</div>
    </div>
    <div class="kpi-box">
        <div class="label">15% Growth Target</div>
        <div class="value">{fmt(target_total)}</div>
        <div class="change">Gap: <span style="color:red;font-weight:bold">{fmt(target_total - s26_projected_full)}</span> short</div>
    </div>
    <div class="kpi-box">
        <div class="label">Daily Sales Needed (Rest of Month)</div>
        <div class="value">{fmt(daily_needed)}</div>
        <div class="change">Current avg: {fmt(avg_daily_so_far_2026)}/day &nbsp;|&nbsp; 2025 avg: {fmt(avg_daily_2025)}/day</div>
    </div>
    <div class="kpi-box">
        <div class="label">Projected Full Month Ad Spend</div>
        <div class="value">{fmt(s26_projected_spend)}</div>
        <div class="change">{change_pct(s26_projected_spend, total_spend_2025)} vs. {fmt(total_spend_2025)} (2025)</div>
    </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>2. Day-by-Day Comparison (March 1–17)</h2>

<div class="card">
<table>
<tr>
    <th>Day</th>
    <th class="text-right">2025 Total Sales</th>
    <th class="text-right">2025 Orders</th>
    <th class="text-right">2025 Discounts</th>
    <th class="text-right">2026 Total Sales</th>
    <th class="text-right">YoY Change</th>
</tr>
"""

for dc in daily_comparison:
    row_class = ' class="highlight-row"' if dc["day_num"] == 12 else ""
    html += f"""<tr{row_class}>
    <td>Mar {dc['day_num']}</td>
    <td class="text-right">{fmt(dc['sales_2025'])}</td>
    <td class="text-right">{dc['orders_2025']}</td>
    <td class="text-right">{fmt(dc['discounts_2025'])}</td>
    <td class="text-right">{fmt(dc['sales_2026'])}</td>
    <td class="text-right">{change_pct(dc['sales_2026'], dc['sales_2025'])}</td>
</tr>
"""

html += f"""<tr style="font-weight:bold;background:#edf2f7">
    <td>Total (1–17)</td>
    <td class="text-right">{fmt(s25_17_totals['total_sales'])}</td>
    <td class="text-right">{s25_17_totals['orders']}</td>
    <td class="text-right">{fmt(s25_17_totals['discounts'])}</td>
    <td class="text-right">{fmt(s26_17_shopify_total)}</td>
    <td class="text-right">{change_pct(s26_17_shopify_total, s25_17_totals['total_sales'])}</td>
</tr>
<tr style="font-weight:bold;background:#fffaf0">
    <td>Total (excl. Mar 12 outlier)</td>
    <td class="text-right">{fmt(s25_17_ex12['total_sales'])}</td>
    <td class="text-right">{s25_17_ex12['orders']}</td>
    <td class="text-right">{fmt(s25_17_ex12['discounts'])}</td>
    <td class="text-right">{fmt(s26_17_ex12)}</td>
    <td class="text-right">{change_pct(s26_17_ex12, s25_17_ex12['total_sales'])}</td>
</tr>
</table>
</div>

<div class="card">
<h3>Weekly Trend</h3>
<table>
<tr>
    <th>Period</th>
    <th class="text-right">2025 Sales</th>
    <th class="text-right">2026 Sales</th>
    <th class="text-right">YoY Change</th>
</tr>
<tr>
    <td>Week 1 (Mar 1–7)</td>
    <td class="text-right">{fmt(week1_2025)}</td>
    <td class="text-right">{fmt(week1_2026)}</td>
    <td class="text-right">{change_pct(week1_2026, week1_2025)}</td>
</tr>
<tr>
    <td>Week 2 (Mar 8–14)</td>
    <td class="text-right">{fmt(week2_2025)}</td>
    <td class="text-right">{fmt(week2_2026)}</td>
    <td class="text-right">{change_pct(week2_2026, week2_2025)}</td>
</tr>
<tr>
    <td>Mar 15–17</td>
    <td class="text-right">{fmt(week3_partial_2025)}</td>
    <td class="text-right">{fmt(week3_partial_2026)}</td>
    <td class="text-right">{change_pct(week3_partial_2026, week3_partial_2025)}</td>
</tr>
</table>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>3. Discount Analysis</h2>

<div class="card">
<table>
<tr>
    <th>Metric</th>
    <th class="text-right">March 2025 (1–17)</th>
    <th class="text-right">March 2026 (1–17)</th>
    <th class="text-right">Change</th>
</tr>
<tr>
    <td>Gross Sales</td>
    <td class="text-right">{fmt(s25_17_totals['gross_sales'])}</td>
    <td class="text-right">{fmt(s26_17_totals['gross_sales'])}</td>
    <td class="text-right">{change_pct(s26_17_totals['gross_sales'], s25_17_totals['gross_sales'])}</td>
</tr>
<tr>
    <td>Total Discounts</td>
    <td class="text-right">{fmt(s25_17_totals['discounts'])}</td>
    <td class="text-right">{fmt(s26_17_totals['discounts'])}</td>
    <td class="text-right">{change_pct(s26_17_totals['discounts'], s25_17_totals['discounts'])}</td>
</tr>
<tr>
    <td>Discount Rate (% of Gross)</td>
    <td class="text-right">{pct(s25_17_totals['discount_rate'])}</td>
    <td class="text-right">{pct(s26_17_totals['discount_rate'])}</td>
    <td class="text-right">{"<span style='color:green'>Lower</span>" if s26_17_totals['discount_rate'] < s25_17_totals['discount_rate'] else "<span style='color:red'>Higher</span>"}</td>
</tr>
<tr>
    <td>Net Sales</td>
    <td class="text-right">{fmt(s25_17_totals['net_sales'])}</td>
    <td class="text-right">{fmt(s26_17_totals['net_sales'])}</td>
    <td class="text-right">{change_pct(s26_17_totals['net_sales'], s25_17_totals['net_sales'])}</td>
</tr>
<tr>
    <td>Avg Order Value (Total Sales / Orders)</td>
    <td class="text-right">{fmt(s25_17_totals['avg_order_value'])}</td>
    <td class="text-right">{fmt(s26_17_totals['avg_order_value'])}</td>
    <td class="text-right">{change_pct(s26_17_totals['avg_order_value'], s25_17_totals['avg_order_value'])}</td>
</tr>
</table>
</div>

<div class="alert alert-warning">
<strong>March 12, 2025 Promo Impact:</strong> That single day contributed {fmt(abs(shopify_2025[11]['discounts']))} in discounts
({pct(abs(shopify_2025[11]['discounts']) / s25_17_totals['discounts'] * 100)} of all discounts in the first 17 days)
and {fmt(shopify_2025[11]['gross_sales'])} in gross sales ({shopify_2025[11]['orders']} orders).
This was clearly a major promotional event that has <strong>no equivalent in March 2026</strong>.
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>4. Ad Spend & Efficiency Deep Dive</h2>

<div class="card">
<h3>Ad Spend Comparison</h3>
<table>
<tr>
    <th>Metric</th>
    <th class="text-right">March 2025 (Full Month)</th>
    <th class="text-right">March 2026 (1–17 only)</th>
    <th class="text-right">Change</th>
</tr>
<tr>
    <td>Google Ads Spend</td>
    <td class="text-right">{fmt(google_spend_2025)}</td>
    <td class="text-right">{fmt(s26_17_google_spent)}</td>
    <td class="text-right">{pct(s26_17_google_spent / google_spend_2025 * 100)} of 2025 total</td>
</tr>
<tr>
    <td>Facebook Ads Spend</td>
    <td class="text-right">{fmt(fb_spend_2025)}</td>
    <td class="text-right">{fmt(s26_17_fb_spent)}</td>
    <td class="text-right">{change_pct(s26_17_fb_spent, fb_spend_2025)}</td>
</tr>
<tr>
    <td>Total Ad Spend</td>
    <td class="text-right">{fmt(total_spend_2025)}</td>
    <td class="text-right">{fmt(s26_17_total_spent)}</td>
    <td class="text-right">{change_pct(s26_17_total_spent, total_spend_2025)}</td>
</tr>
<tr>
    <td>Shopify Total Sales</td>
    <td class="text-right">{fmt(s25_full['total_sales'])} (full)</td>
    <td class="text-right">{fmt(s26_17_shopify_total)} (17 days)</td>
    <td class="text-right">—</td>
</tr>
<tr>
    <td>MER (Total Sales / Total Ad Spend)</td>
    <td class="text-right">{mer_2025_full:.1f}x</td>
    <td class="text-right">{mer_2026_17:.1f}x</td>
    <td class="text-right">{change_pct(mer_2026_17, mer_2025_full)}</td>
</tr>
</table>
</div>

<div class="card">
<h3>Google Ads — Campaign Performance</h3>

<h3 style="font-size:0.95rem;color:#718096">March 2025 (Full Month)</h3>
<table>
<tr><th>Campaign</th><th class="text-right">Spend</th><th class="text-right">Conv.</th><th class="text-right">Conv. Value</th><th class="text-right">ROAS</th><th class="text-right">CPA</th></tr>
"""

for name, data in google_2025["campaigns"].items():
    cpa = f"${data['spend']/data['conv']:.2f}" if data["conv"] > 0 else "—"
    html += f"""<tr>
    <td>{name}</td>
    <td class="text-right">{fmt(data['spend'])}</td>
    <td class="text-right">{data['conv']:.1f}</td>
    <td class="text-right">{fmt(data['value'])}</td>
    <td class="text-right">{data['roas']:.2f}x</td>
    <td class="text-right">{cpa}</td>
</tr>
"""

html += f"""<tr style="font-weight:bold;background:#edf2f7">
    <td>Total</td>
    <td class="text-right">{fmt(google_2025['spend'])}</td>
    <td class="text-right">{google_2025['conversions']:.1f}</td>
    <td class="text-right">{fmt(google_2025['conv_value'])}</td>
    <td class="text-right">{google_2025['roas']:.2f}x</td>
    <td class="text-right">${google_2025['spend']/google_2025['conversions']:.2f}</td>
</tr>
</table>

<h3 style="font-size:0.95rem;color:#718096;margin-top:16px">March 2026 (1–17)</h3>
<table>
<tr><th>Campaign</th><th class="text-right">Spend</th><th class="text-right">Conv.</th><th class="text-right">Conv. Value</th><th class="text-right">ROAS</th><th class="text-right">CPA</th></tr>
"""

for name, data in google_2026["campaigns"].items():
    cpa = f"${data['spend']/data['conv']:.2f}" if data["conv"] > 0 else "—"
    html += f"""<tr>
    <td>{name}</td>
    <td class="text-right">{fmt(data['spend'])}</td>
    <td class="text-right">{data['conv']:.1f}</td>
    <td class="text-right">{fmt(data['value'])}</td>
    <td class="text-right">{data['roas']:.2f}x</td>
    <td class="text-right">{cpa}</td>
</tr>
"""

html += f"""<tr style="font-weight:bold;background:#edf2f7">
    <td>Total</td>
    <td class="text-right">{fmt(google_2026['spend'])}</td>
    <td class="text-right">{google_2026['conversions']:.1f}</td>
    <td class="text-right">{fmt(google_2026['conv_value'])}</td>
    <td class="text-right">{google_2026['roas']:.2f}x</td>
    <td class="text-right">${google_2026['spend']/google_2026['conversions']:.2f}</td>
</tr>
</table>
</div>

<div class="alert alert-success">
<strong>Google Ads Positive:</strong> ROAS improved from 3.62x (2025) to 4.91x (2026). The INTC | P.Max campaign is performing well at 4.88x ROAS
but is <strong>budget-limited</strong> ($190/day). Branded Search is highly efficient at 6.85x ROAS. The NB Dried Cabbage campaign ($191.29 spent, 0 conversions) was correctly paused.
</div>

<div class="card">
<h3>Facebook Ads Performance (March 2026)</h3>
<table>
<tr>
    <th>Metric</th>
    <th class="text-right">Value</th>
</tr>
<tr><td>Total FB Spend (Mar 1–17)</td><td class="text-right">{fmt(s26_17_fb_spent)}</td></tr>
<tr><td>FB Platform Conversion Value</td><td class="text-right">{fmt(s26_17_fb_conv)}</td></tr>
<tr><td>FB Platform ROAS</td><td class="text-right">{s26_17_fb_conv / s26_17_fb_spent:.2f}x</td></tr>
<tr><td>Daily Average FB Spend</td><td class="text-right">{fmt(s26_17_fb_spent / 17)}</td></tr>
</table>
"""

# Calculate UTM-attributed FB sales
fb_utm_orders = sum(r["orders"] for r in utm_2026 if r["source"].lower() in ("facebook", "fb", "ig") and r["medium"].lower() in ("paid", "ads", "social"))
fb_utm_sales = sum(r["total_sales"] for r in utm_2026 if r["source"].lower() in ("facebook", "fb", "ig") and r["medium"].lower() in ("paid", "ads", "social"))
fb_utm_gross = sum(r["gross_sales"] for r in utm_2026 if r["source"].lower() in ("facebook", "fb", "ig") and r["medium"].lower() in ("paid", "ads", "social"))

html += f"""
<h3 style="margin-top:12px">Facebook — UTM Last-Click Attribution vs Platform</h3>
<table>
<tr>
    <th>Attribution</th>
    <th class="text-right">Orders</th>
    <th class="text-right">Gross Sales</th>
    <th class="text-right">Total Sales</th>
    <th class="text-right">Effective ROAS</th>
</tr>
<tr>
    <td>FB Platform Reported</td>
    <td class="text-right">—</td>
    <td class="text-right">—</td>
    <td class="text-right">{fmt(s26_17_fb_conv)}</td>
    <td class="text-right">{s26_17_fb_conv / s26_17_fb_spent:.2f}x</td>
</tr>
<tr>
    <td>Shopify UTM Last-Click (facebook/fb/ig paid)</td>
    <td class="text-right">{fb_utm_orders}</td>
    <td class="text-right">{fmt(fb_utm_gross)}</td>
    <td class="text-right">{fmt(fb_utm_sales)}</td>
    <td class="text-right">{fb_utm_sales / s26_17_fb_spent:.2f}x</td>
</tr>
</table>
</div>

<div class="alert">
<strong>Facebook Concern:</strong> FB is consuming <strong>{pct(s26_17_fb_spent / s26_17_total_spent * 100)}</strong> of total ad spend
({fmt(s26_17_fb_spent)} of {fmt(s26_17_total_spent)}) but Shopify UTM last-click attributes only
{fmt(fb_utm_sales)} in sales — an effective ROAS of just <strong>{fb_utm_sales / s26_17_fb_spent:.2f}x</strong>.
Even FB's self-reported conversion value ({fmt(s26_17_fb_conv)}) only yields {s26_17_fb_conv / s26_17_fb_spent:.2f}x ROAS.
Compared to 2025 when FB spend was only ${fb_spend_2025:.0f} for the entire month, this represents a massive and potentially inefficient increase.
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>5. Channel Attribution Breakdown (March 2026, UTM Last-Click)</h2>

<div class="card">
<table>
<tr>
    <th>Channel</th>
    <th class="text-right">Orders</th>
    <th class="text-right">Gross Sales</th>
    <th class="text-right">Discounts</th>
    <th class="text-right">Total Sales</th>
    <th class="text-right">% of Total Sales</th>
</tr>
"""

total_ch_sales = sum(v["total_sales"] for _, v in channels_sorted)
for ch_name, ch_data in channels_sorted:
    pct_of_total = ch_data["total_sales"] / total_ch_sales * 100 if total_ch_sales else 0
    html += f"""<tr>
    <td>{ch_name}</td>
    <td class="text-right">{ch_data['orders']}</td>
    <td class="text-right">{fmt(ch_data['gross_sales'])}</td>
    <td class="text-right">{fmt(ch_data['discounts'])}</td>
    <td class="text-right">{fmt(ch_data['total_sales'])}</td>
    <td class="text-right">{pct(pct_of_total)}</td>
</tr>
"""

html += f"""<tr style="font-weight:bold;background:#edf2f7">
    <td>Total</td>
    <td class="text-right">{s26_17_totals['orders']}</td>
    <td class="text-right">{fmt(s26_17_totals['gross_sales'])}</td>
    <td class="text-right">{fmt(s26_17_totals['discounts'])}</td>
    <td class="text-right">{fmt(total_ch_sales)}</td>
    <td class="text-right">100%</td>
</tr>
</table>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>6. Google Ads — Channel Type Comparison (2025 vs 2026)</h2>

<div class="card">
<table>
<tr>
    <th>Channel Type</th>
    <th class="text-right">2025 Spend</th>
    <th class="text-right">2025 ROAS</th>
    <th class="text-right">2026 Spend</th>
    <th class="text-right">2026 ROAS</th>
    <th>Notes</th>
</tr>
<tr>
    <td>Search (Branded + Non-Branded)</td>
    <td class="text-right">{fmt(98.80 + 912.02 + 3083.21)}</td>
    <td class="text-right">{(0 + 1352.92 + 11611.15) / (98.80 + 912.02 + 3083.21):.2f}x</td>
    <td class="text-right">{fmt(528.42 + 191.29)}</td>
    <td class="text-right">{3621.40 / (528.42 + 191.29):.2f}x</td>
    <td>Branded search very efficient; NB Cabbage paused (good)</td>
</tr>
<tr>
    <td>Shopping / Performance Max</td>
    <td class="text-right">{fmt(3663.57)}</td>
    <td class="text-right">4.13x</td>
    <td class="text-right">{fmt(2774.63)}</td>
    <td class="text-right">4.88x</td>
    <td>PMax outperforming old Shopping; budget-limited</td>
</tr>
</table>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>7. What's Driving the Gap?</h2>

<div class="card">
<h3>Root Causes</h3>
<ol style="margin:8px 0 8px 20px">
<li><strong>Missing Promotional Event:</strong> March 12, 2025's flash sale/promo generated {fmt(shopify_2025[11]['total_sales'])} (89 orders, {fmt(abs(shopify_2025[11]['discounts']))} in discounts).
No equivalent event has occurred in 2026. This single day accounts for ~{pct(shopify_2025[11]['total_sales'] / s25_17_totals['total_sales'] * 100)} of March 1–17 2025 sales.</li>

<li><strong>Organic/Direct Traffic Decline:</strong> The "Direct / Organic / Unattributed" channel drives {pct(direct_pct_of_total)}
of 2026 sales. Without 2025 UTM data for comparison, we can't measure the exact decline, but the overall business is trending down YoY even outside of paid channels.</li>

<li><strong>Facebook Spend Scaling Too Aggressively:</strong> FB spend went from $153/month to ~${s26_17_fb_spent/17*31:,.0f}/month (projected).
The incremental revenue is not keeping pace — the marginal ROAS on FB is poor.</li>

<li><strong>Lower Discount Aggressiveness in 2026:</strong>
2025 (Mar 1–17) discount rate: <strong>{pct(s25_17_totals['discount_rate'])}</strong> |
2026 (Mar 1–17) discount rate: <strong>{pct(s26_17_totals['discount_rate'])}</strong>.
{"Lower discounts = better margins but fewer orders." if s26_17_totals['discount_rate'] < s25_17_totals['discount_rate'] else "Discounts are similar."}</li>

<li><strong>Underlying Business Trend:</strong> Annual revenue has declined every year since 2021 ($1.81M → $1.02M in 2025, per annual data).
This is a structural headwind — paid media alone cannot reverse a 44% organic decline.</li>
</ol>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>8. Recommendations for the Client Call</h2>

<div class="rec-box">
<strong>1. Run a Flash Sale / Promotion ASAP (March 19–22)</strong><br>
Last year's March 12 promo generated $13,252 in a single day with 89 orders. A similar event could close much of the gap.
Recommend a 48–72 hour flash sale (20–25% off popular items) promoted via email + social.
This alone could add $8,000–15,000 in incremental revenue.
</div>

<div class="rec-box">
<strong>2. Scale Down Facebook Ads Immediately</strong><br>
Cut FB daily budget from ~${s26_17_fb_spent/17:,.0f}/day to $100–150/day (retargeting only).
FB is burning ${s26_17_fb_spent/17:,.0f}/day with UTM-attributed ROAS of only {fb_utm_sales / s26_17_fb_spent:.2f}x.
Reallocate savings to Google PMax and email campaigns. Potential savings: ~$2,500–3,000 for the rest of March.
</div>

<div class="rec-box">
<strong>3. Increase Google PMax Budget</strong><br>
The PMax campaign has 4.88x ROAS and is <strong>budget-limited</strong> at $190/day.
Increase to $250–300/day. This is the highest-efficiency paid channel.
The branded search campaign is already efficient at 6.85x ROAS — keep as-is.
</div>

<div class="rec-box">
<strong>4. Double Down on Email (Klaviyo)</strong><br>
Email is attributing {email_orders} orders / {fmt(email_sales)}
in total sales with <strong>zero ad cost</strong> (infinite ROI).
Send 2–3 additional campaigns this week: flash sale announcement, abandoned cart push, and a "best sellers" feature.
Each email blast can drive $500–2,000 in incremental sales.
</div>

<div class="rec-box">
<strong>5. Set Realistic Expectations on the 15% Target</strong><br>
The 15% YoY growth target ({fmt(target_total)}) requires {fmt(daily_needed)}/day for the remaining {remaining_days} days —
that's <strong>{daily_needed / avg_daily_so_far_2026:.1f}x</strong> the current daily average.
This is only achievable with a major promotional event.
A more realistic target given current trends: match or come within 10–15% of last year's {fmt(s25_full['total_sales'])}.
</div>

<div class="rec-box">
<strong>6. Reframe the Narrative for the Client</strong><br>
Key talking points:
<ul>
<li>Last year's March was inflated by a massive single-day promo ({fmt(shopify_2025[11]['total_sales'])} on Mar 12). Excluding that, the real gap is ~{pct(abs(change_pct_plain(s26_17_ex12, s25_17_ex12['total_sales'])))} not ~{pct(abs(change_pct_plain(s26_17_shopify_total, s25_17_totals['total_sales'])))}.</li>
<li>Google Ads efficiency has <strong>improved</strong> — ROAS up from 3.62x to 4.91x. We're spending smarter.</li>
<li>We've identified FB as the budget drain and are course-correcting now.</li>
<li>Immediate action plan: flash sale + email push + FB budget reallocation can recover $10,000–20,000 before month-end.</li>
<li>The business has a structural organic decline (revenue down 44% since 2021). Paid media optimizes within that reality — we need to also discuss SEO, retention, and product strategy.</li>
</ul>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>9. Projected Scenarios for Rest of March</h2>

<div class="card">
<table>
<tr>
    <th>Scenario</th>
    <th class="text-right">Remaining Spend</th>
    <th class="text-right">Projected Month Total</th>
    <th class="text-right">vs. 2025</th>
    <th class="text-right">vs. Target</th>
</tr>
<tr>
    <td><strong>A: Status Quo</strong> (no changes)</td>
    <td class="text-right">{fmt(avg_daily_so_far_2026 / mer_2026_17 * remaining_days)}</td>
    <td class="text-right">{fmt(s26_projected_full)}</td>
    <td class="text-right">{change_pct(s26_projected_full, s25_full['total_sales'])}</td>
    <td class="text-right">{change_pct(s26_projected_full, target_total)}</td>
</tr>
"""

# Scenario B: Optimize (cut FB, scale Google, send emails)
# Assume: save $150/day on FB, add $100/day to Google, emails add $1000/day incremental
scenario_b_daily = avg_daily_so_far_2026 * 1.15  # 15% lift from optimization
scenario_b_total = s26_17_shopify_total + scenario_b_daily * remaining_days
scenario_b_spend = s26_17_total_spent + (s26_17_total_spent / 17 * 0.75) * remaining_days  # 25% lower daily spend

# Scenario C: Optimize + Flash Sale
flash_sale_boost = 12000  # Conservative estimate
scenario_c_total = scenario_b_total + flash_sale_boost
scenario_c_spend = scenario_b_spend + 500  # Extra ad spend for promo

html += f"""<tr>
    <td><strong>B: Optimize Spend</strong> (cut FB, scale PMax, more emails)</td>
    <td class="text-right">{fmt(scenario_b_spend - s26_17_total_spent)}</td>
    <td class="text-right">{fmt(scenario_b_total)}</td>
    <td class="text-right">{change_pct(scenario_b_total, s25_full['total_sales'])}</td>
    <td class="text-right">{change_pct(scenario_b_total, target_total)}</td>
</tr>
<tr>
    <td><strong>C: Optimize + Flash Sale</strong></td>
    <td class="text-right">{fmt(scenario_c_spend - s26_17_total_spent)}</td>
    <td class="text-right">{fmt(scenario_c_total)}</td>
    <td class="text-right">{change_pct(scenario_c_total, s25_full['total_sales'])}</td>
    <td class="text-right">{change_pct(scenario_c_total, target_total)}</td>
</tr>
</table>
</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<h2>10. Immediate Action Items</h2>

<div class="card">
<table>
<tr><th>#</th><th>Action</th><th>Timeline</th><th>Expected Impact</th></tr>
<tr><td>1</td><td>Cut Facebook daily budget to $100–150 (retargeting only)</td><td>Today</td><td>Save ~$150–200/day; redirect to higher-ROI channels</td></tr>
<tr><td>2</td><td>Increase PMax budget from $190 → $250–300/day</td><td>Today</td><td>Capture more high-intent Shopping traffic at 4.88x ROAS</td></tr>
<tr><td>3</td><td>Plan and launch a flash sale (20–25% off, 48–72hr)</td><td>March 19–22</td><td>+$8,000–15,000 in sales (based on 2025 promo precedent)</td></tr>
<tr><td>4</td><td>Send 2–3 Klaviyo email blasts this week</td><td>This week</td><td>+$1,500–4,000 at zero ad cost</td></tr>
<tr><td>5</td><td>Pause or significantly reduce NB Search experiments</td><td>Today</td><td>Avoid wasting budget on 0-conversion campaigns</td></tr>
<tr><td>6</td><td>Monitor daily MER — target 7x+ for remaining days</td><td>Ongoing</td><td>Ensure spend efficiency improves vs. current 6.1x</td></tr>
</table>
</div>

<div class="footer">
Harmony House Foods — March YoY Performance Analysis &nbsp;|&nbsp; Generated {report_date}<br>
Data sources: Shopify, Google Ads, Facebook Ads, UTM tracking
</div>

</div>
</body>
</html>
"""

# Write report
report_dir = os.path.join(os.path.dirname(BASE), "..", "..", "reports", "Harmony House Foods")
os.makedirs(report_dir, exist_ok=True)
report_path = os.path.join(report_dir, f"March_YoY_Analysis_{datetime.now().strftime('%Y-%m-%d')}.html")
with open(report_path, "w") as f:
    f.write(html)

print(f"Report generated: {report_path}")
print(f"\n{'='*60}")
print(f"QUICK STATS SUMMARY")
print(f"{'='*60}")
print(f"March 2025 (1-17) Total Sales:    {fmt(s25_17_totals['total_sales'])}")
print(f"March 2026 (1-17) Total Sales:    {fmt(s26_17_shopify_total)}")
print(f"YoY Change:                       {change_pct_plain(s26_17_shopify_total, s25_17_totals['total_sales']):.1f}%")
print(f"")
print(f"Excl. Mar 12 outlier:")
print(f"  2025 (1-17 ex-12):              {fmt(s25_17_ex12['total_sales'])}")
print(f"  2026 (1-17 ex-12):              {fmt(s26_17_ex12)}")
print(f"  Adjusted YoY Change:            {change_pct_plain(s26_17_ex12, s25_17_ex12['total_sales']):.1f}%")
print(f"")
print(f"March 2025 Full Month Sales:      {fmt(s25_full['total_sales'])}")
print(f"March 2026 Projected Full Month:  {fmt(s26_projected_full)}")
print(f"15% Growth Target:                {fmt(target_total)}")
print(f"")
print(f"Ad Spend 2025 (full month):       {fmt(total_spend_2025)}")
print(f"Ad Spend 2026 (17 days):          {fmt(s26_17_total_spent)}")
print(f"  - Facebook:                     {fmt(s26_17_fb_spent)}")
print(f"  - Google:                       {fmt(s26_17_google_spent)}")
print(f"")
print(f"MER 2025:                         {mer_2025_full:.1f}x")
print(f"MER 2026 (Mar 1-17):              {mer_2026_17:.1f}x")
print(f"")
print(f"Google ROAS 2025:                 {google_2025['roas']:.2f}x")
print(f"Google ROAS 2026:                 {google_2026['roas']:.2f}x")
print(f"FB Platform ROAS 2026:            {s26_17_fb_conv / s26_17_fb_spent:.2f}x")
print(f"FB UTM Last-Click ROAS 2026:      {fb_utm_sales / s26_17_fb_spent:.2f}x")
print(f"")
print(f"Discount Rate 2025 (1-17):        {pct(s25_17_totals['discount_rate'])}")
print(f"Discount Rate 2026 (1-17):        {pct(s26_17_totals['discount_rate'])}")
print(f"")
print(f"UTM-Attributed FB Orders:         {fb_utm_orders}")
print(f"UTM-Attributed FB Sales:          {fmt(fb_utm_sales)}")
print(f"Email (Klaviyo) Orders:           {channels.get('Email (Klaviyo/Shopify)', {}).get('orders', 0)}")
print(f"Email (Klaviyo) Sales:            {fmt(channels.get('Email (Klaviyo/Shopify)', {}).get('total_sales', 0))}")
