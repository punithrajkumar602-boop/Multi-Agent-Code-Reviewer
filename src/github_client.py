"""
Fetches PR diffs and file contents from GitHub using PyGithub.
Also supports reviewing local files directly (no GitHub needed) so the
project can be demoed and tested without needing a live PR.
"""
from github import Github, Auth
from src.config import GITHUB_TOKEN


def _get_client():
    if GITHUB_TOKEN:
        return Github(auth=Auth.Token(GITHUB_TOKEN))
    return Github()  # unauthenticated, works for public repos with low rate limits


def fetch_pr_files(repo_full_name: str, pr_number: int) -> list:
    """
    Fetches the list of changed files in a PR.
    Returns a list of dicts: {filename, patch, status, additions, deletions}
    """
    client = _get_client()
    repo = client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    files = []
    for f in pr.get_files():
        files.append({
            "filename": f.filename,
            "patch": f.patch or "",
            "status": f.status,
            "additions": f.additions,
            "deletions": f.deletions,
        })
    return files


def post_pr_comment(repo_full_name: str, pr_number: int, comment_body: str) -> str:
    """Posts a consolidated review comment to the PR. Requires a valid GITHUB_TOKEN."""
    if not GITHUB_TOKEN:
        return "Skipped: no GITHUB_TOKEN configured, cannot post comments to GitHub."

    client = _get_client()
    repo = client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(comment_body)
    return f"Comment posted to {repo_full_name}#{pr_number}"
