# Shopify Product Data Analysis — Project Documentation

## Overview
Multi-year Shopify sales data analysis covering annual SKU performance from 2021–2025.
The goal is to identify top-performing SKUs, track year-over-year revenue trends, and
surface strategic recommendations for inventory focus and SKU rationalization.

## Directory Structure

```
Shopify Product Data Analysis/
├── CLAUDE.md                   # This file — project documentation
├── README.md                   # How to use the agent (plain English instructions)
├── .env                        # API keys (never share or commit this file)
├── .claude/
│   └── settings.json           # Claude project-level permissions and settings
│
├── agent.py                    # AI agent — reads config and generates the dashboard
├── config.py                   # Edit this for each new client before running agent.py
│
├── data/
│   └── Harmony House Foods/    # CSV files for Harmony House Foods (2021–2025)
│       ├── 2021.csv
│       ├── 2022.csv
│       ├── 2023.csv
│       ├── 2024.csv
│       └── 2025.csv
│
└── reports/                    # Generated dashboards (never overwritten)
    └── Shopify_2026-03-13.html # Agent-generated dashboard (ClientName_date.html)
```

## Primary Workflow (Agent)

1. Drop client CSV files into `data/raw/` or a named folder e.g. `data/brand-x/`
2. Edit `config.py` — set client name, data folder, excluded IDs, and any custom notes
3. Run the agent:

```bash
cd "/Users/devan/Desktop/Claude Code Agents/Shopify Product Data Analysis"
python3.11 agent.py
```

Output: `reports/{ClientName}_{date}.html`

## config.py Fields

| Field          | Description                                      |
|----------------|--------------------------------------------------|
| CLIENT_NAME    | Client/brand name — used in filename and title   |
| DATA_FOLDER    | Path to folder containing the CSV files          |
| EXCLUDED_IDS   | List of row IDs to filter out (non-product rows) |
| CUSTOM_NOTES   | Plain English instructions for this client       |

## Data Format
Each CSV file contains the following columns:

| Column  | Description                            |
|---------|----------------------------------------|
| Name    | SKU product name                       |
| Sold    | Units sold during the year             |
| Amount  | Total revenue (USD) for that SKU/year  |
| Profit  | Total profit (USD) for that SKU/year   |
| Id      | Internal SKU identifier                |

## Default Excluded Row Types (Shopify client)

| ID      | Description                |
|---------|----------------------------|
| 0       | Phone custom product       |
| 99900   | Shipping adjustment        |
| 2084    | Free bonus / gift item     |
| 1876    | Gift certificate           |
| 1876-2  | Gift certificate variant   |
| 7998    | Custom blend               |

Rows with `Amount <= 0` are also excluded.

## Years Available (Shopify)
- 2021 ✓
- 2022 ✓
- 2023 ✓
- 2024 ✓
- 2025 ✓
- 2017–2020: Not currently available

## Memory / Persistence
Claude project memory is stored at:
`~/.claude/projects/-Users-devan-Desktop-Claude-Code-Agents-Shopify-Product-Data-Analysis/memory/`
