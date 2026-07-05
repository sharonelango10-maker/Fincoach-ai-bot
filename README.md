# FinCoach AI Bot — A Personal Finance Coach Bot

##  Overview

**FinCoach** is a conversational AI agent built using **IBM's Bob**, designed to act as a friendly personal finance assistant. It helps users understand their monthly finances by analyzing income and expenses, identifying overspending, and offering simple, practical, encouraging savings advice — all through natural, turn-by-turn conversation.

This project was built as part of the **Edunet Foundation IBM SkillsBuild Internship**.

---

##  Purpose

Many people find budgeting tools intimidating or overly technical. FinCoach AI aims to make financial self-awareness approachable, almost like chatting with a supportive friend who's good with money, rather than filling out a spreadsheet or talking to a strict accountant.

---

##  Development Journey

FinCoach was built iteratively, starting simple and layering in complexity once each version was tested and working.

### Version 1 — Initial Concept (Detailed)
A full-featured first draft including:
- Income and category-wise expense collection
- Analysis based on standard budgeting guidelines 
- Category breakdowns and overspending flags
- Follow-up Q&A support

### Version 2 — Simplified (Novice-Friendly)
Scaled down to the essentials for an easier first build:
- Ask for income → ask for main expenses → calculate savings → give 2–3 tips → short summary
- Prioritized getting a working bot over feature completeness

### Version 3 (final) — Interactive Chat Flow
Refined to feel like a real conversation rather than a static form:
- Bot asks one question at a time and waits for the user's reply
- Messages kept short and conversational
- Verified to work properly
  
---

##  Features Added

Once the final version of the bot was working, the following features were added **one at a time**, each tested individually before moving to the next:

| Feature | Description |
|---|---|
| **Savings Goal Tracker** | User sets a target amount + timeframe (e.g., "save ₹50,000 in 6 months"); the bot calculates required monthly savings and flags whether it's realistic. |
| **Expense Category Breakdown** | Spending shown as a percentage of income per category (Rent, Food, Transport, etc.) in a clean bullet list. |
| **Recalculate / Try Again** | Users can update specific values without restarting the entire conversation. |
| **Follow-up Q&A Mode** | Bot answers contextual questions like *"How can I save more on food?"* using numbers already discussed. |
| **Currency/Region Flexibility** | Bot asks for the user's preferred currency symbol upfront and uses it consistently throughout. |

---

##  UI/Response Styling Enhancements

Since Bob primarily shapes the bot's *response formatting* (not the chat window's visual skin), the following were added to make FinCoach's messages cleaner and more engaging to read:

| Enhancement | Description |
|---|---|
| **Structured, Visual Responses** | Headings, bullet points, and bold key figures instead of plain paragraphs. |
| **Text-Based Progress Bars** | Category breakdowns shown with block-character bars, e.g. `Rent ████████░░ 35%`. |
| **Consistent Message Structure** | Every response follows: friendly opener → bullet content → clear next step or question. |
| **Highlighted Key Numbers** | Total income, expenses, and savings percentage bolded for quick scanning. |

---

##  Full-Stack Expansion Concept (Proposed Extension)

To extend FinCoach beyond it's environment into a standalone web app:

- **Backend:** Python Flask, with routes for chat, goal calculations, and family/household profile management.
- **AI Integration:** IBM Watsonx.ai with Granite models, API key secured via a `.env` file (never hardcoded).
- **Frontend:** Bootstrap-based responsive UI with dark mode, animations, a chat interface, a savings goal tracker widget, and a family/household budget profile section.
- **Deliverables:** Complete backend + frontend code, `requirements.txt`, and deployment instructions.

---

##  Tools & Technologies

- **IBM Bob** — AI-assisted agent builder
-  Python Flask, IBM Watsonx.ai, Bootstrap

---

##  Key Learnings

- Building iteratively (MVP → features → polish) made testing and debugging much easier than trying to build everything at once.
- A simplified first version still produces a fully functional bot — complexity can always be layered in afterward.
- Conversational UX (one question at a time, short messages) is essential for a natural chatbot feel versus a rigid form-like interaction.
- Thoughtful response formatting (bullets, bold text, emojis, progress bars) meaningfully improves perceived quality, even without a customized front-end.

---

## Author - **Sharon** **Elango**
Edunet Foundation × IBM SkillsBuild AICTE Internship Program
