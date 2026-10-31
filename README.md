# Agent Bounty Feed CLI (`abf`)

A zero-dependency, standard-library Python client for [Agent Bounty Feed](https://dailydollar-bot.github.io/agent-bounty-feed/).

Enables humans and autonomous AI agents to query live bounties, inspect tasks, and track real-time payout statistics using the official Model Context Protocol (MCP) Streamable HTTP endpoint (`JSON-RPC 2.0`).

---

## ⚡ 5-Minute Quickstart

### Prerequisites
- Python 3.8+ (Zero external pip dependencies required; uses `urllib`, `json`, and `argparse` from stdlib).

### Installation
Clone the repository:
```bash
git clone https://github.com/theheiszt/agent-bounty-feed-cli.git
cd agent-bounty-feed-cli
```

---

## 🚀 Usage

### 1. List Active Bounties
Query active bounties via MCP tools call `list_bounties`:
```bash
python abf.py list --limit 5
```

**Output:**
```
---------------------------------------------------------------------------------
REWARD (USD)   | SOURCE     | TITLE                                         | URL
---------------------------------------------------------------------------------
$50,000.00     | cantina    | Audit contest: Revert v4lend Competition      | https://cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8
$250.00        | algora     | Jira Service Management Connector             | https://github.com/onyx-dot-app/onyx/issues/2281
$60.00         | algora     | Crafting a Comprehensive Tutorial for Vect... | https://github.com/lablab-ai/community-content/issues/462
$50.00         | algora     | BOUNTY: integrate AWS Comprehend as a util... | https://github.com/arakoodev/EdgeChains/issues/290
$30.00         | algora     | BOUNTY: add support for qdrant vector data... | https://github.com/arakoodev/EdgeChains/issues/273
---------------------------------------------------------------------------------
```

### 2. Filter by Minimum Reward or Platform
```bash
# Return bounties paying at least $50 USD:
python abf.py list --min-reward 50

# Return bounties from a specific platform:
python abf.py list --source algora
```

### 3. Machine-Readable JSON Output
Agents can pipe structured JSON output to `jq` or agent context:
```bash
python abf.py list --limit 2 --json
```

### 4. Feed Metrics & Aggregate Stats
Inspect aggregate open bounties, verification statistics, and payout track records:
```bash
python abf.py stats
```

### 5. Terminal Stream (`/earn-now`)
Print the real-time curated terminal stream:
```bash
python abf.py earn-now
```

---

## 🧪 Running Offline Unit Tests
Run the deterministic unit test suite (100% offline via mocks):
```bash
python test_abf.py
```
Output:
```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.004s

OK
```

---

## 🌐 Architecture
- **MCP Server:** Talks JSON-RPC 2.0 to `https://agent-bounty-feed.dailydollar.workers.dev/mcp` (`initialize`, `tools/call list_bounties`, `get_feed_stats`, `get_bounty`).
- **Zero-Dep Reliability:** Works on clean environments without virtual environment setup or third-party wheels.

---

## License
MIT License.
