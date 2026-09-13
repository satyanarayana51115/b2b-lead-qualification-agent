import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

import litellm
litellm.drop_params = True
litellm.num_retries = 3

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from ddgs import DDGS

# 1. Page Configuration
st.set_page_config(
    page_title="B2B Lead Intelligence Agent",
    page_icon="🎯",
    layout="wide"
)

load_dotenv()

st.markdown("""
    <style>
    .gold-title {
        color: #D97706;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('# 🎯 Autonomous <span class="gold-title">B2B Lead Qualification</span> Engine', unsafe_allow_html=True)
st.caption("⚡ Powered by CrewAI, Gemini & Live DuckDuckGo Intelligence")
st.write("")

# 2. Sidebar Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    
    selected_model = st.selectbox(
        "LLM Model",
        ["gemini/gemini-3.6-flash", "gemini/gemini-3.5-flash"],
        index=0
    )
    st.markdown("---")
    st.info("💡 Live Multi-Agent Pipeline for Autonomous Enterprise Research")

# 3. Pydantic Output Model
class LeadEvaluation(BaseModel):
    company_name: str = Field(description="Official name of the company")
    fit_score: int = Field(description="Automation fit score from 1 to 10")
    key_pain_points: List[str] = Field(description="Top operational bottlenecks or manual pain points identified")
    cold_pitch_email: str = Field(description="Hyper-personalized cold outreach email pitch")

# 4. Search Tool
@tool("duckduckgo_search")
def ddg_search(query: str) -> str:
    """Searches DuckDuckGo for live intelligence about company operations and bottlenecks."""
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No relevant search results found."
        formatted = ""
        for r in results:
            formatted += f"Title: {r.get('title', '')}\nSnippet: {r.get('body', '')}\n\n"
        return formatted
    except Exception as e:
        return f"Search error: {str(e)}"

# 5. Pipeline Execution Function
def run_lead_qualification(target_domain: str, llm_engine: LLM):
    # Agent 1: Researcher (max_iter limits API calls to prevent 429 quota exhaustion)
    researcher = Agent(
        role="Lead Intelligence Analyst",
        goal=f"Identify key operational bottlenecks and tech stack for {target_domain}.",
        backstory="Expert business operations analyst specialized in surfacing operational friction.",
        tools=[ddg_search],
        llm=llm_engine,
        max_iter=2,
        verbose=True
    )

    # Agent 2: Strategist
    strategist = Agent(
        role="B2B Value Proposition Strategist",
        goal=f"Structure enterprise fit score and personalized outreach for {target_domain}.",
        backstory="Executive sales engineer mapping operational friction directly to AI automation solutions.",
        llm=llm_engine,
        max_iter=2,
        verbose=True
    )

    # Task 1: Research Task
    task_research = Task(
        description=f"Search for main workflows and friction points for {target_domain}.",
        expected_output="Bulleted summary of key business processes and friction points.",
        agent=researcher
    )

    # Task 2: Strategy & Scoring Task
    task_strategy = Task(
        description=f"Produce structured LeadEvaluation schema (fit score 1-10, pain points, email) for {target_domain}.",
        expected_output="Structured LeadEvaluation schema containing company name, fit score, pain points, and pitch email.",
        agent=strategist,
        output_pydantic=LeadEvaluation
    )

    crew = Crew(
        agents=[researcher, strategist],
        tasks=[task_research, task_strategy],
        process=Process.sequential,
        verbose=True
    )

    return crew.kickoff()

# 6. UI Input & Interaction
col1, col2 = st.columns([3, 1])
with col1:
    target_input = st.text_input("Enter Company Domain or Name", placeholder="e.g. zepto.com or razorpay.com")
with col2:
    st.write("")
    st.write("")
    analyze_btn = st.button("🚀 Analyze Lead", type="primary", use_container_width=True)

if analyze_btn:
    if not api_key:
        st.error("⚠️ Please provide a valid Gemini API Key in the sidebar or .env file.")
    elif not target_input.strip():
        st.warning("⚠️ Please enter a company name or domain.")
    else:
        try:
            with st.spinner(f"🔍 Agents analyzing {target_input}..."):
                llm = LLM(
                    model=selected_model,
                    api_key=api_key,
                    temperature=0.2
                )
                
                result = run_lead_qualification(target_input.strip(), llm)
                
                evaluation_data = result.pydantic if hasattr(result, "pydantic") and result.pydantic else None

                st.success("✅ Lead Analysis Complete!")
                st.markdown("---")

                if evaluation_data:
                    m_col1, m_col2 = st.columns([1, 2])
                    with m_col1:
                        st.metric("Fit Score (1-10)", f"{evaluation_data.fit_score} / 10")
                    with m_col2:
                        st.metric("Target Company", evaluation_data.company_name)

                    st.markdown("### ⚠️ Key Operational Friction Points")
                    for pt in evaluation_data.key_pain_points:
                        st.markdown(f"• **{pt}**")

                    st.markdown("### ✉️ Generated Cold Outreach Pitch")
                    st.text_area(
                        "Personalized Outreach Email",
                        value=evaluation_data.cold_pitch_email,
                        height=220
                    )
                else:
                    st.markdown("### 📋 Analysis Output")
                    st.markdown(result.raw)

        except Exception as err:
            st.error(f"Execution Error: {str(err)}")