"""
Minimal routes for debugging
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
def hello():
    return {"hello": "world"}
