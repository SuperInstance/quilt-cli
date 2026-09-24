"""
scout.py — `quilt scout` command.

List recently-pushed SuperInstance repos. Use the GitHub API directly
so the CLI works without cloning.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request


GITHUB_API = "https://api.github.com"


def _api_get(path: str):
    """GET a GitHub API endpoint. Returns None on error."""
    url = f"{GITHUB_API}{path}"
    headers = {"Accept": "application/vnd.github.v3+json",
                "User-Agent": "quilt-cli/0.4.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  scout: API error: {e}", file=sys.stderr)
        return None


def list_recent_repos(org: str = "SuperInstance", limit: int = 30) -> list:
    """List repos in `org` sorted by most recent push."""
    data = _api_get(f"/users/{org}/repos?per_page={limit}&sort=pushed&direction=desc")
    if not isinstance(data, list):
        return []
    return data


def brief(repo: dict) -> str:
    """Format a one-line brief of a repo."""
    pushed = repo.get("pushed_at", "?")[:10]
    name = repo.get("name", "?")
    desc = (repo.get("description") or "(no description)")[:80]
    return f"  {pushed}  {name:35s}  {desc}"


def run_scout(args) -> int:
    """The `quilt scout` subcommand."""
    print(f"=== quilt scout — SuperInstance repos, last {args.limit} ===\n")
    repos = list_recent_repos(limit=args.limit)
    if not repos:
        print("  (could not fetch from GitHub API)")
        return 1
    print(f"  TOTAL REPOS: {len(repos)}")
    print()
    print(f"  === TOP {min(args.limit, len(repos))} MOST RECENTLY PUSHED ===")
    for r in repos[:args.limit]:
        print(brief(r))
    if args.filter:
        print()
        print(f"  === FILTERED: '{args.filter}' ===")
        for r in repos:
            name = r.get("name", "")
            desc = (r.get("description") or "").lower()
            if args.filter.lower() in name.lower() or args.filter.lower() in desc:
                print(brief(r))
    print()
    return 0


def register(sub):
    p = sub.add_parser("scout", help="scout recently-pushed fleet repos")
    p.add_argument("--limit", type=int, default=20,
                   help="max repos to show")
    p.add_argument("--filter", type=str, default="",
                   help="filter by name or description substring")
    p.set_defaults(func=run_scout)
