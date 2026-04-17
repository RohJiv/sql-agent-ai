# app.py — AI SQL Agent / Business Analyst (Complete Final Version)

import os
import re
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# Works locally (from .env) AND on Railway (from environment variables)
def get_api_key():
    # Try Streamlit secrets first (production)
    try:
        return st.secrets["GROQ_API_KEY"]
    except:
        # Fall back to .env (local development)
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("GROQ_API_KEY")

# ── Load API key ──────────────────────────────────────────────
load_dotenv()

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="🗃️ AI Business Analyst",
    page_icon="🗃️",
    layout="wide"
)

# ── Database path — always correct regardless of where app runs
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "business.db")

# ── Initialize session state ──────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "quick_question" not in st.session_state:
    st.session_state["quick_question"] = ""

# ── Load LLM once ─────────────────────────────────────────────
@st.cache_resource
def load_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=get_api_key()
    )

llm = load_llm()

# ── Get database schema ───────────────────────────────────────
@st.cache_resource
def get_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    schema = ""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        schema += f"\nTable: {table_name} ({count} rows)\n"
        schema += f"Columns: {', '.join(col_names)}\n"
    conn.close()
    return schema

schema = get_schema()

# ── Clean SQL — fix table names ───────────────────────────────
def clean_sql(sql):
    sql = sql.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    # Fix product/customer table names only
    # Use negative lookahead to avoid replacing ORDER BY
    sql = re.sub(r'\bproducts?\b',  'products',  sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bcustomers?\b', 'customers', sql, flags=re.IGNORECASE)

    # For orders — only replace when it's a table name (after FROM or JOIN)
    # NOT when it's part of ORDER BY
    sql = re.sub(r'(?i)(FROM|JOIN)\s+orders?\b', 
                 lambda m: m.group(1) + ' orders', sql, flags=re.IGNORECASE)

    return sql.strip()

# ── Run SQL safely ────────────────────────────────────────────
def run_sql(sql):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return columns, results, None
    except Exception as e:
        return None, None, str(e)

# ── Step 1: Generate SQL from question ───────────────────────
def generate_sql(question, chat_history):
    history_text = ""
    for msg in chat_history[-4:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    prompt = ChatPromptTemplate.from_template("""
You are a SQL expert working with a SQLite database.

DATABASE SCHEMA:
{schema}

EXAMPLE QUERIES FOR REFERENCE:
-- Top selling products by quantity
SELECT p.name, SUM(o.quantity) as total_sold
FROM orders o
JOIN products p ON o.product_id = p.id
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 5;

-- Total revenue
SELECT SUM(total) as total_revenue FROM orders;

-- Customers by city
SELECT city, COUNT(*) as count
FROM customers
GROUP BY city
ORDER BY count DESC;

-- Orders last 30 days
SELECT COUNT(*) FROM orders
WHERE order_date >= date('now', '-30 days');

-- Pending orders
SELECT COUNT(*) FROM orders WHERE status = 'pending';

-- Average order value
SELECT ROUND(AVG(total), 2) as avg_order_value FROM orders;

-- Product with lowest stock
SELECT name, stock FROM products ORDER BY stock ASC LIMIT 1;

-- Revenue by product
SELECT p.name, SUM(o.total) as revenue
FROM orders o
JOIN products p ON o.product_id = p.id
GROUP BY p.id, p.name
ORDER BY revenue DESC;

CONVERSATION HISTORY:
{history}

QUESTION: {question}

STRICT RULES:
- Return ONLY the raw SQL query — no explanation, no markdown, no backticks
- ALWAYS use exact lowercase table names: customers, products, orders
- Use only columns that exist in the schema above
- For JOINs always use: FROM orders o JOIN products p ON o.product_id = p.id
- For date filtering use: date('now', '-30 days')
- For revenue use: SUM(total) from orders
- Always use LIMIT 20 for large results
- Use ORDER BY for ranking questions

SQL QUERY:
""")

    chain = prompt | llm | StrOutputParser()
    sql = chain.invoke({
        "schema": schema,
        "question": question,
        "history": history_text
    })
    sql = clean_sql(sql)
    #st.code(sql, language="sql") # shows sql whats wrong
    return sql

# ── Step 2: Explain results in plain English ─────────────────
def explain_results(question, sql, columns, results):
    if not results:
        results_text = "No results found"
    else:
        results_text = f"Columns: {columns}\n"
        for row in results[:20]:
            results_text += f"{row}\n"

    prompt = ChatPromptTemplate.from_template("""
You are a friendly Business Analyst explaining database query results.

QUESTION: {question}
SQL USED: {sql}
RESULTS: {results}

RULES:
- Start directly with the answer — no preamble
- Use bullet points for lists of items
- Include relevant numbers and percentages where useful
- Keep it concise but complete
- If no results found say no data was found clearly

ANSWER:
""")

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "question": question,
        "sql": sql,
        "results": results_text
    })

# ── Step 3: Fix broken SQL ────────────────────────────────────
def fix_sql(sql, error, question):
    prompt = ChatPromptTemplate.from_template("""
This SQL query failed. Fix it.

SCHEMA: {schema}
QUESTION: {question}
FAILED SQL: {sql}
ERROR: {error}

RULES:
- Return ONLY the corrected SQL — no explanation, no markdown, no backticks
- Use exact lowercase table names: customers, products, orders
- For JOINs use: FROM orders o JOIN products p ON o.product_id = p.id
- Use only columns that exist in the schema

FIXED SQL:
""")
    chain = prompt | llm | StrOutputParser()
    fixed = chain.invoke({
        "schema": schema,
        "question": question,
        "sql": sql,
        "error": error
    })
    return clean_sql(fixed)

# ── Title ─────────────────────────────────────────────────────
st.title("🗃️ AI Business Analyst")
st.caption("Ask business questions in plain English — AI writes SQL and explains results")

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("🗄️ Database Info")
    st.info("""
**Tables available:**
- 👥 customers (100 rows)
- 📦 products (10 rows)
- 🛒 orders (500 rows)
    """)

    st.divider()
    st.markdown("**💡 Try these questions:**")

    example_questions = [
        "How many customers do we have?",
        "Which product is selling the most?",
        "How many orders came in last 30 days?",
        "Which city has the most customers?",
        "What is our total revenue?",
        "Which product has the lowest stock?",
        "How many orders are still pending?",
        "What is the average order value?",
        "Show revenue by product",
        "How many orders per status?",
    ]

    for q in example_questions:
        if st.button(q, key=q):
            st.session_state["quick_question"] = q
            st.rerun()

    st.divider()

    if st.button("🗄️ Show Database Schema"):
        st.code(schema)

    if st.button("🗑️ Clear Chat"):
        st.session_state["chat_history"] = []
        st.rerun()

    st.caption("Built by Sahaji | Powered by Groq + LangChain")

# ── Display chat history ──────────────────────────────────────
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sql"):
            with st.expander("🔍 SQL Generated"):
                st.code(msg["sql"], language="sql")

# ── Input Row ─────────────────────────────────────────────────
st.divider()
col_input, col_send = st.columns([11, 1])

with col_input:
    question = st.text_input(
        "question",
        value=st.session_state["quick_question"],
        placeholder="Ask a business question in plain English...",
        label_visibility="collapsed",
        key="question_input"
    )

with col_send:
    send_btn = st.button("➤", type="primary")

# Clear quick question after use
if st.session_state["quick_question"]:
    st.session_state["quick_question"] = ""

# ── Process Question ──────────────────────────────────────────
if send_btn and question:

    with st.chat_message("user"):
        st.markdown(question)

    st.session_state["chat_history"].append({
        "role": "user",
        "content": question
    })

    sql = ""
    answer = ""

    with st.chat_message("assistant"):

        # Step 1 — Generate SQL
        with st.spinner("✍️ Writing SQL query..."):
            sql = generate_sql(question, st.session_state["chat_history"])

        # Step 2 — Run SQL
        with st.spinner("⚡ Running query..."):
            columns, results, error = run_sql(sql)

        # Step 3 — If failed try to fix once
        if error:
            with st.spinner("🔧 Fixing query..."):
                sql = fix_sql(sql, error, question)
                columns, results, error = run_sql(sql)

        # Step 4 — Explain or show error
        if error:
            answer = f"❌ Could not execute query: {error}"
            st.error(answer)
        else:
            with st.spinner("💬 Explaining results..."):
                answer = explain_results(question, sql, columns, results)
            st.markdown(answer)
            with st.expander("🔍 SQL Generated"):
                st.code(sql, language="sql")

    # Save to history
    st.session_state["chat_history"].append({
        "role": "assistant",
        "content": answer,
        "sql": sql
    })