# ResearchMind — Multi-Agent AI Research System

ResearchMind is a multi-stage AI research pipeline that researches a topic end-to-end: searching the web, scraping multiple sources, drafting a structured report, critiquing the draft, and optionally revising it once before returning the final output.

## Live Demo : https://researchmind-ai-research-agent.streamlit.app/


## How it works

The pipeline now runs through a shared orchestration layer so both the CLI and Streamlit app use the same logic:

1. **Search** — Uses Tavily to gather recent sources.
2. **Multi-source reader** — Scrapes the top sources in parallel with retry and timeout protection.
3. **Writer** — Synthesizes retrieved evidence into a structured report.
4. **Critic** — Scores the draft and points out weaknesses.
5. **Revision loop** — If the score is below the configured threshold, the report is revised once using the critic feedback.

```
Topic
  │
  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Search Agent │────▶│ Reader Agent │────▶│ Writer Chain │────▶│ Critic Chain │
│ (Tavily API) │     │ (BS4 scrape) │     │ (report gen) │     │  (review)    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
                                          Final Report (.md)
```

## Tech stack

- **LangChain** — prompt chains and optional tool agents
- **Groq** — LLM inference (`llama-3.3-70b-versatile`)
- **Tavily** — web search API
- **BeautifulSoup4 + Requests** — web scraping
- **Pydantic** — typed pipeline state
- **Tenacity** — retry handling
- **Streamlit** — UI

## Project structure

```
.
├── app.py           # Streamlit UI
├── pipeline.py      # CLI entry point
├── orchestrator.py  # Shared pipeline orchestration
├── agents.py        # Writer / critic / revision chains
├── tools.py         # Search and scraping helpers
├── models.py        # Typed pipeline state models
├── config.py        # Environment-driven settings
├── requirements.txt
└── .env.example
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/<your-username>/multiagent-research-system.git
cd multiagent-research-system
```

**2. Create a virtual environment and install dependencies**
```bash
uv venv
.venv\Scripts\activate      # Windows
uv pip install -r requirements.txt
```

**3. Set up environment variables**

Copy `.env.example` to `.env` and fill in your API keys:
```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

- Get a free Groq API key at [console.groq.com](https://console.groq.com)
- Get a free Tavily API key at [tavily.com](https://tavily.com)

## Usage

**Streamlit UI:**
```bash
streamlit run app.py
```

**CLI:**
```bash
python pipeline.py
```

## Configuration

You can tune the pipeline behavior with environment variables:

- `SEARCH_RESULTS_LIMIT`
- `SCRAPE_SOURCE_LIMIT`
- `SCRAPE_CHAR_LIMIT`
- `CRITIC_PASS_SCORE`
- `MAX_REVISION_ROUNDS`
- `GROQ_MODEL`

## Known limitations / roadmap

- JS-heavy or paywalled pages may still return weak content
- Source ranking is still based on Tavily order rather than a dedicated ranking model
- There are not yet automated tests or persistent run history

## License

MIT
