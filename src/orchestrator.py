"""
Orchestrator: runs the Style, Bug Finder, and Test Runner agents on
each changed file in a PR (or a locally provided set of files), then
consolidates their findings into one review report.
"""
from src.agents.style_agent import review_style
from src.agents.bug_finder_agent import review_bugs
from src.agents.test_runner_agent import assess_test_coverage, run_local_tests
from src.github_client import fetch_pr_files, post_pr_comment


def review_files(files: list) -> dict:
    """
    Runs all three agents against a list of {filename, code} dicts.
    Returns per-file findings from each agent plus a consolidated summary.
    """
    per_file_results = []

    for f in files:
        filename = f["filename"]
        code = f.get("patch") or f.get("code") or ""

        style_result = review_style(filename, code)
        bug_result = review_bugs(filename, code)
        test_result = assess_test_coverage(filename, code)

        per_file_results.append({
            "filename": filename,
            "style": style_result["findings"],
            "bugs": bug_result["findings"],
            "test_coverage": test_result["findings"],
        })

    return {
        "files_reviewed": len(files),
        "per_file_results": per_file_results,
        "consolidated_comment": consolidate_feedback(per_file_results),
    }


def consolidate_feedback(per_file_results: list) -> str:
    """Merges all agents' outputs into one readable review comment."""
    if not per_file_results:
        return "No files were reviewed."

    lines = ["## 🤖 Automated Multi-Agent Code Review\n"]
    for r in per_file_results:
        lines.append(f"### 📄 `{r['filename']}`\n")
        lines.append(f"**🎨 Style Agent:**\n{r['style']}\n")
        lines.append(f"**🐛 Bug Finder Agent:**\n{r['bugs']}\n")
        lines.append(f"**✅ Test Coverage Agent:**\n{r['test_coverage']}\n")
        lines.append("---\n")

    return "\n".join(lines)


def review_pr(repo_full_name: str, pr_number: int, post_comment: bool = False) -> dict:
    """
    Fetches a GitHub PR's changed files and runs the full multi-agent
    review pipeline on them. Optionally posts the consolidated result
    back as a PR comment.
    """
    files = fetch_pr_files(repo_full_name, pr_number)
    result = review_files(files)

    if post_comment:
        post_status = post_pr_comment(repo_full_name, pr_number, result["consolidated_comment"])
        result["post_status"] = post_status

    # Also run the local test suite if one exists in this environment
    result["local_test_run"] = run_local_tests()

    return result
