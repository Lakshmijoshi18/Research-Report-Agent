# 🔎 R²A — Research & Report Agent

An autonomous AI agent that takes any topic, researches it live on the web, and generates a clean, structured report in seconds — built as a hands-on project to learn agentic AI architecture (plan → act → observe → synthesize).

**Live demo:** https://research-report-agent-tt45yk7byvy9dytsd8vupg.streamlit.app

## What it does

Instead of just asking an LLM a question (which relies only on its training data), this agent:
1. **Plans** — breaks your topic into 3-4 focused sub-questions
2. **Searches** — looks up each sub-question on the live web
3. **Fetches** — reads the actual article content behind each result, not just previews
4. **Synthesizes** — merges everything into coherent findings
5. **Reports** — writes a final, clean, markdown-formatted report

All of this happens automatically from a single topic input.

## Architecture

```
User Topic
   │
   ▼
Planner (Gemini) ──► generates sub-questions
   │
   ▼
Search Tool (DuckDuckGo) ──► live web results
   │
   ▼
Fetch Tool (requests + BeautifulSoup) ──► full article text
   │
   ▼
Synthesizer (Gemini) ──► merges findings
   │
   ▼
Report Generator (Gemini) ──► final structured report
   │
   ▼
Streamlit UI ──► displayed + downloadable as PDF
```

## Tech stack (100% free tools)

- **Python**
- **Google Gemini API** — reasoning, synthesis, and report writing
- **duckduckgo-search** — free live web search, no API key required
- **BeautifulSoup + requests** — full article text extraction
- **Streamlit** — web UI
- **markdown2 + xhtml2pdf** — PDF export

## Features

- Session-based memory (remembers topics researched in the same session)
- Clickable history sidebar to revisit past reports instantly
- One-click PDF download of any report
- Automatic retry handling for flaky free-API/search responses

## Run it yourself

**1. Clone this repo**
```bash
git clone https://github.com/Lakshmijoshi18/research-report-agent.git
cd research-report-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Get a free Gemini API key**
Sign up at [Google AI Studio](https://aistudio.google.com/app/apikey) and generate a key.

**4. Set your API key**

Windows:
```
set GEMINI_API_KEY=your-key-here
```
Mac/Linux:
```
export GEMINI_API_KEY="your-key-here"
```

**5. Run the app**
```bash
streamlit run streamlit_app.py
```

## Known limitations / next steps

- Currently uses free-tier search, which can occasionally rate-limit under heavy use (handled with automatic retries)
- Memory is session-based only (resets on app restart) — persistent memory across sessions is a planned improvement
- Article fetching may be blocked by sites with strict bot protection, in which case it falls back to search snippets

## Why I built this

Built as the first project in a self-directed roadmap to learn agentic AI development hands-on — covering tool-calling, multi-step orchestration, retrieval-augmented synthesis, and deploying a usable product from scratch, using only free tools throughout.
