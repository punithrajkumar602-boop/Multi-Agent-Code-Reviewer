"""
Unit tests for the multi-agent code reviewer's core logic:
feedback consolidation and fallback behavior when the LLM is unavailable.
Run with: pytest tests/
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.orchestrator import consolidate_feedback, review_files
from src.agents.style_agent import review_style
from src.agents.bug_finder_agent import review_bugs
from src.agents.test_runner_agent import assess_test_coverage, run_local_tests


def test_consolidate_feedback_empty():
    result = consolidate_feedback([])
    assert "No files were reviewed" in result


def test_consolidate_feedback_with_results():
    per_file = [{
        "filename": "app.py",
        "style": "No significant style issues found.",
        "bugs": "No significant bugs found.",
        "test_coverage": "This appears well covered.",
    }]
    result = consolidate_feedback(per_file)
    assert "app.py" in result
    assert "Style Agent" in result
    assert "Bug Finder Agent" in result
    assert "Test Coverage Agent" in result


def test_review_style_falls_back_gracefully_without_api_key():
    result = review_style("test.py", "def foo(): pass")
    assert result["agent"] == "style"
    assert isinstance(result["findings"], str)
    assert len(result["findings"]) > 0


def test_review_bugs_falls_back_gracefully_without_api_key():
    result = review_bugs("test.py", "def divide(a, b): return a / b")
    assert result["agent"] == "bug_finder"
    assert isinstance(result["findings"], str)


def test_assess_test_coverage_falls_back_gracefully_without_api_key():
    result = assess_test_coverage("test.py", "def foo(): pass")
    assert result["agent"] == "test_runner"
    assert isinstance(result["findings"], str)


def test_run_local_tests_reports_missing_directory():
    result = run_local_tests(test_dir="nonexistent_dir_xyz")
    assert result["ran_tests"] is False
    assert "No 'nonexistent_dir_xyz' directory" in result["summary"]


def test_review_files_returns_expected_structure():
    files = [{"filename": "sample.py", "code": "def add(a, b): return a + b"}]
    result = review_files(files)
    assert result["files_reviewed"] == 1
    assert len(result["per_file_results"]) == 1
    assert "consolidated_comment" in result
