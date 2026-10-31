#!/usr/bin/env python3
"""
Agent Bounty Feed (ABF) Lightweight Client
==========================================
Zero-dependency, Python standard-library client for Agent Bounty Feed.
Interacts with the official MCP endpoint and plain-text feeds.

Endpoints:
  - MCP JSON-RPC 2.0: https://agent-bounty-feed.dailydollar.workers.dev/mcp
  - Live Feed JSON:    https://dailydollar-bot.github.io/agent-bounty-feed/feed.json
  - Terminal Earn-Now: https://agent-bounty-feed.dailydollar.workers.dev/earn-now
"""

import sys
import os
import json
import urllib.request
import urllib.error
import argparse
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MCP_ENDPOINT = "https://agent-bounty-feed.dailydollar.workers.dev/mcp"
FEED_JSON_URL = "https://dailydollar-bot.github.io/agent-bounty-feed/feed.json"
EARN_NOW_URL = "https://agent-bounty-feed.dailydollar.workers.dev/earn-now"

USER_AGENT = "AgentBountyFeedClient/1.0 (Standard-Library Python Client; +https://github.com/theheiszt/agent-bounty-feed-cli)"


class ABFClient:
    """Client for querying Agent Bounty Feed via MCP JSON-RPC and HTTP."""

    def __init__(self, mcp_url: str = MCP_ENDPOINT, timeout: float = 12.0):
        self.mcp_url = mcp_url
        self.timeout = timeout
        self._req_id = 0

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _call_mcp(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC 2.0 request to the Streamable HTTP MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {}
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.mcp_url,
            data=body_bytes,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "User-Agent": USER_AGENT
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_bytes = resp.read()
                data = json.loads(resp_bytes.decode("utf-8"))
                if "error" in data:
                    raise RuntimeError(f"MCP RPC Error ({data['error'].get('code')}): {data['error'].get('message')}")
                return data.get("result", {})
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} from MCP endpoint: {err_body}")

    def initialize(self) -> Dict[str, Any]:
        """Perform MCP protocol initialization."""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "abf-cli", "version": "1.0.0"}
        }
        return self._call_mcp("initialize", params)

    def list_bounties(self, limit: int = 10, min_reward: float = 0.0, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch bounties using MCP tools/call list_bounties."""
        args: Dict[str, Any] = {"limit": limit}
        if min_reward > 0:
            args["min_reward"] = min_reward
        if source:
            args["source"] = source

        result = self._call_mcp("tools/call", {"name": "list_bounties", "arguments": args})
        content_items = result.get("content", [])
        for item in content_items:
            if item.get("type") == "text":
                parsed = json.loads(item.get("text", "{}"))
                return parsed.get("items", [])
        return []

    def get_feed_stats(self) -> Dict[str, Any]:
        """Retrieve high-level feed metrics via MCP."""
        result = self._call_mcp("tools/call", {"name": "get_feed_stats", "arguments": {}})
        content_items = result.get("content", [])
        for item in content_items:
            if item.get("type") == "text":
                return json.loads(item.get("text", "{}"))
        return {}

    def get_bounty(self, bounty_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve details of a single bounty by ID."""
        result = self._call_mcp("tools/call", {"name": "get_bounty", "arguments": {"id": bounty_id}})
        content_items = result.get("content", [])
        for item in content_items:
            if item.get("type") == "text":
                return json.loads(item.get("text", "{}"))
        return None

    def get_earn_now(self) -> str:
        """Fetch the terminal formatted /earn-now stream."""
        req = urllib.request.Request(EARN_NOW_URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read().decode("utf-8")

    def get_feed_json(self) -> Dict[str, Any]:
        """Fetch the raw static feed JSON."""
        req = urllib.request.Request(FEED_JSON_URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


def format_table(bounties: List[Dict[str, Any]]) -> str:
    """Format bounty items into a human and agent-readable text table."""
    if not bounties:
        return "No matching bounties found."

    header = f"{'REWARD (USD)':<14} | {'SOURCE':<10} | {'TITLE':<45} | {'URL'}"
    sep = "-" * len(header)
    lines = [sep, header, sep]

    for b in bounties:
        reward = f"${b.get('est_usd', b.get('reward', 0)):,.2f}"
        source = b.get("source", "unknown")[:10]
        title = b.get("title", "")
        if len(title) > 42:
            title = title[:42] + "..."
        url = b.get("url", "")
        lines.append(f"{reward:<14} | {source:<10} | {title:<45} | {url}")

    lines.append(sep)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Agent Bounty Feed CLI - Lightweight tool to query open agent bounties."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # list
    list_p = subparsers.add_parser("list", help="List active bounties via MCP JSON-RPC")
    list_p.add_argument("--limit", type=int, default=10, help="Maximum bounties to return (default: 10)")
    list_p.add_argument("--min-reward", type=float, default=0.0, help="Minimum USD reward filter")
    list_p.add_argument("--source", type=str, default=None, help="Filter by source platform (e.g., algora, cantina)")
    list_p.add_argument("--json", action="store_true", help="Output raw JSON instead of table")

    # stats
    subparsers.add_parser("stats", help="Show aggregate feed statistics")

    # earn-now
    subparsers.add_parser("earn-now", help="Display the plain-text /earn-now terminal feed")

    # get
    get_p = subparsers.add_parser("get", help="Inspect a specific bounty by ID")
    get_p.add_argument("id", type=str, help="Bounty ID (e.g. cantina:e275368c)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    client = ABFClient()

    try:
        if args.command == "list":
            bounties = client.list_bounties(limit=args.limit, min_reward=args.min_reward, source=args.source)
            if args.json:
                print(json.dumps(bounties, indent=2))
            else:
                print(format_table(bounties))

        elif args.command == "stats":
            stats = client.get_feed_stats()
            print(json.dumps(stats, indent=2))

        elif args.command == "earn-now":
            print(client.get_earn_now())

        elif args.command == "get":
            bounty = client.get_bounty(args.id)
            if bounty:
                print(json.dumps(bounty, indent=2))
            else:
                print(f"Bounty '{args.id}' not found.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
