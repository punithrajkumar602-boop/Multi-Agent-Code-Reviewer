"""
Streamlit UI for the Multi-Agent Code Reviewer.
Paste in a Python file's code and get feedback from three specialized
agents (style, bug-finder, test-coverage) run in parallel and consolidated
into one report. For a full GitHub PR review with posted comments, use the
FastAPI endpoint in src/api.py instead -- this UI is for quick, interactive
single-file review and demoing the multi-agent pipeline.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from src.orchestrator import review_files
from src.agents.test_runner_agent import run_local_tests

st.set_page_config(page_title="Multi-Agent Code Reviewer", layout="wide")
st.title("🤖 Multi-Agent Code Reviewer")
st.caption("Three specialized LLM agents — style, bug-finder, and test-coverage — "
           "independently review your code and their findings are consolidated into one report.")

with st.sidebar:
    st.header("About")
    st.write(
        "This demo runs the same `review_files()` pipeline used for GitHub PR "
        "reviews, just on code you paste in directly instead of a live PR diff."
    )
    st.write("For real GitHub PR integration (fetch diffs, post review comments), "
             "see `src/api.py` in the repo.")
    run_tests = st.checkbox("Also run this repo's local pytest suite", value=False)

filename = st.text_input("Filename (used for display and language hints)", value="my_file.py")
code = st.text_area("Paste your Python code here", height=350,
                     placeholder="def add(a, b):\n    return a + b\n")

if st.button("Run Multi-Agent Review", type="primary"):
    if not code.strip():
        st.warning("Paste some code first.")
    else:
        with st.spinner("Running style, bug-finder, and test-coverage agents..."):
            result = review_files([{"filename": filename, "code": code}])

        file_result = result["per_file_results"][0]

        tab1, tab2, tab3 = st.tabs(["🎨 Style Agent", "🐛 Bug Finder Agent", "✅ Test Coverage Agent"])
        with tab1:
            st.markdown(file_result["style"])
        with tab2:
            st.markdown(file_result["bugs"])
        with tab3:
            st.markdown(file_result["test_coverage"])

        with st.expander("📋 Full consolidated report (what would be posted to a PR)"):
            st.markdown(result["consolidated_comment"])

        if run_tests:
            st.divider()
            st.subheader("Local pytest results (this repo's own test suite)")
            with st.spinner("Running pytest..."):
                test_result = run_local_tests()
            if test_result["ran_tests"]:
                status = "✅ Passed" if test_result["passed"] else "❌ Failed"
                st.write(f"**Status:** {status}")
                st.code(test_result.get("output", ""), language="text")
            else:
                st.info(test_result.get("message", "No tests found to run."))
