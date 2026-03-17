"""
Dashboard Agent
---------------
Edit config.py first, then run this script to generate a dashboard.

Usage:
    python3.11 agent.py
"""

import anyio
import subprocess
import os
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
import config

# Build output filename from client name + today's date
# e.g. reports/LogOX/LogOX_2026-03-14.html
date_str = datetime.today().strftime("%Y-%m-%d")
client_folder = f"reports/{config.CLIENT_NAME}"
output_file = f"{client_folder}/{config.CLIENT_NAME.replace(' ', '_')}_{date_str}.html"

PROMPT = f"""
You are a data analyst. Your job is to read the Shopify sales CSV files
in the {config.DATA_FOLDER}/ folder and generate a new HTML dashboard.

Output file: {output_file}

The dashboard must:
1. Match the same structure, style, and dark theme as the existing reports/dashboard.html
2. Include all the same sections:
   - KPI summary row (revenue, profit, margin, SKU count)
   - Annual revenue & profit by year (chart + table)
   - Gross margin trend by year
   - Most recent year vs prior year YoY decline breakdown
   - Top 15 SKUs by most recent year revenue (chart + table with status badges)
   - Revenue concentration (top 5/10/15/20/25/30 SKUs)
   - Top 10 SKUs from prior year — multi-year trend chart + table
   - Top 20 all-time SKUs
   - Biggest revenue decliners (most recent year vs prior year)
   - SKU-level YoY change table (top 40 by prior year revenue)
   - Growth opportunities (emerging SKUs + consistent growers)
   - Strategic recommendations section
3. Use "{config.CLIENT_NAME}" as the client name in the report title

Important rules:
- Exclude rows where Id is in: {config.EXCLUDED_IDS}
- {config.CUSTOM_NOTES}
- Use Chart.js from CDN for all charts
- Write the final output to {output_file}
- Do not overwrite any existing files in reports/
- Do not ask questions — just read the data and generate the file
"""


async def main():
    os.makedirs(client_folder, exist_ok=True)
    print(f"Client:  {config.CLIENT_NAME}")
    print(f"Data:    {config.DATA_FOLDER}/")
    print(f"Output:  {output_file}")
    print("\nStarting agent... this may take a minute.\n")

    async for message in query(
        prompt=PROMPT,
        options=ClaudeAgentOptions(
            cwd="/Users/devan/Desktop/Claude Code Agents/Shopify Product Data Analysis",
            allowed_tools=["Read", "Glob", "Write", "Bash"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, ResultMessage):
            print("\nDone!")
            print(f"Report saved to: {output_file}")
            print("\nPushing to GitHub...")
            try:
                repo_dir = "/Users/devan/Desktop/Claude Code Agents/Shopify Product Data Analysis"
                # Push full project (private repo — all files)
                subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True)
                subprocess.run(["git", "commit", "-m", f"Add report: {output_file}"], cwd=repo_dir, check=True)
                subprocess.run(["git", "push", "full-project", "main"], cwd=repo_dir, check=True)
                print("Full project repo updated.")

                # Deploy to public GitHub Pages repo (origin remote)
                subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)
                report_filename = os.path.basename(output_file)
                client_url = config.CLIENT_NAME.replace(" ", "%20")
                print(f"Public repo updated.")
                print(f"Live URL: https://devansh-intc.github.io/logox-report/reports/{client_url}/{report_filename}")
            except subprocess.CalledProcessError as e:
                print(f"GitHub push failed: {e}")


anyio.run(main)
