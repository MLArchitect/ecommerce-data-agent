# AI Agent Project

A learning-focused AI agent that connects to an Azure SQL database and answers analytical questions about e-commerce data using natural language.

## Architecture

```
agent.py       → Main agent loop (Azure OpenAI chat + tool calling)
db.py          → Database connection (Azure SQL via service principal + access token)
query_tool.py  → CLI tool for running queries (used by /data-agent skill)
```

- **LLM:** Azure OpenAI (deployment name in .env)
- **Database:** Azure SQL with Microsoft Entra (service principal auth, not password)
- **Driver:** pyodbc with ODBC Driver 18 for SQL Server

## How it works

1. `agent.py` runs an agentic loop: user asks a question → LLM decides whether to call `query_database` or `get_database_schema` → tool result feeds back into the LLM → LLM responds
2. `query_tool.py` is a standalone CLI used by the `/data-agent` Claude Code skill
3. Both enforce read-only access (SELECT only)

## Dataset

The primary dataset is `dbo.order_items` — Olist Brazilian e-commerce order items (112,650 rows, Oct 2016 – Aug 2018). All columns are stored as `nvarchar` and must be CAST for calculations. Full data dictionary and KPI reference are in `.claude/commands/data-agent.md`.

There is also a `dbo.products` table (product_id, product_name, units_in_stock, sale_price) with proper typed columns.

## Skills

The `/data-agent` skill (defined in `.claude/commands/data-agent.md`) is the primary interface for answering data questions. It contains:
- Full data dictionary with all 7 variables
- KPI definitions and baseline benchmarks
- Red flags and data caveats
- Tone and communication guidelines
- Example SQL patterns with proper CAST usage

When answering data or analytics questions, follow the instructions in the `/data-agent` skill file.

## Running

```bash
# Interactive agent
python agent.py

# Direct queries via CLI
python query_tool.py schema
python query_tool.py query "SELECT TOP 5 * FROM dbo.order_items"
python query_tool.py sample dbo.order_items
```

## Environment

Requires a `.env` file — see `.env.example` for required variables. Never commit `.env` to git.

Dependencies: `pip install -r requirements.txt` (openai, pyodbc, azure-identity, python-dotenv, tabulate)

## Rules

- Never modify data — SELECT queries only
- Never expose or commit credentials (.env, connection strings, API keys)
- Always CAST nvarchar columns before arithmetic or date operations on `dbo.order_items`
- Filter `shipping_limit_date < '2018-10-01'` to exclude stray post-cutoff records
- Currency is BRL (Brazilian Real), not USD
- This is a learning project — prioritize clear explanations over brevity
