#!/usr/bin/env python3
"""
LogOX Performance Dashboard Generator
Processes Shopify sales + Facebook ad CSVs across 3 periods and
generates an interactive dark-themed HTML report with insights.
"""

import csv
import json
import os
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "data", "LogOX")
OUT_DIR   = os.path.join(BASE_DIR, "reports", "LogOX")
OUT_FILE  = os.path.join(OUT_DIR, f"LogOX_{datetime.today().strftime('%Y-%m-%d')}.html")
ROAS_TARGET = 3.0

PERIODS = {
    "Mar 2025": {"sales": "sales_mar2025.csv", "fb": "fb_mar2025.csv", "label": "Mar 1–10, 2025"},
    "Feb 2026": {"sales": "sales_feb2026.csv", "fb": "fb_feb2026.csv", "label": "Feb 1–10, 2026"},
    "Mar 2026": {"sales": "sales_mar2026.csv", "fb": "fb_mar2026.csv", "label": "Mar 1–10, 2026"},
}
PERIOD_KEYS = list(PERIODS.keys())

SKIP_NAMES = {
    "LogOX Can Cooler", "LogOX Can Coolers (4 pack)", "Team LogOX Sticker",
    "Team LogOX Hat", "Team LogOX Handmade Mugs", "LogOX Made in USA Sticker",
    "LogOX Hat", "Free Unlimited Return Valid in US.", "LogOX Cant Handle Extension",
}

# ── URL → Product ──────────────────────────────────────────────────────────────

def url_to_product(url: str) -> str:
    u = url.strip().lower()
    if "logox-3-in-1" in u or "multitool" in u:
        return "LogOX 3-in-1 MultiTool"
    if "forester-package" in u:
        return "LogOX Forester Package"
    if "woodox-sling" in u:
        return "WoodOX Sling"
    if "timberox-ddl" in u:
        return "TimberOX Dan-D-Lift"
    if "/products/timberox" in u:
        return "TimberOX Summit 30-Ton"
    if "logox-carrying-tool" in u:
        return "LogOX Hauler"
    if "carryox-gear-bag" in u:
        return "CarryOX Gear Bag"
    if "fireside-bundle" in u:
        return "Fireside Bundle"
    if "logox-firewood-hearth-bin" in u:
        return "Hearth Bin"
    if "the-woodsman" in u:
        return "The Woodsman Bundle"
    if "amazon.ca" in u:
        return "Amazon (CA)"
    if "best-sellers" in u:
        return "General / DPA"
    stripped = u.rstrip("/").split("?")[0]
    if stripped in ("https://www.thelogox.com", "http://www.thelogox.com"):
        return "General / DPA"
    return "Other"


# ── Shopify product normalization ──────────────────────────────────────────────

def normalize_shopify(name: str) -> str:
    name = name.strip().rstrip("*").strip()
    if "LogOX 3-in-1 Forestry MultiTool" in name:
        return "LogOX 3-in-1 MultiTool"
    if "TimberOX Summit Dan-D-Lift" in name or "TimberOX Dan-D-Lift" in name:
        return "TimberOX Dan-D-Lift"
    if "LogOX Forester Package" in name:
        return "LogOX Forester Package"
    if "WoodOX Sling" in name:
        return "WoodOX Sling"
    if "TimberOX Summit 30-Ton" in name:
        return "TimberOX Summit 30-Ton"
    if name.startswith("LogOX Hauler") and "Upgrade" not in name and "Holster" not in name:
        return "LogOX Hauler"
    if "CarryOX Gear Bag" in name:
        return "CarryOX Gear Bag"
    if "PickOX Pickaroon" in name:
        return "PickOX Pickaroon"
    if "The Woodsman Bundle" in name or name == "The Woodsman":
        return "The Woodsman Bundle"
    if "Fireside Bundle" in name:
        return "Fireside Bundle"
    return name


# ── CSV loaders ───────────────────────────────────────────────────────────────

def load_sales(path: str) -> dict:
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            raw = row.get("Product title", "").strip()
            if not raw:
                continue
            try:
                net = float(row.get("Net sales", 0) or 0)
            except ValueError:
                net = 0
            if net <= 0:
                continue
            name = normalize_shopify(raw)
            if name in SKIP_NAMES:
                continue
            totals[name] = totals.get(name, 0.0) + net
    return totals


def load_fb(path: str) -> dict:
    """Aggregated FB data by product."""
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url  = row.get("Link (ad settings)", "").strip()
            prod = url_to_product(url)
            try:
                spend = float(row.get("Amount spent (USD)", 0) or 0)
            except ValueError:
                spend = 0
            try:
                conv  = float(row.get("Purchases conversion value", 0) or 0)
            except ValueError:
                conv = 0
            try:
                purch = int(float(row.get("Purchases", 0) or 0))
            except ValueError:
                purch = 0
            if spend <= 0:
                continue
            if prod not in totals:
                totals[prod] = {"spend": 0.0, "conv": 0.0, "purchases": 0}
            totals[prod]["spend"]     += spend
            totals[prod]["conv"]      += conv
            totals[prod]["purchases"] += purch
    return totals


def load_fb_ads(path: str, period_label: str) -> list:
    """Individual ad rows for creative-level analysis."""
    ads = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url  = row.get("Link (ad settings)", "").strip()
            name = row.get("Ad name", "").strip()
            try:
                spend = float(row.get("Amount spent (USD)", 0) or 0)
            except ValueError:
                spend = 0
            try:
                conv  = float(row.get("Purchases conversion value", 0) or 0)
            except ValueError:
                conv = 0
            try:
                purch = int(float(row.get("Purchases", 0) or 0))
            except ValueError:
                purch = 0
            if spend <= 0:
                continue
            roas = conv / spend if spend > 0 else 0
            ads.append({
                "name":     name,
                "product":  url_to_product(url),
                "spend":    spend,
                "conv":     conv,
                "purchases": purch,
                "roas":     roas,
                "period":   period_label,
            })
    return ads


# ── Data computation ───────────────────────────────────────────────────────────

def compute():
    sales_raw = {p: load_sales(os.path.join(DATA_DIR, cfg["sales"])) for p, cfg in PERIODS.items()}
    fb_raw    = {p: load_fb   (os.path.join(DATA_DIR, cfg["fb"   ])) for p, cfg in PERIODS.items()}
    ads_raw   = {p: load_fb_ads(os.path.join(DATA_DIR, cfg["fb"]), p) for p, cfg in PERIODS.items()}

    # ── Period summaries
    summaries = {}
    for p in PERIOD_KEYS:
        ts  = sum(sales_raw[p].values())
        tsp = sum(v["spend"] for v in fb_raw[p].values())
        tc  = sum(v["conv" ] for v in fb_raw[p].values())
        tpu = sum(v["purchases"] for v in fb_raw[p].values())
        summaries[p] = {
            "label":     PERIODS[p]["label"],
            "sales":     ts,
            "spend":     tsp,
            "conv":      tc,
            "purchases": tpu,
            "roas":      tc / tsp if tsp else 0,
            "cpa":       tsp / tpu if tpu else 0,
            "mer":       ts  / tsp if tsp else 0,
        }

    # ── Shopify product table
    all_shopify = set()
    for d in sales_raw.values():
        all_shopify.update(d.keys())

    shopify_rows = []
    for prod in sorted(all_shopify,
                       key=lambda p: sales_raw["Mar 2026"].get(p, 0),
                       reverse=True):
        r = {"product": prod}
        for p in PERIOD_KEYS:
            r[p] = sales_raw[p].get(prod, 0.0)
        m25, m26 = r["Mar 2025"], r["Mar 2026"]
        r["yoy"] = (m26 - m25) / m25 * 100 if m25 > 0 else None
        shopify_rows.append(r)

    # ── FB product table
    all_fb = set()
    for d in fb_raw.values():
        all_fb.update(d.keys())

    fb_rows = []
    for prod in sorted(all_fb,
                       key=lambda p: fb_raw["Mar 2026"].get(p, {}).get("spend", 0),
                       reverse=True):
        r = {"product": prod}
        for p in PERIOD_KEYS:
            d = fb_raw[p].get(prod, {"spend": 0, "conv": 0, "purchases": 0})
            r[f"{p}_spend"]     = d["spend"]
            r[f"{p}_conv"]      = d["conv"]
            r[f"{p}_purchases"] = d["purchases"]
            r[f"{p}_roas"]      = d["conv"] / d["spend"] if d["spend"] > 0 else 0
        s25, s26 = r["Mar 2025_spend"], r["Mar 2026_spend"]
        c25, c26 = r["Mar 2025_conv" ], r["Mar 2026_conv" ]
        r["spend_growth"] = (s26 - s25) / s25 * 100 if s25 > 0 else None
        r["conv_growth"]  = (c26 - c25) / c25 * 100 if c25 > 0 else None
        fb_rows.append(r)

    # ── Scaling rows (products with Mar 2025 + Mar 2026 FB data)
    scale_rows = [r for r in fb_rows
                  if r["Mar 2025_spend"] > 0 and r["Mar 2026_spend"] > 0
                  and r["product"] not in ("General / DPA", "Amazon (CA)", "Other")]

    return summaries, shopify_rows, fb_rows, scale_rows, ads_raw, sales_raw, fb_raw


# ── Insight engine ─────────────────────────────────────────────────────────────

def compute_insights(summaries, shopify_rows, fb_rows, scale_rows, ads_raw, sales_raw, fb_raw):
    """Return structured insight objects grouped by type."""
    insights = {"scale": [], "watch": [], "act": [], "context": []}
    cur = "Mar 2026"

    # ── MER trend
    m25 = summaries["Mar 2025"]
    f26 = summaries["Feb 2026"]
    m26 = summaries["Mar 2026"]
    insights["context"].append(
        f"<strong>Note on MER:</strong> MER (Media Efficiency Ratio) = Total Shopify Revenue ÷ Total FB Ad Spend. "
        f"It is <em>not</em> the same as ROAS — it includes all Shopify revenue (organic, email, direct), not just "
        f"what Facebook claims to have driven. "
        f"Mar 2025 MER of <strong>{m25['mer']:.1f}x</strong> is artificially high because FB spend was only "
        f"<strong>${m25['spend']:,.0f}</strong> — nearly all of the ${m25['sales']:,.0f} in Shopify sales that period "
        f"came from organic/email/direct channels, not paid ads. It is <strong>not a reliable efficiency signal</strong> "
        f"at that spend level. "
        f"The meaningful comparison is Feb 2026 (<strong>{f26['mer']:.1f}x MER</strong>) vs "
        f"Mar 2026 (<strong>{m26['mer']:.1f}x MER</strong>) — a healthy slight decline as FB spend scales from "
        f"${f26['spend']:,.0f} to ${m26['spend']:,.0f} while Shopify revenue grew "
        f"<strong>+{(m26['sales']-m25['sales'])/m25['sales']*100:.0f}%</strong> YoY."
    )

    # ── ROAS above/below target per product
    spend_threshold = 100  # only flag products with meaningful spend
    below_target = [(r["product"], r[f"{cur}_spend"], r[f"{cur}_roas"])
                    for r in fb_rows
                    if r[f"{cur}_spend"] >= spend_threshold
                    and r[f"{cur}_roas"] < ROAS_TARGET
                    and r["product"] not in ("General / DPA", "Amazon (CA)", "Other")]

    above_target = [(r["product"], r[f"{cur}_spend"], r[f"{cur}_roas"])
                    for r in fb_rows
                    if r[f"{cur}_spend"] >= spend_threshold
                    and r[f"{cur}_roas"] >= ROAS_TARGET
                    and r["product"] not in ("General / DPA", "Amazon (CA)", "Other")]

    # ── Hidden gems: high ROAS, very low spend (< $300)
    hidden_gems = [(r["product"], r[f"{cur}_spend"], r[f"{cur}_roas"])
                   for r in fb_rows
                   if r[f"{cur}_spend"] > 0 and r[f"{cur}_spend"] < 300
                   and r[f"{cur}_roas"] > 5
                   and r["product"] not in ("General / DPA", "Amazon (CA)", "Other")]

    # ── Individual creative standouts in Mar 2026
    mar26_ads = ads_raw["Mar 2026"]
    top_creatives = sorted([a for a in mar26_ads if a["conv"] > 0 and a["spend"] >= 20],
                           key=lambda a: a["roas"], reverse=True)[:5]
    worst_creatives = sorted([a for a in mar26_ads if a["spend"] >= 200 and a["roas"] < ROAS_TARGET],
                              key=lambda a: a["roas"])[:3]

    # ── Products with Shopify sales but zero FB spend in Mar 2026
    fb_prods_with_spend = {r["product"] for r in fb_rows if r[f"{cur}_spend"] > 0}
    organic_only = [(r["product"], r["Mar 2026"])
                    for r in shopify_rows
                    if r["Mar 2026"] > 1000
                    and r["product"] not in fb_prods_with_spend
                    and r["product"] not in ("Other",)]

    # ── Amazon spend with zero tracked conversions
    amazon_row = next((r for r in fb_rows if r["product"] == "Amazon (CA)"), None)
    # Identify which product(s) the Amazon ads are for (from ad names)
    amazon_ads = [a for a in ads_raw[cur] if a["product"] == "Amazon (CA)"]
    amazon_products = set()
    for a in amazon_ads:
        n = a["name"].lower()
        if "woodox" in n or "wood ox" in n or "sling" in n:
            amazon_products.add("WoodOX Sling")
        elif "logox" in n or "multitool" in n:
            amazon_products.add("LogOX 3-in-1 MultiTool")
        elif "forester" in n:
            amazon_products.add("LogOX Forester Package")
    amazon_products_str = " & ".join(sorted(amazon_products)) if amazon_products else "unknown product(s)"
    if amazon_row and amazon_row[f"{cur}_spend"] > 0 and amazon_row[f"{cur}_conv"] == 0:
        insights["act"].append({
            "title": "WoodOX Sling Amazon Campaigns — Untrackable ROAS",
            "body": f"<strong>${amazon_row[f'{cur}_spend']:,.0f} in {amazon_products_str} ads</strong> are sending "
                    f"traffic to amazon.ca (not the Shopify PDP) with <strong>$0 tracked conversion value</strong>. "
                    f"Facebook cannot track Amazon purchases, so this entire budget appears as 0x ROAS. "
                    f"Note: WoodOX Sling has <em>zero</em> Shopify-destined FB ads in Mar 2026 — all its paid support "
                    f"goes to Amazon. Either switch landing pages to the Shopify PDP to restore attribution, "
                    f"or measure via MER (compare Shopify WoodOX Sling sales on vs. off ad days)."
        })

    # ── Dan-D-Lift opportunity (check individual ads)
    ddl_ads = [a for a in mar26_ads if a["product"] == "TimberOX Dan-D-Lift"]
    if ddl_ads:
        best_ddl = max(ddl_ads, key=lambda a: a["roas"])
        total_ddl_spend = sum(a["spend"] for a in ddl_ads)
        total_ddl_conv  = sum(a["conv"]  for a in ddl_ads)
        if best_ddl["roas"] > 10 and total_ddl_spend < 500:
            insights["scale"].append({
                "title": "TimberOX Dan-D-Lift — Massive Untapped Opportunity",
                "body": f"<strong>Total Dan-D-Lift spend in Mar 2026: ${total_ddl_spend:,.0f}</strong> "
                        f"across {len(ddl_ads)} active creative(s), returning ${total_ddl_conv:,.0f} in tracked conversions. "
                        f"Best creative: <em>\"{best_ddl['name'][:50]}\"</em> — "
                        f"<strong>{best_ddl['roas']:.0f}x ROAS</strong> "
                        f"(${best_ddl['conv']:,.0f} revenue on ${best_ddl['spend']:,.0f} spend). "
                        f"At ~$850/unit AOV and only ${total_ddl_spend:,.0f} total spend, this product is massively underfunded. "
                        f"Increase the top creative's daily budget immediately and test new audiences."
            })

    # ── Products performing above ROAS target
    for prod, spend, roas in sorted(above_target, key=lambda x: x[2], reverse=True):
        if roas > 4.0 and spend > 200:
            insights["scale"].append({
                "title": f"{prod} — Scale Budget ({roas:.1f}x ROAS)",
                "body": f"Generating <strong>{roas:.1f}x ROAS</strong> on ${spend:,.0f} spend in Mar 2026, "
                        f"well above the {ROAS_TARGET:.0f}x target. "
                        f"This product has room to absorb more budget before ROAS compresses to breakeven. "
                        f"Test increasing spend 30–50% while monitoring ROAS weekly."
            })

    # ── Hidden gems
    for prod, spend, roas in hidden_gems:
        insights["scale"].append({
            "title": f"{prod} — Underfunded (${spend:.0f} spend, {roas:.1f}x ROAS)",
            "body": f"Only <strong>${spend:,.0f} spent</strong> but returning <strong>{roas:.1f}x ROAS</strong>. "
                    f"This is a signal the audience isn't saturated. Increase budget to at least $300–500 "
                    f"to get a statistically meaningful read, then scale if ROAS holds."
        })

    # ── Organic-only high-revenue products
    for prod, rev in sorted(organic_only, key=lambda x: x[1], reverse=True):
        insights["scale"].append({
            "title": f"{prod} — No Paid Support Despite ${rev:,.0f} Shopify Sales",
            "body": f"Generating <strong>${rev:,.0f} in Shopify net sales</strong> in Mar 2026 "
                    f"with no active Facebook ads. This revenue is likely organic/email. "
                    f"Test a small FB campaign (${200}–500) to see if paid can amplify what's already converting."
        })

    # ── Watch: ROAS compressing near target
    for r in scale_rows:
        sg = r["spend_growth"]
        r26_roas = r["Mar 2026_roas"]
        r25_roas = r["Mar 2025_roas"]
        if sg and sg > 50 and ROAS_TARGET * 0.7 <= r26_roas < ROAS_TARGET * 1.3:
            insights["watch"].append({
                "title": f"{r['product']} — ROAS Near Floor ({r26_roas:.2f}x)",
                "body": f"Spend grew <strong>+{sg:.0f}%</strong> from Mar 2025 → Mar 2026, and ROAS has "
                        f"compressed to <strong>{r26_roas:.2f}x</strong> (target: {ROAS_TARGET}x). "
                        f"Hold current budget and optimize creatives before scaling further. "
                        f"One bad week could push this below breakeven."
            })

    # ── Watch: high-spend ads with no conversion data
    no_conv_ads = [a for a in mar26_ads if a["spend"] >= 200 and a["conv"] == 0 and a["purchases"] == 0]
    if no_conv_ads:
        total_dark = sum(a["spend"] for a in no_conv_ads)
        insights["watch"].append({
            "title": f"${total_dark:,.0f} in Spend With No Tracked Conversions",
            "body": f"{len(no_conv_ads)} active ads in Mar 2026 show <strong>$0 in reported conversion value</strong>. "
                    f"This may indicate attribution gaps (iOS privacy), long purchase cycles, or truly non-converting ads. "
                    f"Cross-reference against Shopify revenue by date. If Shopify sales drop on days these ads run, pause them."
        })

    # ── Act: ads below ROAS target with large spend
    for prod, spend, roas in sorted(below_target, key=lambda x: x[1], reverse=True):
        insights["act"].append({
            "title": f"{prod} — Below ROAS Target ({roas:.2f}x on ${spend:,.0f} spend)",
            "body": f"Spending <strong>${spend:,.0f}</strong> but only returning <strong>{roas:.2f}x ROAS</strong> "
                    f"against a {ROAS_TARGET}x target. Audit the creative mix — pause underperforming individual ads "
                    f"first (see creative table below). If the best creative still can't reach {ROAS_TARGET}x, "
                    f"reduce budget 30% and reallocate to higher-ROAS products."
        })

    # ── Top creatives insight
    if top_creatives:
        best = top_creatives[0]
        insights["scale"].append({
            "title": f"Best Creative in Mar 2026: {best['roas']:.0f}x ROAS",
            "body": f"<em>\"{best['name'][:60]}\"</em> ({best['product']}) returned "
                    f"<strong>{best['roas']:.1f}x ROAS</strong> "
                    f"(${best['conv']:,.0f} on ${best['spend']:,.0f}). "
                    f"Duplicate this creative, test new audiences, and increase its budget — "
                    f"it's the current benchmark for what good looks like."
        })

    return insights, top_creatives, worst_creatives


# ── HTML helpers ───────────────────────────────────────────────────────────────

def fmt_usd(v):    return f"${v:,.0f}"
def fmt_pct(v, plus=True):
    if v is None: return "—"
    sign = "+" if (v >= 0 and plus) else ""
    return f"{sign}{v:.1f}%"
def roas_color(v):
    if v >= ROAS_TARGET:         return "#10b981"
    if v >= ROAS_TARGET * 0.7:  return "#f59e0b"
    return "#ef4444"
def yoy_color(v):
    if v is None: return "#94a3b8"
    return "#10b981" if v >= 0 else "#ef4444"


# ── HTML generation ────────────────────────────────────────────────────────────

def generate_html(summaries, shopify_rows, fb_rows, scale_rows, ads_raw, sales_raw, fb_raw):
    insights, top_creatives, worst_creatives = compute_insights(
        summaries, shopify_rows, fb_rows, scale_rows, ads_raw, sales_raw, fb_raw
    )

    p = PERIOD_KEYS
    colors = ["#1A5FA8", "#C85C28", "#2A7A3B"]  # LogOX blue, brand orange, forest green

    # ── Chart data
    top8_shop = shopify_rows[:8]
    chart_shop_labels = [r["product"] for r in top8_shop]
    chart_shop_datasets = [{"label": pk, "data": [round(r[pk], 2) for r in top8_shop],
                             "backgroundColor": colors[i], "borderRadius": 4}
                           for i, pk in enumerate(p)]

    fb_top = [r for r in fb_rows if r["product"] not in ("General / DPA", "Amazon (CA)", "Other")][:8]
    chart_fb_labels = [r["product"] for r in fb_top]
    chart_fb_spend_datasets = [{"label": pk, "data": [round(r[f"{pk}_spend"], 2) for r in fb_top],
                                  "backgroundColor": colors[i], "borderRadius": 4}
                                for i, pk in enumerate(p)]
    chart_roas_datasets = [{"label": pk, "data": [round(r[f"{pk}_roas"], 2) for r in fb_top],
                              "backgroundColor": colors[i], "borderRadius": 4}
                           for i, pk in enumerate(p)]

    scale_chart_rows = [r for r in scale_rows]
    chart_scale_labels = [r["product"] for r in scale_chart_rows]
    chart_scale_spend  = [round(r["spend_growth"], 1) if r["spend_growth"] is not None else 0 for r in scale_chart_rows]
    chart_scale_conv   = [round(r["conv_growth"],  1) if r["conv_growth"]  is not None else 0 for r in scale_chart_rows]

    # ── Period summary cards
    def summary_card(pk):
        s = summaries[pk]
        roas_cls = "green" if s["roas"] >= ROAS_TARGET else ("amber" if s["roas"] >= ROAS_TARGET * 0.7 else "red")
        mer_cls  = "green" if s["mer"]  >= 4           else ("amber" if s["mer"]  >= 2               else "red")
        return f"""
        <div class="card summary-card">
          <div class="card-period">{s['label']}</div>
          <div class="metrics-grid">
            <div class="metric">
              <span class="metric-label">Shopify Net Sales</span>
              <span class="metric-value blue">{fmt_usd(s['sales'])}</span>
            </div>
            <div class="metric">
              <span class="metric-label">FB Ad Spend</span>
              <span class="metric-value purple">{fmt_usd(s['spend'])}</span>
            </div>
            <div class="metric">
              <span class="metric-label">FB Conv. Value</span>
              <span class="metric-value teal">{fmt_usd(s['conv'])}</span>
            </div>
            <div class="metric">
              <span class="metric-label">FB Purchases</span>
              <span class="metric-value">{s['purchases']}</span>
            </div>
            <div class="metric">
              <span class="metric-label">FB ROAS</span>
              <span class="metric-value {roas_cls}">{s['roas']:.2f}x</span>
            </div>
            <div class="metric">
              <span class="metric-label">MER</span>
              <span class="metric-value {mer_cls}">{s['mer']:.1f}x</span>
            </div>
          </div>
        </div>"""

    cards_html = "".join(summary_card(pk) for pk in p)

    # ── Insights HTML
    def insight_card(item, kind):
        icon = {"scale": "🚀", "watch": "⚠️", "act": "🔴"}.get(kind, "•")
        return f"""
        <div class="insight-card {kind}">
          <div class="insight-title">{icon} {item['title']}</div>
          <div class="insight-body">{item['body']}</div>
        </div>"""

    scale_cards = "".join(insight_card(i, "scale") for i in insights["scale"])
    watch_cards = "".join(insight_card(i, "watch") for i in insights["watch"])
    act_cards   = "".join(insight_card(i, "act"  ) for i in insights["act"  ])
    context_txt = insights["context"][0] if insights["context"] else ""

    # Top creative table
    def creative_row(a):
        roas_col = roas_color(a["roas"])
        return f"""<tr>
          <td class="product-name" style="max-width:320px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis"
              title="{a['name']}">{a['name'][:55]}{'…' if len(a['name'])>55 else ''}</td>
          <td>{a['product']}</td>
          <td>{fmt_usd(a['spend'])}</td>
          <td>{fmt_usd(a['conv'])}</td>
          <td>{a['purchases']}</td>
          <td style="color:{roas_col};font-weight:700">{a['roas']:.2f}x</td>
        </tr>"""

    top_creatives_html    = "".join(creative_row(a) for a in top_creatives)
    worst_creatives_html  = "".join(creative_row(a) for a in worst_creatives)

    # ── Shopify table
    def shopify_row_html(r):
        yoy_col = yoy_color(r["yoy"])
        return f"""<tr>
          <td class="product-name">{r['product']}</td>
          <td>{fmt_usd(r['Mar 2025'])}</td>
          <td>{fmt_usd(r['Feb 2026'])}</td>
          <td>{fmt_usd(r['Mar 2026'])}</td>
          <td style="color:{yoy_col};font-weight:600">{fmt_pct(r['yoy'])}</td>
        </tr>"""

    shopify_table_rows = "".join(shopify_row_html(r) for r in shopify_rows)

    # ── FB detail table
    def fb_row_html(r):
        rows = ""
        for pk in p:
            spend = r[f"{pk}_spend"]; conv = r[f"{pk}_conv"]
            roas  = r[f"{pk}_roas"]; purch = r[f"{pk}_purchases"]
            roas_col = roas_color(roas) if spend > 0 else "#94a3b8"
            rows += f"""<tr class="fb-data-row">
              <td></td>
              <td class="period-sub">{pk}</td>
              <td>{'—' if spend==0 else fmt_usd(spend)}</td>
              <td>{'—' if conv==0  else fmt_usd(conv)}</td>
              <td>{'—' if purch==0 else purch}</td>
              <td style="color:{roas_col};font-weight:600">{'—' if spend==0 else f'{roas:.2f}x'}</td>
            </tr>"""
        sg, cg = r["spend_growth"], r["conv_growth"]
        rows += f"""<tr class="scale-row">
              <td></td><td class="period-sub" style="color:#94a3b8;font-style:italic">YoY (Mar)</td>
              <td style="color:{yoy_color(sg)}">{fmt_pct(sg)}</td>
              <td style="color:{yoy_color(cg)}">{fmt_pct(cg)}</td>
              <td>—</td><td>—</td>
            </tr>"""
        return f"""<tr class="fb-product-header"><td colspan="6" class="product-name">{r['product']}</td></tr>{rows}"""

    fb_table_rows = "".join(fb_row_html(r) for r in fb_rows)

    # ── Scaling table
    def scale_row_html(r):
        sg, cg = r["spend_growth"], r["conv_growth"]
        s25, s26 = r["Mar 2025_spend"], r["Mar 2026_spend"]
        c25, c26 = r["Mar 2025_conv" ], r["Mar 2026_conv" ]
        r25, r26 = r["Mar 2025_roas" ], r["Mar 2026_roas" ]
        if sg is not None and cg is not None:
            if cg > sg:   verdict = "<span class='badge green'>Scaling Efficiently ✓</span>"
            elif sg > 0 and cg > 0: verdict = "<span class='badge amber'>Scaling (Watch)</span>"
            elif sg > 0:  verdict = "<span class='badge red'>Scaling Poorly ✗</span>"
            else:         verdict = "<span class='badge gray'>—</span>"
        else:             verdict = "<span class='badge gray'>—</span>"
        return f"""<tr>
          <td class="product-name">{r['product']}</td>
          <td>{fmt_usd(s25)}</td><td>{fmt_usd(s26)}</td>
          <td style="color:{yoy_color(sg)};font-weight:600">{fmt_pct(sg)}</td>
          <td>{fmt_usd(c25)}</td><td>{fmt_usd(c26)}</td>
          <td style="color:{yoy_color(cg)};font-weight:600">{fmt_pct(cg)}</td>
          <td style="color:{roas_color(r25)}">{r25:.2f}x</td>
          <td style="color:{roas_color(r26)}">{r26:.2f}x</td>
          <td>{verdict}</td>
        </tr>"""

    scale_rows_html = "".join(scale_row_html(r) for r in scale_rows)

    generated = datetime.today().strftime("%B %d, %Y")

    # ── Full HTML ──────────────────────────────────────────────────────────────
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LogOX Performance Dashboard — {generated}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    /* LogOX Brand Colors */
    --logox-blue:   #1A5FA8;   /* "OX" blue from logo */
    --logox-orange: #C85C28;   /* tagline burnt orange */
    --logox-black:  #1A1A1A;   /* "Log" text black */

    /* Light theme surfaces */
    --bg:           #F7F5F2;   /* warm off-white, like natural paper */
    --surface:      #FFFFFF;
    --surface-2:    #F0EDE8;   /* slightly warm gray for table headers */
    --border:       #E0DBD5;
    --border-light: #EDE9E4;

    /* Semantic colors */
    --green:  #2A7A3B;
    --red:    #C0392B;
    --amber:  #C85C28;   /* brand orange doubles as warning */
    --blue:   #1A5FA8;

    /* Typography */
    --text:   #1C1C1C;
    --muted:  #6B6460;
    --subtle: #9E9792;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--text); font-family:'Inter',system-ui,-apple-system,sans-serif; padding:32px; max-width:1400px; margin:0 auto; }}

  /* ── Header ── */
  .report-header {{ display:flex; align-items:center; justify-content:space-between; padding-bottom:24px; margin-bottom:36px; border-bottom:3px solid var(--logox-blue); }}
  .header-left {{ display:flex; align-items:center; gap:24px; }}
  .header-logo {{ height:80px; width:auto; }}
  .header-divider {{ width:1px; height:64px; background:var(--border); }}
  .header-text h1 {{ font-size:1.5rem; font-weight:800; color:var(--logox-black); letter-spacing:-.02em; }}
  .header-text .subtitle {{ font-size:.85rem; color:var(--muted); margin-top:4px; }}
  .header-right {{ text-align:right; }}
  .header-date {{ font-size:.8rem; color:var(--muted); }}
  .header-badge {{ display:inline-block; margin-top:6px; padding:4px 12px; background:var(--logox-orange); color:#fff; font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; border-radius:4px; }}

  h2 {{ font-size:1.1rem; font-weight:700; color:var(--logox-black); margin-bottom:4px; letter-spacing:-.01em; }}
  .section {{ margin-bottom:48px; }}
  .section-header {{ display:flex; align-items:baseline; gap:12px; margin-bottom:16px; }}
  .section-sub {{ font-size:.82rem; color:var(--muted); }}

  /* ── Summary cards ── */
  .cards-row {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
  .card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:20px; box-shadow:0 1px 4px rgba(0,0,0,.06); }}
  .card-period {{ font-size:.7rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--logox-blue); margin-bottom:14px; padding-bottom:10px; border-bottom:2px solid var(--logox-blue); }}
  .metrics-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .metric {{ display:flex; flex-direction:column; gap:3px; }}
  .metric-label {{ font-size:.67rem; color:var(--muted); text-transform:uppercase; letter-spacing:.07em; font-weight:500; }}
  .metric-value {{ font-size:1.15rem; font-weight:700; color:var(--logox-black); }}
  .metric-value.blue   {{ color:var(--logox-blue);   }}
  .metric-value.orange {{ color:var(--logox-orange); }}
  .metric-value.green  {{ color:var(--green);  }}
  .metric-value.amber  {{ color:var(--amber);  }}
  .metric-value.red    {{ color:var(--red);    }}

  /* ── Insights ── */
  .insights-context {{ background:#EBF2F9; border:1px solid #BAD3EC; border-left:4px solid var(--logox-blue); border-radius:8px; padding:14px 18px; margin-bottom:20px; font-size:.88rem; line-height:1.7; color:#2C3E50; }}
  .insights-context strong {{ color:var(--logox-black); font-weight:700; }}
  .insights-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
  .insight-col-header {{ font-size:.68rem; font-weight:800; text-transform:uppercase; letter-spacing:.1em; padding:7px 12px; border-radius:6px; margin-bottom:12px; }}
  .insight-col-header.scale {{ background:#E8F5EA; color:var(--green); border:1px solid #C8E6CA; }}
  .insight-col-header.watch {{ background:#FDF3E7; color:#A0522D; border:1px solid #F5CBA7; }}
  .insight-col-header.act   {{ background:#FDEDEC; color:var(--red); border:1px solid #F1948A; }}
  .insight-card {{ border-radius:8px; padding:14px 16px; margin-bottom:10px; }}
  .insight-card.scale {{ background:#F0FAF1; border:1px solid #C3E6C7; }}
  .insight-card.watch {{ background:#FEF9F0; border:1px solid #F5D5A3; }}
  .insight-card.act   {{ background:#FEF1EF; border:1px solid #F4A99E; }}
  .insight-title {{ font-size:.85rem; font-weight:700; margin-bottom:7px; }}
  .insight-card.scale .insight-title {{ color:#1B6B2A; }}
  .insight-card.watch .insight-title {{ color:#8B4513; }}
  .insight-card.act   .insight-title {{ color:#922B21; }}
  .insight-body {{ font-size:.8rem; line-height:1.65; color:#444; }}
  .insight-body strong {{ color:var(--logox-black); }}
  .insight-body em {{ color:var(--muted); font-style:normal; }}

  /* ── Charts ── */
  .charts-row {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .chart-card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:20px; box-shadow:0 1px 4px rgba(0,0,0,.06); }}
  .chart-card.full {{ grid-column:1/-1; }}
  canvas {{ max-height:300px; }}

  /* ── Tables ── */
  .table-wrap {{ overflow-x:auto; }}
  table {{ width:100%; border-collapse:collapse; font-size:.86rem; }}
  thead th {{ background:var(--surface-2); color:var(--muted); font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.07em; padding:10px 12px; text-align:right; border-bottom:2px solid var(--border); white-space:nowrap; }}
  thead th:first-child {{ text-align:left; }}
  tbody tr {{ border-bottom:1px solid var(--border-light); }}
  tbody tr:hover {{ background:#F9F7F4; }}
  tbody td {{ padding:9px 12px; text-align:right; color:var(--text); }}
  tbody td:first-child {{ text-align:left; }}
  .product-name {{ font-weight:600; color:var(--logox-black); }}
  .period-sub {{ color:var(--muted); font-size:.76rem; padding-left:24px !important; text-align:left !important; font-weight:500; }}
  .fb-product-header td {{ background:var(--surface-2); font-size:.9rem; padding:10px 12px; border-top:2px solid var(--border); color:var(--logox-blue); font-weight:700; }}
  .scale-row td {{ background:#FAFAF8; font-size:.79rem; border-top:1px dashed var(--border); color:var(--muted); }}
  .badge {{ display:inline-block; padding:3px 9px; border-radius:999px; font-size:.7rem; font-weight:700; }}
  .badge.green {{ background:#E8F5EA; color:var(--green); border:1px solid #C3E6C7; }}
  .badge.amber {{ background:#FDF3E7; color:#A0522D; border:1px solid #F5CBA7; }}
  .badge.red   {{ background:#FDEDEC; color:var(--red); border:1px solid #F4A99E; }}
  .badge.gray  {{ background:#F0EDE8; color:var(--muted); border:1px solid var(--border); }}
  .target-note {{ font-size:.77rem; color:var(--logox-orange); margin-top:10px; font-weight:500; }}
  .footer {{ margin-top:48px; border-top:2px solid var(--border); padding-top:20px; font-size:.77rem; color:var(--muted); display:flex; align-items:center; justify-content:space-between; }}
  .footer img {{ height:32px; opacity:.6; }}
</style>
</head>
<body>

<!-- ── Brand Header ── -->
<div class="report-header">
  <div class="header-left">
    <img class="header-logo" src="https://www.thelogox.com/cdn/shop/files/logox-logo.png" alt="LogOX Logo" onerror="this.style.display='none'">
    <div class="header-divider"></div>
    <div class="header-text">
      <h1>Performance Dashboard</h1>
      <div class="subtitle">Facebook Ads &amp; Shopify Sales Analysis &nbsp;·&nbsp; All periods: Mar 1–10 or Feb 1–10</div>
    </div>
  </div>
  <div class="header-right">
    <div class="header-date">Generated {generated}</div>
    <div class="header-badge">Confidential</div>
  </div>
</div>

<!-- ── Period Summary ── -->
<div class="section">
  <h2>Period Overview</h2>
  <div class="cards-row">{cards_html}</div>
</div>

<!-- ── Insights & Recommendations ── -->
<div class="section">
  <h2>Insights &amp; Recommendations</h2>
  <p class="section-sub">Computed automatically from the data above. Priorities ranked by impact.</p>
  <div class="insights-context">{context_txt}</div>
  <div class="insights-grid">
    <div>
      <div class="insight-col-header scale">🚀 Scale — Do More of This</div>
      {scale_cards}
    </div>
    <div>
      <div class="insight-col-header watch">⚠️ Watch — Needs Monitoring</div>
      {watch_cards}
    </div>
    <div>
      <div class="insight-col-header act">🔴 Act — Fix or Pause</div>
      {act_cards}
    </div>
  </div>
</div>

<!-- ── Top/Worst Creatives ── -->
<div class="section">
  <h2>Creative Performance — Mar 2026</h2>
  <p class="section-sub">Individual ad-level ROAS. Minimum $20 spend included. Use these to guide creative decisions.</p>
  <div class="charts-row">
    <div class="card table-wrap">
      <h2 style="margin-bottom:12px;color:var(--green);font-size:1rem">🏆 Top Performing Creatives</h2>
      <table>
        <thead><tr><th>Ad Name</th><th>Product</th><th>Spend</th><th>Conv. Value</th><th>Purchases</th><th>ROAS</th></tr></thead>
        <tbody>{top_creatives_html}</tbody>
      </table>
    </div>
    <div class="card table-wrap">
      <h2 style="margin-bottom:12px;color:var(--red);font-size:1rem">🔴 Underperforming Creatives (Pause Candidates)</h2>
      <table>
        <thead><tr><th>Ad Name</th><th>Product</th><th>Spend</th><th>Conv. Value</th><th>Purchases</th><th>ROAS</th></tr></thead>
        <tbody>{worst_creatives_html}</tbody>
      </table>
    </div>
  </div>
</div>

<!-- ── Shopify Sales ── -->
<div class="section">
  <h2>Shopify Net Sales by Product</h2>
  <div class="chart-card full"><canvas id="shopifyChart"></canvas></div>
</div>

<!-- ── FB Performance Charts ── -->
<div class="section">
  <h2>Facebook Ad Performance by Product</h2>
  <div class="charts-row">
    <div class="chart-card"><h2>Ad Spend</h2><canvas id="fbSpendChart"></canvas></div>
    <div class="chart-card">
      <h2>ROAS <span style="color:var(--amber);font-size:.8rem">(target {ROAS_TARGET:.0f}x)</span></h2>
      <canvas id="roasChart"></canvas>
    </div>
  </div>
</div>

<!-- ── Scaling Analysis ── -->
<div class="section">
  <h2>Scaling Analysis: Mar 2025 → Mar 2026</h2>
  <div class="chart-card full" style="margin-bottom:20px">
    <h2>Spend Growth vs Revenue Growth</h2>
    <canvas id="scaleChart"></canvas>
    <p class="target-note">Green bars above purple = revenue growing faster than spend = scaling efficiently. ROAS target: {ROAS_TARGET:.0f}x.</p>
  </div>
  <div class="card table-wrap">
    <table>
      <thead><tr>
        <th>Product</th><th>Spend Mar'25</th><th>Spend Mar'26</th><th>Spend Δ%</th>
        <th>Conv. Mar'25</th><th>Conv. Mar'26</th><th>Conv. Δ%</th>
        <th>ROAS Mar'25</th><th>ROAS Mar'26</th><th>Verdict</th>
      </tr></thead>
      <tbody>{scale_rows_html}</tbody>
    </table>
  </div>
</div>

<!-- ── Shopify Detail Table ── -->
<div class="section">
  <h2>Shopify Net Sales — All Products</h2>
  <div class="card table-wrap">
    <table>
      <thead><tr><th>Product</th><th>Mar 2025</th><th>Feb 2026</th><th>Mar 2026</th><th>YoY (Mar)</th></tr></thead>
      <tbody>{shopify_table_rows}</tbody>
    </table>
  </div>
</div>

<!-- ── FB Detail Table ── -->
<div class="section">
  <h2>Facebook Ads — Full Breakdown by Product &amp; Period</h2>
  <div class="card table-wrap">
    <table>
      <thead><tr><th>Product</th><th>Period</th><th>Spend</th><th>Conv. Value</th><th>Purchases</th><th>ROAS</th></tr></thead>
      <tbody>{fb_table_rows}</tbody>
    </table>
  </div>
</div>

<div class="footer">
  <div>
    <strong style="color:var(--logox-black)">LogOX</strong> · Performance Dashboard · Generated {generated}<br>
    <span style="color:var(--logox-orange);font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.7rem">American Tools for Woodsmen®</span>
  </div>
  <img src="https://www.thelogox.com/cdn/shop/files/logox-logo.png" alt="LogOX" onerror="this.style.display='none'">
</div>

<script>
Chart.defaults.color='#6B6460';
Chart.defaults.borderColor='#E0DBD5';

new Chart(document.getElementById('shopifyChart'),{{
  type:'bar',
  data:{{labels:{json.dumps(chart_shop_labels)},datasets:{json.dumps(chart_shop_datasets)}}},
  options:{{responsive:true,plugins:{{legend:{{labels:{{color:'#1C1C1C'}}}}}},
    scales:{{
      x:{{ticks:{{color:'#6B6460',maxRotation:25}},grid:{{color:'#E0DBD5'}}}},
      y:{{ticks:{{color:'#6B6460',callback:v=>'$'+v.toLocaleString()}},grid:{{color:'#E0DBD5'}}}}
    }}
  }}
}});

new Chart(document.getElementById('fbSpendChart'),{{
  type:'bar',
  data:{{labels:{json.dumps(chart_fb_labels)},datasets:{json.dumps(chart_fb_spend_datasets)}}},
  options:{{responsive:true,plugins:{{legend:{{labels:{{color:'#1C1C1C'}}}}}},
    scales:{{
      x:{{ticks:{{color:'#6B6460',maxRotation:25}},grid:{{color:'#E0DBD5'}}}},
      y:{{ticks:{{color:'#6B6460',callback:v=>'$'+v.toLocaleString()}},grid:{{color:'#E0DBD5'}}}}
    }}
  }}
}});

new Chart(document.getElementById('roasChart'),{{
  type:'bar',
  data:{{labels:{json.dumps(chart_fb_labels)},datasets:{json.dumps(chart_roas_datasets)}}},
  plugins:[{{
    id:'roasLine',
    afterDraw(chart){{
      const {{ctx,chartArea:{{left,right}},scales:{{y}}}}=chart;
      const yp=y.getPixelForValue({ROAS_TARGET});
      ctx.save();ctx.setLineDash([6,4]);ctx.strokeStyle='#C85C28';ctx.lineWidth=2;
      ctx.beginPath();ctx.moveTo(left,yp);ctx.lineTo(right,yp);ctx.stroke();ctx.restore();
    }}
  }}],
  options:{{responsive:true,plugins:{{legend:{{labels:{{color:'#1C1C1C'}}}},
    tooltip:{{callbacks:{{label:ctx=>ctx.dataset.label+': '+ctx.raw.toFixed(2)+'x'}}}}}},
    scales:{{
      x:{{ticks:{{color:'#6B6460',maxRotation:25}},grid:{{color:'#E0DBD5'}}}},
      y:{{ticks:{{color:'#6B6460',callback:v=>v.toFixed(1)+'x'}},grid:{{color:'#E0DBD5'}}}}
    }}
  }}
}});

new Chart(document.getElementById('scaleChart'),{{
  type:'bar',
  data:{{
    labels:{json.dumps(chart_scale_labels)},
    datasets:[
      {{label:'Spend Growth %',data:{json.dumps(chart_scale_spend)},backgroundColor:'#1A5FA8',borderRadius:4}},
      {{label:'Conv. Revenue Growth %',data:{json.dumps(chart_scale_conv)},backgroundColor:'#2A7A3B',borderRadius:4}}
    ]
  }},
  options:{{responsive:true,plugins:{{legend:{{labels:{{color:'#1C1C1C'}}}}}},
    scales:{{
      x:{{ticks:{{color:'#6B6460',maxRotation:25}},grid:{{color:'#E0DBD5'}}}},
      y:{{ticks:{{color:'#6B6460',callback:v=>v+'%'}},grid:{{color:'#E0DBD5'}}}}
    }}
  }}
}});
</script>
</body>
</html>"""


# ── Self-review / validation ───────────────────────────────────────────────────

def validate(summaries, sales_raw, fb_raw):
    """
    Cross-check computed totals against raw CSV sums.
    Prints PASS/FAIL for each check and raises if any critical check fails.
    """
    errors = []

    for pk in PERIOD_KEYS:
        cfg = PERIODS[pk]

        # ── Re-sum Shopify sales directly from CSV
        raw_sales_total = 0.0
        with open(os.path.join(DATA_DIR, cfg["sales"]), newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    v = float(row.get("Net sales", 0) or 0)
                except ValueError:
                    v = 0
                if v > 0:
                    raw_sales_total += v
        computed_sales = sum(sales_raw[pk].values())
        # Computed will be less because we skip SKIP_NAMES; just verify computed <= raw total
        if computed_sales > raw_sales_total + 1:
            errors.append(f"[{pk}] Shopify: computed ${computed_sales:,.2f} > raw ${raw_sales_total:,.2f} — impossible overcount!")
        else:
            print(f"  ✓ [{pk}] Shopify sales: computed ${computed_sales:,.2f} ≤ raw total ${raw_sales_total:,.2f}")

        # ── Re-sum FB spend directly from CSV (all rows with spend > 0)
        raw_fb_spend = 0.0
        raw_fb_conv  = 0.0
        product_spend: dict = {}
        with open(os.path.join(DATA_DIR, cfg["fb"]), newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    spend = float(row.get("Amount spent (USD)", 0) or 0)
                except ValueError:
                    spend = 0
                try:
                    conv = float(row.get("Purchases conversion value", 0) or 0)
                except ValueError:
                    conv = 0
                if spend <= 0:
                    continue
                raw_fb_spend += spend
                raw_fb_conv  += conv
                prod = url_to_product(row.get("Link (ad settings)", "").strip())
                product_spend[prod] = product_spend.get(prod, 0.0) + spend

        computed_spend = sum(v["spend"] for v in fb_raw[pk].values())
        computed_conv  = sum(v["conv"]  for v in fb_raw[pk].values())

        if abs(computed_spend - raw_fb_spend) > 0.02:
            errors.append(f"[{pk}] FB spend mismatch: computed ${computed_spend:,.2f} vs raw ${raw_fb_spend:,.2f}")
        else:
            print(f"  ✓ [{pk}] FB total spend: ${computed_spend:,.2f} matches raw")

        if abs(computed_conv - raw_fb_conv) > 0.02:
            errors.append(f"[{pk}] FB conv mismatch: computed ${computed_conv:,.2f} vs raw ${raw_fb_conv:,.2f}")
        else:
            print(f"  ✓ [{pk}] FB total conv value: ${computed_conv:,.2f} matches raw")

        # ── Per-product spend spot-check (catch URL-aggregation bugs)
        for prod, raw_ps in product_spend.items():
            comp_ps = fb_raw[pk].get(prod, {}).get("spend", 0.0)
            if abs(comp_ps - raw_ps) > 0.02:
                errors.append(
                    f"[{pk}] Product spend mismatch for '{prod}': "
                    f"computed ${comp_ps:,.2f} vs raw ${raw_ps:,.2f}"
                )
            else:
                print(f"  ✓ [{pk}] '{prod}' spend: ${comp_ps:,.2f}")

    if errors:
        print("\n❌ VALIDATION FAILED — Report NOT written:")
        for e in errors:
            print(f"   {e}")
        raise SystemExit(1)

    print("\n✅ All validation checks passed.\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Reading CSV files...")
    summaries, shopify_rows, fb_rows, scale_rows, ads_raw, sales_raw, fb_raw = compute()

    print("\nRunning self-review validation...")
    validate(summaries, sales_raw, fb_raw)

    print("Generating report with insights...")
    html = generate_html(summaries, shopify_rows, fb_rows, scale_rows, ads_raw, sales_raw, fb_raw)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✓ Report saved to: {OUT_FILE}")
    print("\nPeriod Summary:")
    for pk in PERIOD_KEYS:
        s = summaries[pk]
        print(f"  {pk}: Sales={fmt_usd(s['sales'])} | Spend={fmt_usd(s['spend'])} | ROAS={s['roas']:.2f}x | MER={s['mer']:.1f}x")
