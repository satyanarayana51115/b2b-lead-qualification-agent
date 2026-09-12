import os
import time
import csv
import json
from pathlib import Path
from dotenv import load_dotenv

import litellm
litellm.drop_params = True

from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from ddgs import DDGS
from pydantic import BaseModel, Field

# 1. ఎన్విరాన్‌మెంట్ వేరియబుల్స్
load_dotenv()

# 2. LLM కాన్ఫిగరేషన్ (నిన్న రాత్రి సక్సెస్ అయిన మోడల్)
gemini_llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)
# mistral_llm = LLM(
#     model="openai/mistral-small-latest",
#     base_url="https://api.mistral.ai/v1",
#     api_key=os.getenv("MISTRAL_API_KEY"),
#     temperature=0.5,
#     extra_body={"cache_prompt": False}
# )

# 3. స్ట్రక్చర్డ్ అవుట్‌పుట్ స్కీమా
class LeadEvaluation(BaseModel):
    company_name: str
    fit_score: int = Field(description="Score between 1 to 10 based on automation fit")
    key_pain_points: list[str] = Field(description="Identified operational bottlenecks")
    cold_pitch_email: str = Field(description="Direct, personalized cold outreach email")

# 4. వెబ్ సెర్చ్ టూల్
@tool("Web Research Tool")
def search_web(query: str) -> str:
    """Online web search for recent company information and business challenges."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    return str(results)

# 5. ఏజెంట్ల నిర్మాణం
research_analyst = Agent(
    role="Lead Intelligence Analyst",
    goal="Extract core business focus, operational stack, and pain points for {company_domain}",
    backstory="Specialized B2B research analyst who spots manual bottlenecks and operations issues.",
    tools=[search_web],
    llm=gemini_llm,
    verbose=True
)

outreach_strategist = Agent(
    role="B2B Value Proposition Strategist",
    goal="Evaluate automation fit and write a high-converting cold email for {company_domain}",
    backstory="Expert strategist crafting targeted pitches highlighting AI and Python automation ROI.",
    llm=gemini_llm,
    verbose=True
)

# 6. టాస్క్‌ల డిఫినిషన్
research_task = Task(
    description="Research the business operations for {company_name} at domain '{company_domain}'. Identify manual workflow challenges.",
    expected_output="A bullet-point summary of business operations and potential automation targets.",
    agent=research_analyst
)

outreach_task = Task(
    description="Based on the research, evaluate lead fit and produce structured output matching LeadEvaluation schema.",
    expected_output="Structured JSON matching the LeadEvaluation model.",
    output_pydantic=LeadEvaluation,
    agent=outreach_strategist
)

lead_crew = Crew(
    agents=[research_analyst, outreach_strategist],
    tasks=[research_task, outreach_task],
    process=Process.sequential
)

# 7. బ్యాచ్ ప్రాసెసింగ్ మరియు ఫైల్ సేవింగ్ ఫంక్షన్
def process_leads_pipeline(csv_path: str = "leads.csv"):
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
        
    print(f"\n[INFO] Found {len(leads)} leads to process.\n")
    
    for idx, lead in enumerate(leads, start=1):
        name = lead["company_name"]
        domain = lead["domain"]
        
        print(f"\n==========================================")
        print(f"[{idx}/{len(leads)}] Processing: {name} ({domain})")
        print(f"==========================================")
        
        try:
            result = lead_crew.kickoff(inputs={"company_name": name, "company_domain": domain})
            
            # రిపోర్ట్‌లను ఫైల్‌గా సేవ్ చేయడం
            file_slug = name.lower().replace(" ", "_")
            out_file = reports_dir / f"{file_slug}_report.md"
            with open(out_file, "w", encoding="utf-8") as rf:
                rf.write(f"# Lead Report: {name}\n\n")
                rf.write(result.raw)
                
            print(f"[SUCCESS] Report saved to: {out_file}")
            print("[WAIT] Waiting 25 seconds for API quota cooldown...")
            time.sleep(25)
            
        except Exception as e:
            print(f"[ERROR] Failed processing {name}: {str(e)}")

if __name__ == "__main__":
    process_leads_pipeline("leads.csv")