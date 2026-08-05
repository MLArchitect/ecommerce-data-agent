import streamlit as st
import json
import os
from groq import Groq
from dotenv import load_dotenv
from db import run_query, get_schema_info

load_dotenv()

if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
    os.environ.update({k: str(v) for k, v in st.secrets.items()})

client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": (
                "Run a read-only SQL query against the Azure SQL database. "
                "Use this to explore data, compute aggregates, filter records, and answer analytical questions. "
                "Only SELECT statements are allowed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "A read-only SELECT SQL query to execute.",
                    }
                },
                "required": ["sql"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_database_schema",
            "description": (
                "Retrieve the schema of all tables in the database, "
                "including table names, column names, data types, and nullability. "
                "Call this first to understand what data is available before writing queries."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a data analysis agent connected to an Azure SQL database containing Olist Brazilian e-commerce data.

Your job is to help the user understand and analyze their data. You can:
1. Inspect the database schema to see what tables and columns exist.
2. Run read-only SQL queries to explore, filter, aggregate, and analyze data.
3. Summarize findings in clear, concise language.

Key rules:
- Always start by checking the schema if you don't know the table structure.
- Only use SELECT statements — never modify data.
- All columns in dbo.order_items are nvarchar — always CAST price and freight_value to FLOAT, and shipping_limit_date to DATETIME.
- Filter shipping_limit_date < '2018-10-01' to exclude stray post-cutoff records.
- Currency is BRL (Brazilian Real), not USD.
- When presenting results, format them clearly with context about what the numbers mean.
- This is a learning tool — explain insights in plain language and suggest follow-up questions."""


def handle_tool_call(tool_name, tool_args):
    if tool_name == "query_database":
        sql = tool_args["sql"].strip()
        if not sql.upper().startswith("SELECT"):
            return json.dumps({"error": "Only SELECT queries are allowed."})
        try:
            columns, rows = run_query(sql)
            if len(rows) > 50:
                rows = rows[:50]
                truncated = True
            else:
                truncated = False
            result = {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": truncated,
            }
            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif tool_name == "get_database_schema":
        try:
            columns, rows = get_schema_info()
            tables = {}
            for row in rows:
                schema, table, col, dtype, nullable = row
                key = f"{schema}.{table}"
                if key not in tables:
                    tables[key] = []
                tables[key].append({
                    "column": col,
                    "type": dtype,
                    "nullable": nullable,
                })
            return json.dumps(tables, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def get_agent_response(conversation_history):
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        msg_dict = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ]
        conversation_history.append(msg_dict)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = handle_tool_call(tool_call.function.name, args)
                conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            break

    return message.content


st.set_page_config(
    page_title="Data Agent",
    page_icon="📊",
    layout="centered",
)

st.title("📊 E-Commerce Data Agent")
st.caption("Ask questions about Olist marketplace data (Oct 2016 – Aug 2018) in plain English.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about the data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.conversation_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = get_agent_response(st.session_state.conversation_history)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
