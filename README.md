# Dashboard Agent — How to Use

## Your entire job is 2 steps:

---

### Step 1 — Attach the CSV files in the chat
Click the paperclip/attach button in the Claude Code chat and upload the client's CSV files directly.

CSV files should be named by year: `2021.csv`, `2022.csv`, etc.

---

### Step 2 — Tell Claude in the chat
Just say something like:

> "New client: Brand X. Exclude IDs: 0, 99900. Notes: data covers 2022–2024 only."

Claude will:
- Create the client folder under `data/`
- Save the CSV files into it
- Update `config.py`
- Run the agent
- Tell you when the report is ready in `reports/`

---

## That's it. No terminal. No editing files. Just attach and chat.

---

## Folder Structure
```
├── CLAUDE.md           ← project documentation
├── README.md           ← this file
├── .env                ← API keys (never share)
├── .claude/
│   └── settings.json
├── agent.py            ← the agent (never touch)
├── config.py           ← auto-updated by Claude
├── data/
│   └── [Client Name]/  ← created automatically per client
└── reports/            ← finished dashboards appear here
```
