# ResearchMind — Multi-Agent AI Research System

A 4-agent AI pipeline that researches any topic end-to-end: searching the web, scraping the most relevant source, drafting a structured report, and critiquing its own output — all orchestrated with LangChain + LangGraph and served through a Streamlit UI.

## How it works

The pipeline runs four specialized agents/chains in sequence, each one feeding the next:

1. **Search Agent** — Uses the Tavily API to find recent, reliable information on the topic (titles, URLs, snippets).
2. **Reader Agent** — Picks the most relevant URL from the search results and scrapes it for deeper content using BeautifulSoup.
3. **Writer Chain** — Synthesizes the search results and scraped content into a structured report (Introduction, Key Findings, Conclusion, Sources).
4. **Critic Chain** — Reviews the report and returns a score out of 10, strengths, areas to improve, and a one-line verdict.

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

- **LangChain / LangGraph** — agent orchestration (`create_agent`) and chains
- **Groq** — LLM inference (`llama-3.3-70b-versatile`)
- **Tavily** — web search API
- **BeautifulSoup4 + Requests** — web scraping
- **Streamlit** — UI

## Project structure

```
.
├── app.py          # Streamlit UI — runs the pipeline interactively
├── pipeline.py      # CLI entry point — runs the pipeline end-to-end in the terminal
├── agents.py        # Agent + chain definitions (search, reader, writer, critic)
├── tools.py         # Tool implementations (web_search, scrape_url)
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

## Example output

Enter a topic like `"Quantum computing breakthroughs in 2025"` and the pipeline will return a structured research report with sources, plus a critic review scoring the report's quality — downloadable as a `.md` file.

## Known limitations / roadmap

- Reader agent scrapes a single URL; multi-URL synthesis would improve depth
- No rewrite loop yet — low critic scores don't currently trigger a revision pass
- Scraping can fail silently on JS-heavy or paywalled sites

## License

MIT