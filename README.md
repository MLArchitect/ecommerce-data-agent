# E-Commerce Data Agent

An AI-powered agent that answers analytical questions about Olist Brazilian e-commerce data using natural language. Ask questions in plain English and get answers backed by real SQL queries.

**Live app:** [https://mlarchitect-ecommerce-data-agent-app-xmrn8l.streamlit.app](https://mlarchitect-ecommerce-data-agent-app-xmrn8l.streamlit.app)

## How it works

1. You ask a question in the chat (e.g. "What is the total revenue?")
2. The LLM decides what SQL query to run
3. The query executes against Azure SQL and returns results
4. The LLM explains the results in plain language

## Tech stack

- **LLM:** Groq (llama-3.3-70b-versatile, free tier)
- **Database:** Azure SQL with Microsoft Entra (service principal auth)
- **Web UI:** Streamlit
- **Database driver:** pytds (pure Python, no ODBC needed)

## Dataset

Olist Brazilian e-commerce order items — 112,650 rows covering Oct 2016 to Aug 2018. Columns: order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value. Currency is BRL (Brazilian Real).

## Example questions

| Question | Answer |
|----------|--------|
| What is the total revenue? | ~13,591,298 BRL |
| What is the average price of an order item? | ~120.65 BRL |
| How many orders are in the dataset? | 98,663 unique orders (112,650 order items) |
| Which month had the highest revenue? | Try it and find out! |
| What is the average freight cost? | Try it and find out! |
| Who are the top 5 sellers by revenue? | Try it and find out! |

## Setup

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials
4. Run locally:
   ```
   python agent.py
   ```

## Deploy to Streamlit Cloud

1. Push the repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app
3. Point it to your repo, branch `master`, file `app.py`
4. In Advanced Settings, add your secrets (same format as `.env`)
5. Make sure your Azure SQL firewall allows Streamlit Cloud's IP
