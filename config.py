# ============================================================
# CONFIG — Edit this file each time you run the agent
# for a new client or brand.
# ============================================================

# Name of the client or brand (used in the report filename and title)
CLIENT_NAME = "Harmony House Foods"

# Folder containing the CSV files for this client
# CSV files should be named by year, e.g. 2021.csv, 2022.csv, etc.
DATA_FOLDER = "data/Harmony House Foods"

# IDs to exclude from analysis (non-product rows)
EXCLUDED_IDS = ["0", "99900", "2084", "1876", "1876-2", "7998"]

# Any extra instructions or tweaks for this specific client
# Leave as empty string "" if no special requirements
CUSTOM_NOTES = """
- Exclude rows where Amount <= 0
- The data covers years 2021 through 2025
"""
