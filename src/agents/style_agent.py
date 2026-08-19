"""
Style Agent: reviews a code diff/file for style issues -- naming
conventions, formatting, PEP8-style concerns, and readability.
"""
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

from src.config import GROQ_API_KEY, LLM_MODEL, MAX_FILE_CHARS

STYLE_PROMPT = ChatPromptTemplate.from_template("""
You are a code style reviewer. Review the following code changes for style issues:
naming conventions, formatting consistency, line length, readability, and idiomatic patterns.

File: {filename}
Code:
{code}

List up to 5 specific style issues (with line context where possible). If there are no
significant issues, say "No significant style issues found."
Keep your response concise -- bullet points only, no preamble.
""")


def _get_llm():
    return ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL, temperature=0)


def review_style(filename: str, code: str) -> dict:
    """
    Reviews a single file's code for style issues.
    Falls back to a neutral message if the LLM call fails.
    """
    truncated_code = code[:MAX_FILE_CHARS]
    try:
        llm = _get_llm()
        chain = STYLE_PROMPT | llm
        result = chain.invoke({"filename": filename, "code": truncated_code})
        findings = result.content.strip()
    except Exception as e:
        findings = f"Style review unavailable right now ({e})."

    return {"agent": "style", "filename": filename, "findings": findings}
