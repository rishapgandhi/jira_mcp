"""Jira API client — uses only httpx + basic auth (API token)."""

import os
from base64 import b64encode
import httpx

_client: httpx.Client | None = None


def _get_config():
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    if not all([base_url, email, token]):
        raise RuntimeError("Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in env")
    return base_url, email, token


def get_client() -> httpx.Client:
    global _client
    if _client is None:
        base_url, email, token = _get_config()
        auth_str = b64encode(f"{email}:{token}".encode()).decode()
        _client = httpx.Client(
            base_url=f"{base_url}/rest/api/3",
            headers={"Authorization": f"Basic {auth_str}", "Content-Type": "application/json"},
            timeout=30.0,
        )
    return _client


def get_project_key() -> str | None:
    return os.environ.get("JIRA_PROJECT_KEY", "").strip() or None
