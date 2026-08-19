"""
Bug Finder Agent: reviews a code diff/file for logic issues, missing
null/edge-case checks, off-by-one errors, and other correctness concerns.
"""
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

from src.config import GROQ_API_KEY, LLM_MODEL, MAX_FILE_CHARS

BUG_PROMPT = ChatPromptTemplate.from_template("""
You are a bug-finding code reviewer. Review the following code changes for potential bugs:
logic errors, missing null/edge-case handling, off-by-one errors, unhandled exceptions,
and race conditions.

File: {filename}
Code:
{code}

List up to 5 specific potential bugs (with line context where possible), ranked by severity
(High/Medium/Low). If there are no significant issues, say "No significant bugs found."
Keep your response concise -- bullet points only, no preamble.
""")


def _get_llm():
    return ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL, temperature=0)


def review_bugs(filename: str, code: str) -> dict:
    """
    Reviews a single file's code for potential bugs.
    Falls back to a neutral message if the LLM call fails.
    """
    truncated_code = code[:MAX_FILE_CHARS]
    try:
        llm = _get_llm()
        chain = BUG_PROMPT | llm
        result = chain.invoke({"filename": filename, "code": truncated_code})
        findings = result.content.strip()
    except Exception as e:
        findings = f"Bug review unavailable right now ({e})."

    return {"agent": "bug_finder", "filename": filename, "findings": findings}
