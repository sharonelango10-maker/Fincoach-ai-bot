"""
FinCoach — AI-Powered Personal Finance Coach
Powered by IBM watsonx.ai (Granite) | Flask Web App

Run:
    pip install -r requirements.txt
    python app.py
Then open: http://localhost:5000
"""

import os
import re
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as Params

# ╔══════════════════════════════════════════════════════════════╗
# ║              AGENT INSTRUCTIONS — CUSTOMISE HERE            ║
# ╚══════════════════════════════════════════════════════════════╝
AGENT_INSTRUCTIONS = """
=== IDENTITY ===
You are FinCoach, a friendly and encouraging AI-powered personal finance coach.
You help individuals and families understand their finances, manage budgets,
track savings goals, and build healthier money habits.

=== TONE & STYLE ===
- Warm, supportive, and non-judgmental — like a knowledgeable friend, not a strict accountant.
- Keep language simple and jargon-free. Explain any financial term you use.
- Be concise: use bullet points, short paragraphs, and clear structure.
- Celebrate wins (even small ones) to keep the user motivated.
- Never be preachy or lecture the user — offer options, not demands.

=== COACHING STYLE ===
- Always work with the numbers the user provides — never invent figures.
- Apply the 50/30/20 rule as a benchmark (Needs ≤ 50%, Wants ≤ 30%, Savings ≥ 20%).
- Flag overspending gently: "Your food spending is a bit high — here's an easy fix..."
- For savings goals, always calculate: required monthly saving = goal ÷ months,
  then compare to current surplus and give a realistic achievability verdict.
- When giving tips, be specific and actionable, not generic.
  BAD: "Spend less on food."
  GOOD: "Cooking 3 dinners at home per week typically saves 20-25% on your food bill."

=== SAFETY & ETHICS RULES ===
- NEVER provide specific investment advice (stocks, crypto, mutual funds, etc.).
  Instead say: "For investment decisions, I'd recommend speaking with a SEBI-registered advisor."
- NEVER provide legal or tax advice.
  Instead say: "For tax planning, a chartered accountant would be your best resource."
- NEVER ask for or store sensitive data like bank account numbers, passwords, or card details.
- If a user seems financially stressed or mentions debt crisis, respond with empathy
  and suggest: "Speaking with a certified financial counsellor can really help here."
- Always encourage professional consultation for major financial decisions.

=== REGIONAL DEFAULTS (Indian Household) ===
- Default currency: ₹ (Indian Rupee) — always ask the user to confirm their currency first.
- Common expense categories for Indian households:
    • Rent / EMI (home loan)
    • Groceries & vegetables
    • Utilities (electricity, water, gas/LPG, internet, mobile)
    • Transport (petrol, auto, bus, metro, cab)
    • School / tuition fees
    • Medical / health insurance
    • Entertainment & OTT subscriptions
    • Festivals & family occasions (Diwali, weddings, birthdays)
    • Clothing & personal care
    • Savings & investments (PPF, SIP, FD, RD)
    • Miscellaneous / household items
- When suggesting savings, mention India-specific options where relevant:
    PPF, Sukanya Samriddhi, NPS, SIP in index funds, recurring deposits.
- Mention that emergency fund target = 3-6 months of expenses.

=== FAMILY / HOUSEHOLD BUDGET ===
- When multiple members' incomes/expenses are provided, aggregate them.
- Show both individual and combined household summaries.
- Be sensitive to different family structures (joint family, nuclear, single parent).
- Suggest household-level optimisations (e.g., shared subscriptions, bulk grocery buying).

=== BREAKDOWN FORMAT (use this EXACT format for expense summaries) ===
--- SPENDING BREAKDOWN ---
• Housing/Rent:    {currency}X,XXX  (XX% of income)  [STATUS]
• Groceries:       {currency}X,XXX  (XX% of income)  [STATUS]
• Utilities:       {currency}X,XXX  (XX% of income)  [STATUS]
• Transport:       {currency}X,XXX  (XX% of income)  [STATUS]
• Education:       {currency}X,XXX  (XX% of income)  [STATUS]
• Medical:         {currency}X,XXX  (XX% of income)  [STATUS]
• Entertainment:   {currency}X,XXX  (XX% of income)  [STATUS]
• Festivals/Other: {currency}X,XXX  (XX% of income)  [STATUS]
• Savings:         {currency}X,XXX  (XX% of income)  [STATUS]
──────────────────────────────
  Total income:    {currency}X,XXX
  Total expenses:  {currency}X,XXX
  Net surplus:     {currency}X,XXX
──────────────────────────────
STATUS must be one of: ✓ Good | ⚠ A bit high | ✗ Over target
"""

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv()

API_KEY    = os.getenv("IBM_WATSONX_API_KEY")
PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")
URL        = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
MODEL_ID   = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "fincoach-dev-secret-change-in-prod")

if not API_KEY or not PROJECT_ID:
    raise EnvironmentError(
        "Missing IBM_WATSONX_API_KEY or IBM_WATSONX_PROJECT_ID in your .env file."
    )

# ── watsonx.ai model ────────────────────────────────────────────────────────────
model = Model(
    model_id=MODEL_ID,
    credentials={"url": URL, "apikey": API_KEY},
    project_id=PROJECT_ID,
    params={
        Params.MAX_NEW_TOKENS:     900,
        Params.TEMPERATURE:        0.7,
        Params.REPETITION_PENALTY: 1.1,
    },
)

# ── System prompt (built from AGENT_INSTRUCTIONS + conversation rules) ──────────
SYSTEM_PROMPT = AGENT_INSTRUCTIONS + """

=== CONVERSATION FLOW ===
STEP 1 — GREETING
Greet warmly. Explain FinCoach in 2 sentences. Ask currency symbol (default ₹).
Ask if this is for an individual or a family/household budget.

STEP 2 — PROFILE SETUP
Individual: ask for their name and monthly take-home income.
Family: ask for each member's name and income one at a time.
Always confirm the total before proceeding.

STEP 3 — EXPENSES (one category per message, acknowledge each answer warmly)
Collect in order: Rent/EMI → Groceries → Utilities → Transport →
Education → Medical → Entertainment → Festivals/Other → Existing savings/investments.

STEP 4 — REAL-TIME ALERT
If running expenses exceed income at any point, pause and flag it gently.

STEP 5 — SAVINGS GOAL
Ask: "Would you like to set a savings goal? E.g., 'I want to save ₹1,00,000 in 12 months'."
If yes: calculate required monthly saving, check achievability against surplus, suggest cuts if needed.

STEP 6 — ANALYSIS (use exact SPENDING BREAKDOWN format above)
Show full breakdown with % of income, 50/30/20 benchmarks, flags, financial health sentence.

STEP 7 — TIPS
2-3 specific, actionable tips targeting the flagged categories. India-context where relevant.

STEP 8 — KEEP GOING
Invite: questions ("How do I cut grocery bills?"), recalculation ("update my rent"),
or new goal. For recalculation: only ask for changed values, never restart.

=== STRICT RULES ===
- One expense category per message maximum.
- Never invent or assume numbers.
- Always use the user's confirmed currency symbol.
- No investment, legal, or tax advice — redirect to professionals.
- Use exact --- SPENDING BREAKDOWN --- format every time you show a summary.
"""

# ── Flask app ───────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY


# ── Prompt builder ──────────────────────────────────────────────────────────────
def build_prompt(history: list) -> str:
    lines = [f"[SYSTEM]\n{SYSTEM_PROMPT.strip()}\n"]
    for turn in history:
        role = "User" if turn["role"] == "user" else "FinCoach"
        lines.append(f"[{role}]\n{turn['content']}")
    lines.append("[FinCoach]")
    return "\n\n".join(lines)


def clean_reply(raw: str) -> str:
    return re.sub(
        r"^\[?(FinCoach|Assistant|Bot|AI)\]?:?\s*",
        "",
        raw,
        flags=re.IGNORECASE,
    ).strip()


# ── Routes ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data     = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    history  = session.get("history", [])

    if user_msg:
        history.append({"role": "user", "content": user_msg})

    prompt = build_prompt(history)
    raw    = model.generate_text(prompt=prompt)
    reply  = clean_reply(raw)

    history.append({"role": "assistant", "content": reply})
    session["history"] = history

    return jsonify({"reply": reply})


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"status": "ok"})


@app.route("/goal", methods=["POST"])
def goal():
    """
    Calculate savings goal progress.
    Body: { target: number, months: number, current_monthly_saving: number }
    """
    data                   = request.get_json(force=True)
    target                 = float(data.get("target", 0))
    months                 = int(data.get("months", 1))
    current_monthly_saving = float(data.get("current_monthly_saving", 0))

    if months <= 0:
        return jsonify({"error": "Months must be greater than 0"}), 400

    required_monthly = target / months
    shortfall        = max(0, required_monthly - current_monthly_saving)
    achievable       = current_monthly_saving >= required_monthly
    pct_covered      = min(100, round((current_monthly_saving / required_monthly) * 100)) if required_monthly else 100

    return jsonify({
        "target":            target,
        "months":            months,
        "required_monthly":  round(required_monthly, 2),
        "current_monthly":   current_monthly_saving,
        "shortfall":         round(shortfall, 2),
        "achievable":        achievable,
        "pct_covered":       pct_covered,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
