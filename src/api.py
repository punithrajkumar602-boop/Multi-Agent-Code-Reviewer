"""
FastAPI wrapper around the multi-agent code review orchestrator.
Lets you trigger a review via HTTP (e.g. from a CI webhook) instead of
only through the CLI/demo script.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.orchestrator import review_pr, review_files

app = FastAPI(title="Multi-Agent Code Reviewer API")


class PRReviewRequest(BaseModel):
    repo_full_name: str   # e.g. "octocat/Hello-World"
    pr_number: int
    post_comment: bool = False


class FileReviewRequest(BaseModel):
    files: list[dict]     # [{"filename": "app.py", "code": "..."}]


@app.get("/")
def root():
    return {"status": "ok", "message": "Multi-Agent Code Reviewer API is running."}


@app.post("/review/pr")
def review_pull_request(request: PRReviewRequest):
    try:
        result = review_pr(request.repo_full_name, request.pr_number, request.post_comment)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review/files")
def review_local_files(request: FileReviewRequest):
    try:
        result = review_files(request.files)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
