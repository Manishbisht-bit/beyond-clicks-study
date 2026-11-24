"""Vercel Serverless Function entrypoint with ASGI path restoration."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app as _app


async def app(scope, receive, send):
    if scope.get("type") == "http":
        headers = dict(scope.get("headers", []))
        matched = headers.get(b"x-matched-path")
        if matched:
            scope["path"] = matched.decode("utf-8")
        elif scope.get("path", "").startswith("/api/index.py"):
            new_path = scope["path"][len("/api/index.py"):]
            scope["path"] = new_path if new_path else "/"
        elif scope.get("path", "").startswith("/api/index"):
            new_path = scope["path"][len("/api/index"):]
            scope["path"] = new_path if new_path else "/"
        elif scope.get("path", "") == "/api" or scope.get("path", "") == "/api/":
            scope["path"] = "/"
    await _app(scope, receive, send)
