#!/usr/bin/env python
"""
Launcher script to run the AI Agent with proper asyncio handling for Windows
"""
import os
import sys

# Set the API key from environment or .env file (loaded via config.py)
# The API key should be set in .env or as an environment variable

# If no argument provided, add a default one
if len(sys.argv) == 1:
    sys.argv.append("Build a simple to-do REST API with Flask")

# Import and run main
from main import main

if __name__ == "__main__":
    main()
