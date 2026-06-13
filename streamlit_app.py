import os
import threading
import time
from dotenv import load_dotenv
import streamlit as st
import uvicorn
from dashboard import app

# Load local environment variables from .env
load_dotenv()

st.set_page_config(page_title="AI Agent Dashboard", layout="wide")

if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY is not set. Add it to .env or Streamlit secrets.")
    st.stop()


def _run_api_server() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if "api_server_started" not in st.session_state:
    threading.Thread(target=_run_api_server, daemon=True).start()
    st.session_state["api_server_started"] = True
    time.sleep(1)

st.title("AI Agent Dashboard")
st.markdown("The FastAPI dashboard is running on port 8000.")
st.markdown("[Open the dashboard in a new tab](http://localhost:8000/)")

try:
    st.components.v1.iframe("http://localhost:8000/", height=900)
except Exception as exc:
    st.warning(f"Unable to embed the dashboard in an iframe: {exc}")
    st.write("Use the link above to open the dashboard.")
