"""
Dashboard Backend — FastAPI server with Server-Sent Events (SSE)
for real-time pipeline streaming to the web dashboard.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from agents import planner_agent, developer_agent, tester_agent, reviewer_agent
from config import (
    ENABLE_PLANNING,
    ENABLE_DEVELOPMENT,
    ENABLE_TESTING,
    ENABLE_REVIEW,
    SAVE_OUTPUT_TO_FILE,
    OUTPUT_DIR,
)

app = FastAPI(title="AI Agent Dashboard", version="1.0.0")

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# In-memory run history
run_history: list[dict] = []


def _sse_event(data: dict) -> str:
    """Format a dict as an SSE event string."""
    return f"data: {json.dumps(data)}\n\n"


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the dashboard HTML."""
    html_path = os.path.join(STATIC_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/history")
async def get_history():
    """Return past pipeline runs."""
    return {"runs": run_history}


@app.get("/api/run")
async def run_pipeline(idea: str):
    """
    Execute the multi-agent pipeline and stream progress via SSE.
    Each stage sends 'running' and 'complete' events to the client.
    """
    run_id = str(uuid.uuid4())[:8]
    started_at = datetime.now().isoformat()

    run_record = {
        "id": run_id,
        "idea": idea,
        "started_at": started_at,
        "status": "running",
        "stages": {},
    }
    run_history.insert(0, run_record)

    # Keep only last 20 runs
    while len(run_history) > 20:
        run_history.pop()

    async def _stream_agent_output(agent_callable, *args, **kwargs):
        result = agent_callable(*args, **kwargs)
        if isinstance(result, str):
            yield result
            return
        if hasattr(result, '__aiter__'):
            async for chunk in result:
                yield chunk
            return
        if hasattr(result, '__iter__'):
            for chunk in result:
                yield chunk
            return
        raise TypeError(f"Agent result is not iterable: {type(result)}")

    async def event_stream():
        plan = ""
        code = ""
        test_report = ""
        final_code = ""

        try:
            # ── Stage 1: Planning ──
            if ENABLE_PLANNING:
                yield _sse_event({
                    "type": "stage_start",
                    "stage": "planning",
                    "message": "Analyzing app idea and creating development plan...",
                })
                plan = ""
                async for chunk in _stream_agent_output(planner_agent, idea, astream=True):
                    plan += chunk
                    yield _sse_event({
                        "type": "stage_chunk",
                        "stage": "planning",
                        "chunk": chunk,
                    })
                run_record["stages"]["planning"] = plan
                yield _sse_event({
                    "type": "stage_complete",
                    "stage": "planning",
                    "output": plan,
                })
            else:
                plan = idea
                yield _sse_event({
                    "type": "stage_skip",
                    "stage": "planning",
                })

            # ── Stage 2: Development ──
            if ENABLE_DEVELOPMENT:
                yield _sse_event({
                    "type": "stage_start",
                    "stage": "development",
                    "message": "Writing production-ready code from the plan...",
                })
                code = ""
                async for chunk in _stream_agent_output(developer_agent, plan, astream=True):
                    code += chunk
                    yield _sse_event({
                        "type": "stage_chunk",
                        "stage": "development",
                        "chunk": chunk,
                    })
                run_record["stages"]["development"] = code
                yield _sse_event({
                    "type": "stage_complete",
                    "stage": "development",
                    "output": code,
                })
            else:
                yield _sse_event({
                    "type": "stage_skip",
                    "stage": "development",
                })

            # ── Stage 3: Testing ──
            if ENABLE_TESTING and code:
                yield _sse_event({
                    "type": "stage_start",
                    "stage": "testing",
                    "message": "Analyzing code for bugs, edge cases & security...",
                })
                test_report = ""
                async for chunk in _stream_agent_output(tester_agent, code, astream=True):
                    test_report += chunk
                    yield _sse_event({
                        "type": "stage_chunk",
                        "stage": "testing",
                        "chunk": chunk,
                    })
                run_record["stages"]["testing"] = test_report
                yield _sse_event({
                    "type": "stage_complete",
                    "stage": "testing",
                    "output": test_report,
                })
            else:
                yield _sse_event({
                    "type": "stage_skip",
                    "stage": "testing",
                })

            # ── Stage 4: Review ──
            if ENABLE_REVIEW and code:
                yield _sse_event({
                    "type": "stage_start",
                    "stage": "review",
                    "message": "Reviewing and improving code quality...",
                })
                final_code = ""
                async for chunk in _stream_agent_output(reviewer_agent, code, test_report, astream=True):
                    final_code += chunk
                    yield _sse_event({
                        "type": "stage_chunk",
                        "stage": "review",
                        "chunk": chunk,
                    })
                run_record["stages"]["review"] = final_code
                yield _sse_event({
                    "type": "stage_complete",
                    "stage": "review",
                    "output": final_code,
                })
            else:
                final_code = code
                yield _sse_event({
                    "type": "stage_skip",
                    "stage": "review",
                })

            # ── Save artifacts ──
            if SAVE_OUTPUT_TO_FILE:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                run_dir = os.path.join(OUTPUT_DIR, f"run_{timestamp}")
                os.makedirs(run_dir, exist_ok=True)
                if plan:
                    with open(os.path.join(run_dir, "01_plan.md"), "w", encoding="utf-8") as f:
                        f.write(plan)
                if code:
                    with open(os.path.join(run_dir, "02_code.py"), "w", encoding="utf-8") as f:
                        f.write(code)
                if test_report:
                    with open(os.path.join(run_dir, "03_test_report.md"), "w", encoding="utf-8") as f:
                        f.write(test_report)
                if final_code:
                    with open(os.path.join(run_dir, "04_final_code.py"), "w", encoding="utf-8") as f:
                        f.write(final_code)

            run_record["status"] = "complete"
            yield _sse_event({
                "type": "pipeline_complete",
                "run_id": run_id,
                "message": "Pipeline completed successfully!",
            })

        except Exception as e:
            run_record["status"] = "error"
            yield _sse_event({
                "type": "pipeline_error",
                "message": str(e),
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dashboard:app", host="127.0.0.1", port=8000, reload=True)
