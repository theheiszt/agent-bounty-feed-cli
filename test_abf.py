#!/usr/bin/env python3
"""
Unit tests for abf.py (Agent Bounty Feed CLI)
Tests run 100% offline using mock responses.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import io

from abf import ABFClient, format_table


class TestABFClient(unittest.TestCase):
    def setUp(self):
        self.client = ABFClient(mcp_url="https://mock-mcp.local", timeout=5.0)

    @patch("urllib.request.urlopen")
    def test_initialize(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "agent-bounty-feed", "version": "1.2.0"}
            }
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.initialize()
        self.assertEqual(res["protocolVersion"], "2024-11-05")
        self.assertEqual(res["serverInfo"]["name"], "agent-bounty-feed")

    @patch("urllib.request.urlopen")
    def test_list_bounties(self, mock_urlopen):
        mock_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "items": [
                            {
                                "id": "test:001",
                                "title": "Implement Test Connector",
                                "reward": 250.0,
                                "est_usd": 250.0,
                                "source": "algora",
                                "url": "https://github.com/example/repo/issues/1"
                            }
                        ]
                    })
                }]
            }
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        items = self.client.list_bounties(limit=1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "test:001")
        self.assertEqual(items[0]["est_usd"], 250.0)

    @patch("urllib.request.urlopen")
    def test_get_feed_stats(self, mock_urlopen):
        mock_stats = {"total_usd": 617.6, "items": 25}
        mock_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [{"type": "text", "text": json.dumps(mock_stats)}]
            }
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        stats = self.client.get_feed_stats()
        self.assertEqual(stats["total_usd"], 617.6)
        self.assertEqual(stats["items"], 25)

    def test_format_table(self):
        sample = [
            {
                "title": "Fix memory leak in parser",
                "reward": 100.0,
                "est_usd": 100.0,
                "source": "algora",
                "url": "https://github.com/example/repo/issues/42"
            }
        ]
        table = format_table(sample)
        self.assertIn("$100.00", table)
        self.assertIn("algora", table)
        self.assertIn("Fix memory leak in parser", table)

    def test_format_table_empty(self):
        table = format_table([])
        self.assertEqual(table, "No matching bounties found.")


if __name__ == "__main__":
    unittest.main()
