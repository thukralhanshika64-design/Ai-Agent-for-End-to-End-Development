# AI Agent for End-to-End App Development

A **multi-agent AI system** that turns a natural-language app idea into production-ready code — all running locally on your machine with **no paid APIs**.

```
┌─────────────────────────────────────────────────────────┐
│                    🚀 App Idea                          │
│            "Build a todo REST API..."                   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   📋 Planner Agent    │  → Development plan
         │  (Software Architect) │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   💻 Developer Agent  │  → Application code
         │   (Python Developer)  │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   🧪 Tester Agent     │  → Test report
         │    (QA Engineer)      │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   🔍 Reviewer Agent   │  → Final improved code
         │  (Senior Reviewer)    │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │    ✅ Final Output    │
         │  (Saved to /output)   │
         └───────────────────────┘
```

---

## Prerequisites

1. **Get a Groq API Key** — Sign up free at [console.groq.com](https://console.groq.com)
2. **Set the API key as an environment variable:**
   ```bash
   # On Windows (PowerShell):
   $env:GROQ_API_KEY = "your-api-key-here"
   
   # On macOS/Linux (Bash):
   export GROQ_API_KEY="your-api-key-here"
   
   # Or create a .env file in the project root:
   GROQ_API_KEY=your-api-key-here
   ```
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the Web Dashboard (recommended)
1. Ensure `GROQ_API_KEY` is set (see Prerequisites).
2. Start the FastAPI dashboard:
```bash
uvicorn dashboard:app --host 0.0.0.0 --port 8000 --reload
```
3. Open your browser at: http://localhost:8000

The dashboard provides a rich UI with real-time streaming of each agent via Server-Sent Events (SSE).

### CLI Mode (optional)
You can still run the pipeline from the command line:
```bash
python main.py "Build a simple REST API for a todo app using FastAPI"
```

## Project Structure

```
📁 AI Agent for End-to-End App Development/
├── main.py            # Entry point — CLI interface
├── orchestrator.py    # Pipeline controller (runs all stages)
├── agents.py          # Specialized agent definitions
├── llm_engine.py      # LLM wrapper with retry logic
├── config.py          # All configurable settings
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── output/            # Generated artifacts (auto-created)
    └── run_YYYYMMDD_HHMMSS/
        ├── 01_plan.md
        ├── 02_code.py
        ├── 03_test_report.md
        └── 04_final_code.py
```

## Configuration

Edit `config.py` to customize:

| Setting               | Default                         | Description                       |
|-----------------------|---------------------------------|-----------------------------------|
| `MODEL_NAME`          | `"llama-3.1-8b-instant"`       | Ollama/Groq model to use          |
| `MODEL_TEMPERATURE`   | `0.4`                           | Creativity level (0.0–1.0)        |
| `MAX_RETRIES`         | `2`                             | Retry attempts per agent call     |
| `SAVE_OUTPUT_TO_FILE` | `True`                          | Save artifacts to disk            |
| `OUTPUT_DIR`          | `"output"`                      | Where to save artifacts           |
| `ENABLE_PLANNING`     | `True`                          | Enable/disable planning stage     |
| `ENABLE_DEVELOPMENT`  | `True`                          | Enable/disable development stage  |
| `ENABLE_TESTING`      | `True`                          | Enable/disable testing stage      |
| `ENABLE_REVIEW`       | `True`                          | Enable/disable review stage       |

## How It Works

1. **Planner Agent** → Acts as a senior software architect. Breaks down your idea into features, tech stack, architecture, and a step-by-step implementation plan.

2. **Developer Agent** → Takes the plan and writes clean, modular, production-ready Python code with type hints, error handling, and proper structure.

3. **Tester Agent** → Analyzes the code for bugs, edge cases, security concerns, and writes pytest test cases.

4. **Reviewer Agent** → Takes the code AND the test report, fixes identified issues, and outputs the final improved version.

## Tech Stack

- **[Ollama](https://ollama.com)** — Run open-source LLMs locally
- **[LangChain](https://langchain.com)** — LLM orchestration framework
- **[Rich](https://rich.readthedocs.io)** — Beautiful terminal output

## License

MIT — Use freely for learning, projects, and production.
