# E-Commerce Data Agent

An AI-powered agent that answers analytical questions about e-commerce data using natural language. Built with Azure OpenAI and Azure SQL.

## Setup

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials
4. Run the agent:
   ```
   python agent.py
   ```

## Web UI (for team access)

```
pip install streamlit
streamlit run app.py
```

Share the URL with your team — they can ask questions in the browser.

## Tech stack

- Azure OpenAI (LLM with tool calling)
- Azure SQL Database (data storage)
- Streamlit (web interface)
- Python + pyodbc (database driver)
