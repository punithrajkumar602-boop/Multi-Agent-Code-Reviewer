"""
Test Runner Agent: runs the existing pytest suite (if present locally)
and reports pass/fail results. When reviewing a remote PR diff (no local
checkout), it instead asks the LLM to assess test coverage of the change
and flag missing tests.
"""
import subprocess
import os

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

from src.config import GROQ_API_KEY, LLM_MODEL, MAX_FILE_CHARS

COVERAGE_PROMPT = ChatPromptTemplate.from_template("""
You are a test-coverage reviewer. Look at this code change and assess whether it appears
to be adequately covered by tests, based on what's visible in the diff itself.

File: {filename}
Code:
{code}

Answer in 2-3 sentences: does this change look like it needs new/updated tests, and if so,
what should be tested? If the file itself is a test file, just say "This is a test file."
""")


def _get_llm():
    return ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL, temperature=0)


def run_local_tests(test_dir: str = "tests") -> dict:
    """
    Runs pytest on a local test directory (if it exists) and returns
    the pass/fail summary. Use this when reviewing a local checkout.
    """
    if not os.path.isdir(test_dir):
        return {"agent": "test_runner", "ran_tests": False, "summary": f"No '{test_dir}' directory found to run."}

    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", test_dir, "-v", "--tb=short"],
            capture_output=True, text=True, timeout=60,
        )
        passed = result.returncode == 0
        summary = result.stdout[-3000:]  # last part of output, most relevant
        return {"agent": "test_runner", "ran_tests": True, "passed": passed, "summary": summary}
    except Exception as e:
        return {"agent": "test_runner", "ran_tests": False, "summary": f"Could not run tests: {e}"}


def assess_test_coverage(filename: str, code: str) -> dict:
    """
    Used for remote PR review where there's no local checkout to run tests
    against -- asks the LLM to assess whether the diff looks adequately tested.
    """
    truncated_code = code[:MAX_FILE_CHARS]
    try:
        llm = _get_llm()
        chain = COVERAGE_PROMPT | llm
        result = chain.invoke({"filename": filename, "code": truncated_code})
        findings = result.content.strip()
    except Exception as e:
        findings = f"Test coverage assessment unavailable right now ({e})."

    return {"agent": "test_runner", "filename": filename, "findings": findings}
