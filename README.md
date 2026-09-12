# 🎯 Autonomous B2B Lead Intelligence & Qualification Agent

An enterprise-grade autonomous multi-agent pipeline built with **CrewAI**, **Python**, and **Gemini 3.5**. This system autonomously conducts live web intelligence on target companies, identifies operational friction and manual bottlenecks, evaluates enterprise automation fit, and outputs structured, personalized cold outreach emails.

---

## 🚀 Key Features

* **Multi-Agent Orchestration:**
  * **Lead Intelligence Analyst:** Autonomous agent utilizing DuckDuckGo Search to extract technical infrastructure, operational models, and enterprise pain points.
  * **Value Proposition Strategist:** Evaluates lead automation fit (1-10) and crafts hyper-personalized cold outreach emails based on discovered bottlenecks.
* **Structured Output Validation:** Enforces strict Pydantic schemas (`LeadEvaluation`) to guarantee deterministic JSON output.
* **Resilient API Handling:** Implements automatic quota-cooldown mechanisms and multi-model support.
* **Batch Lead Ingestion:** Automated evaluation loops processing prospects directly from `leads.csv`.

---

## 📊 Sample Intelligence Output (Shopify Evaluation)

```json
{
  "company_name": "Shopify Inc.",
  "fit_score": 9,
  "key_pain_points": [
    "Manual data mapping and transformation during enterprise migrations to Shopify Plus.",
    "App Store review backlogs and manual compliance verification.",
    "Risk underwriting and document verification friction for Shopify Payments & Capital."
  ],
  "cold_pitch_email": "Subject: Accelerating Shopify Plus Onboarding & Risk Triage with AI\n\nHi Team,\n\nWhile Shopify powers global commerce, manual bottlenecks in enterprise migrations and underwriting are likely slowing down your time-to-revenue. Solution Engineers spending hours manually mapping databases creates massive friction.\n\nWe build custom Python automation pipelines to solve this exact friction by deploying OCR-driven document verification and schema auto-mapping. Are you open to a brief chat next week?"
}
```
```bash
## 🛠️ Tech Stack
​Framework: CrewAI
​Language: Python 3.11+
​LLM Engine: Gemini 2.5 Flash
Search Integration: DuckDuckGo Search (ddgs)
​Schema Validation: Pydantic v2
​## ⚙️ Quickstart
```
