"""Vercel Serverless Function entrypoint with ASGI path restoration."""
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app as _app


async def app(scope, receive, send):
    if scope.get("type") == "http":
        qs_bytes = scope.get("query_string", b"")
        qs = qs_bytes.decode("utf-8", errors="ignore")
        if "path=" in qs:
            params = urllib.parse.parse_qs(qs, keep_blank_values=True)
            if "path" in params and params["path"]:
                real_path = params["path"][0]
                if not real_path.startswith("/"):
                    real_path = "/" + real_path
                scope["path"] = real_path
                del params["path"]
                scope["query_string"] = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
        else:
            headers = dict(scope.get("headers", []))
            matched = headers.get(b"x-matched-path")
            if matched:
                scope["path"] = matched.decode("utf-8")
            elif scope.get("path", "").startswith("/api/index"):
                new_path = scope["path"][len("/api/index"):]
                scope["path"] = new_path if new_path else "/"
    await _app(scope, receive, send)
