import os
from dotenv import load_dotenv
import uvicorn
from dashboard import app

# Load environment variables from .env when running locally
load_dotenv()

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("ERROR: GROQ_API_KEY is not set. Add it to .env or Streamlit secrets.")
    uvicorn.run(app, host="0.0.0.0", port=8501)
