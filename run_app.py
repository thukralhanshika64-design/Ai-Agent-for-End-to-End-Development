#!/usr/bin/env python
"""
Launcher script to run the AI Agent with proper asyncio handling for Windows
"""
import os
import sys

# Do not hardcode the Groq API key here.
# The key should be provided in .env or as an environment variable.
if not os.getenv("GROQ_API_KEY"):
    print("ERROR: GROQ_API_KEY is not set. Add it to .env or your environment variables.")
    sys.exit(1)

# If no argument provided, add a default one
if len(sys.argv) == 1:
    sys.argv.append("Build a simple to-do REST API with Flask")

# Import and run main
from main import main

if __name__ == "__main__":
    main()
