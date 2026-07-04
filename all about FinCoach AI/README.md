# FinCoach — AI Personal Finance Coach
### Powered by IBM watsonx.ai (Granite) · Flask · Chart.js · Bootstrap 5

---

## Quick Start (Local)

### 1. Clone / download the project
```
Finance Coach Bot/
├── app.py
├── requirements.txt
├── .env              ← create from .env.example
├── .env.example
└── templates/
    └── index.html
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your .env
```bash
# Copy the template
cp .env.example .env
```
Then edit `.env` and fill in your real IBM credentials:
```
IBM_WATSONX_API_KEY=your-api-key
IBM_WATSONX_PROJECT_ID=your-project-id
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
FLASK_SECRET_KEY=generate-a-long-random-string
```

**Where to find your credentials:**
- API Key: https://cloud.ibm.com → Manage → Access (IAM) → API Keys
- Project ID: https://dataplatform.cloud.ibm.com → Your Project → Manage → General

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

---

## Features

| Tab | What it does |
|---|---|
| **Chat** | Conversational AI finance coach — asks one question at a time, gives personalised advice |
| **Dashboard** | KPI cards, Bar + Doughnut charts, 50/30/20 rule visualiser, member savings badges |
| **Goal Tracker** | Enter target + timeframe → see required monthly saving, progress bar, achievability verdict |
| **Family Budget** | Add multiple members with income + 9 expense categories → combined household analysis |

### Cross-cutting features
- Dark mode toggle (persists via `data-theme` attribute)
- Fully mobile-responsive (Bootstrap 5 grid)
- Currency flexibility — user sets their symbol (₹, $, £, €, etc.)
- Overspending alerts in both chat and dashboard
- Quick-action chips after chat breakdown
- Session-only history — no financial data stored server-side

---

## Customising the Agent

Open [`app.py`](app.py) and find the `AGENT_INSTRUCTIONS` block (lines 18–90).

You can change:

| Section | What to edit |
|---|---|
| `=== IDENTITY ===` | Agent name, description |
| `=== TONE & STYLE ===` | Personality, formality, emoji use |
| `=== COACHING STYLE ===` | Budget rules (50/30/20 vs 40/30/30), tip style |
| `=== SAFETY & ETHICS RULES ===` | What advice to avoid, when to redirect to professionals |
| `=== REGIONAL DEFAULTS ===` | Change from Indian to US/UK/EU expense categories and savings products |
| `=== BREAKDOWN FORMAT ===` | Add/remove expense categories in the structured output |

---

## API Routes

| Method | Route | Body | Returns |
|---|---|---|---|
| `GET` | `/` | — | Chat UI (HTML) |
| `POST` | `/chat` | `{ message: string }` | `{ reply: string }` |
| `POST` | `/reset` | — | `{ status: "ok" }` |
| `POST` | `/goal` | `{ target, months, current_monthly_saving }` | Goal plan JSON |
| `POST` | `/dashboard` | `{ currency, members: [{name, income, expenses}] }` | Dashboard data JSON |

---

## Production Deployment

### Option A — Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Option B — IBM Code Engine / Cloud Foundry
1. Add `gunicorn` to `requirements.txt`
2. Create a `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Set environment variables in the platform dashboard (never commit `.env`)
4. Deploy via `ibmcloud cf push` or Code Engine CLI

### Option C — Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```
```bash
docker build -t fincoach .
docker run -p 5000:5000 --env-file .env fincoach
```

---

## Security Notes

- `.env` is listed in `.gitignore` — never commit it
- `FLASK_SECRET_KEY` must be a long random string in production
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- Chat history is stored in the Flask session (signed cookie) — cleared on page load / reset
- No financial data is written to any database

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Missing IBM_WATSONX_API_KEY` | Check your `.env` file exists and has the correct key |
| `Could not find a version that satisfies ibm-watsonx-ai` | You're on Python 3.9 — use `ibm-watson-machine-learning` (already in requirements.txt) |
| IDE squiggles on imports | Select the correct Python interpreter in VS Code (`Ctrl+Shift+P` → Python: Select Interpreter) |
| Blank dashboard | Add members in the Family Budget tab first, then click "Analyse Household Budget" |
| Model responds slowly | Switch to `ibm/granite-3-8b-instruct` in `.env` for fastest responses |
