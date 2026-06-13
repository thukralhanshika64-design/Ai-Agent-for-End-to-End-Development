"""
Specialized AI Agents — Each agent has a focused role in the
software development lifecycle, mirroring a real engineering team.

Agents:
    • Planner Agent   → Senior Software Architect
    • Developer Agent  → Python Developer
    • Tester Agent     → QA / Software Tester
    • Reviewer Agent   → Senior Code Reviewer
"""

from llm_engine import run_llm, stream_llm, astream_llm
from config import PLAN_MODEL, DEV_MODEL, TEST_MODEL, REVIEW_MODEL


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PLANNER AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def planner_agent(app_idea: str, stream: bool = False, astream: bool = False):
    """
    Acts as a senior software architect.
    Breaks down an app idea into a structured development plan
    including features, tech stack, and implementation steps.

    Args:
        app_idea: A natural-language description of the app to build.

    Returns:
        A detailed development plan as a string.
    """
    prompt = f"""
You are a senior software architect with 15+ years of experience.

A client has asked you to plan the following application:
"{app_idea}"

Provide a comprehensive development plan that includes:

1. **Project Overview** — A brief summary of what the application does.
2. **Core Features** — A numbered list of features to implement.
3. **Tech Stack** — Languages, frameworks, libraries, and tools to use.
4. **Architecture** — High-level architecture (e.g., MVC, microservices, monolith).
5. **Data Model** — Key entities and their relationships.
6. **Step-by-Step Implementation Plan** — Ordered phases with clear deliverables.
7. **Potential Challenges** — Risks and how to mitigate them.

Be specific and actionable. This plan will be handed directly to a developer.
"""
    if astream:
        return astream_llm(prompt, model_name=PLAN_MODEL)
    if stream:
        return stream_llm(prompt, model_name=PLAN_MODEL)
    return run_llm(prompt, model_name=PLAN_MODEL)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DEVELOPER AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def developer_agent(plan: str, stream: bool = False, astream: bool = False):
    """
    Acts as an experienced Python developer.
    Writes clean, modular, production-ready code based on the plan.

    Args:
        plan: The development plan from the planner agent.

    Returns:
        Complete Python source code as a string.
    """
    prompt = f"""
You are an expert Python developer who writes clean, production-ready code.

Based on the following development plan, write the complete application code.

--- DEVELOPMENT PLAN ---
{plan}
--- END PLAN ---

Requirements:
1. Write clean, modular, well-structured Python code.
2. Use proper type hints and docstrings.
3. Include necessary imports at the top.
4. Add inline comments for complex logic.
5. Follow PEP 8 style guidelines.
6. Make the code production-ready — include error handling where appropriate.
7. If the plan specifies a web framework, include route definitions and models.
8. Include a `if __name__ == "__main__":` block for the entry point.

Output ONLY the Python code. Do not add explanations outside code blocks.
"""
    if astream:
        return astream_llm(prompt, model_name=DEV_MODEL)
    if stream:
        return stream_llm(prompt, model_name=DEV_MODEL)
    return run_llm(prompt, model_name=DEV_MODEL)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TESTER AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tester_agent(code: str, stream: bool = False, astream: bool = False):
    """
    Acts as a thorough software tester / QA engineer.
    Analyzes code for bugs, edge cases, and improvements.

    Args:
        code: The source code to analyze.

    Returns:
        A test report with findings and suggestions.
    """
    prompt = f"""
You are a meticulous software tester and QA engineer.

Analyze the following code carefully:

```python
{code}
```

Provide a detailed test report covering:

1. **Bug Report** — List any bugs or logical errors found. For each bug:
   - Describe the issue
   - Point to the specific code section
   - Suggest a fix

2. **Edge Cases** — Identify edge cases that are not handled:
   - Empty inputs
   - Invalid data types
   - Boundary conditions
   - Concurrent access issues (if applicable)

3. **Security Concerns** — Flag any security vulnerabilities:
   - Input validation gaps
   - SQL injection risks
   - Authentication / authorization issues

4. **Test Cases** — Write 5-10 test cases (using pytest) that should be run:
   - Include both positive and negative tests
   - Cover the critical paths

5. **Improvements** — Suggest code improvements for reliability.

Be specific with line references and code snippets in your suggestions.
"""
    if astream:
        return astream_llm(prompt, model_name=TEST_MODEL)
    if stream:
        return stream_llm(prompt, model_name=TEST_MODEL)
    return run_llm(prompt, model_name=TEST_MODEL)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  REVIEWER AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def reviewer_agent(code: str, test_report: str, stream: bool = False, astream: bool = False):
    """
    Acts as a senior code reviewer.
    Improves code quality, readability, and performance based on
    both the original code and the tester's findings.

    Args:
        code: The original source code.
        test_report: The test report from the tester agent.

    Returns:
        Improved, final version of the source code.
    """
    prompt = f"""
You are a senior code reviewer with deep expertise in Python best practices.

Here is the code to review and improve:

```python
{code}
```

And here is the QA test report with findings:

--- TEST REPORT ---
{test_report}
--- END REPORT ---

Your task:
1. Fix all bugs identified in the test report.
2. Handle the edge cases mentioned.
3. Address the security concerns raised.
4. Improve code readability and structure.
5. Optimize performance where possible.
6. Ensure proper error handling throughout.
7. Add or improve type hints and docstrings.
8. Follow Python best practices and PEP 8.

Output the FINAL, IMPROVED version of the complete Python code.
Include brief comments explaining significant changes you made.
Output ONLY the Python code.
"""
    if stream:
        return stream_llm(prompt, model_name=REVIEW_MODEL)
    return run_llm(prompt, model_name=REVIEW_MODEL)
