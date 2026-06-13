"""
Configuration settings for the AI Agent pipeline.
Modify these values to customize model, behavior, and output.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
#  Groq API Configuration (Online)
# ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Use a faster Groq model that is supported by the configured API key.
# If you want higher quality later, choose a larger model from the Groq API.
MODEL_NAME = "llama-3.1-8b-instant"  # Smaller/faster and valid on Groq
MODEL_TEMPERATURE = 0.4         # Slightly higher creativity with low latency

# Stage-specific (faster) model choices to reduce latency.
# Use Groq model IDs returned by your Groq account (see groq.models.list()).
PLAN_MODEL = "groq/compound-mini"        # very fast for short planning text
DEV_MODEL = "llama-3.1-8b-instant"      # balance of quality and speed for code
TEST_MODEL = "groq/compound-mini"        # fast for test-generation summaries
REVIEW_MODEL = "llama-3.1-8b-instant"   # use same as developer for review

# ──────────────────────────────────────────────
#  Agent Behavior
# ──────────────────────────────────────────────
MAX_RETRIES = 2                 # Number of retry attempts if an agent call fails
VERBOSE_OUTPUT = True           # Show full agent responses in the console
SAVE_OUTPUT_TO_FILE = True      # Save the final generated code to a file
OUTPUT_DIR = "output"           # Directory to save generated artifacts

# ──────────────────────────────────────────────
#  Pipeline Stages (enable/disable)
# ──────────────────────────────────────────────
ENABLE_PLANNING = True
ENABLE_DEVELOPMENT = True
ENABLE_TESTING = True
ENABLE_REVIEW = True
