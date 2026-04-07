"""
server/main.py — uvicorn entrypoint for the OpenEnv Data Cleaning server.
The Dockerfile runs: uvicorn server.main:app
This module simply re-exports `app` from server/app.py.
"""

from server.app import app  # noqa: F401  re-export for uvicorn

__all__ = ["app"]
