# 🗃️ AI SQL Agent — Business Analyst in Your Browser

An AI-powered business analytics tool that converts plain English questions into SQL queries, runs them against a database, and explains the results in natural language. No SQL knowledge required.

![Status](https://img.shields.io/badge/status-live-brightgreen)
![Python](https://img.shields.io/badge/python-3.11-blue)
![LangChain](https://img.shields.io/badge/framework-LangChain-yellow)

---

## 🎯 What It Does

Instead of asking a data analyst "how many customers do we have in Mumbai?" — just ask the AI.

- Type any business question in English
- AI writes the SQL query automatically
- Executes it against the database
- Explains results in plain language
- Shows you the SQL used (for transparency)

Example interactions:
```
You: "Which product sells the most?"
AI:  "Office Chair is your best-seller with 181 units sold."
     [Shows SQL: SELECT p.name, SUM(o.quantity)...]

You: "How many orders came in last 30 days?"
AI:  "47 orders were placed in the last 30 days."
```

---

## 💡 Why I Built This

Every business has the same bottleneck: non-technical leaders need data, but can't write SQL. They wait hours (or days) for the data team.

This tool puts the power of SQL in anyone's hands — managers, marketers, founders — without requiring technical knowledge.

This is how modern AI-powered BI tools like ChatGPT Code Interpreter, Snowflake Cortex, and Databricks AI assistants work.

---

## 🏗️ Architecture

```
User Question (English)
         ↓
Schema Context Injection
         ↓
SQL Generation (LLM)
         ↓
SQL Cleanup & Validation
         ↓
Execute Against SQLite
         ↓
Auto-Fix if Query Fails
         ↓
Natural Language Explanation (LLM)
         ↓
Streamlit UI with SQL Expander
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 Natural Language Input | Ask in plain English — no SQL needed |
| ✍️ SQL Generation | AI writes production-quality SQL with JOINs |
| 🔧 Auto-Fix Broken Queries | Retries with corrections if first attempt fails |
| 📊 Plain Language Answers | Results explained like a business analyst would |
| 👀 SQL Transparency | View the SQL generated — build trust |
| 💡 Sample Questions | One-click example queries in sidebar |
| 🔄 Conversation Memory | Ask follow-up questions using context |

---

## 🛠️ Tech Stack

- **Framework:** LangChain
- **LLM:** OpenAI GPT-4 compatible APIs
- **Database:** SQLite
- **UI:** Streamlit
- **Language:** Python 3.11

---

## 🗄️ Sample Database

Includes a realistic business database with:
- 100 customers across 5 Indian cities
- 10 products across multiple categories
- 500 orders spanning 90 days
- Revenue, stock, and status fields

Perfect for demonstrating real-world business queries.

---

## 🚀 Run Locally

```bash
# Clone and navigate
git clone https://github.com/RohJiv/sql-agent-ai.git
cd sql-agent-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create sample database
python create_database.py

# Set up .env
# OPENAI_API_KEY=your_key_here

# Run
streamlit run app.py
```

---

## 📖 How Tool Calling Works

**Tool Calling** is the most important agent skill in production AI.

Traditional LLMs only talk. Agents **take actions**:

```
You:     "How many customers do we have?"

AI thinks: "I need to query the database"
AI writes: SELECT COUNT(*) FROM customers
AI runs:   Execute against SQLite
AI sees:   100
AI says:   "You have 100 customers"
```

The LLM never touches your database directly — it only writes SQL. The application executes it safely. This is a critical security boundary.

---

## 🎓 What I Learned Building This

- **Tool calling and agent patterns** for AI
- **Few-shot prompting** with SQL examples
- **Schema-aware LLM prompts** for accurate query generation
- **Error recovery loops** — auto-fix broken SQL
- **Regex-based SQL sanitization** (table name normalisation)
- **Prompt engineering** for both generation AND explanation
- **Multi-step LLM chains** working together

---

## 💼 Real-World Use Cases

This pattern powers:
- Internal BI tools (replaces custom reports)
- Customer-facing dashboards with natural language search
- Sales team enablement (anyone can query CRM)
- Executive dashboards with conversational drill-down
- Data democratisation in large enterprises

---

## 🔐 Security Notes

- SQL queries executed in sandboxed SQLite
- LLM never has direct database access
- No write operations allowed by default
- Sample data is synthetic — no real customer information

---

## 👤 Author

**Phani Rajiv G**
Technical Program Manager | Cloud & AI Platforms
📍 Hyderabad, India
📧 phani.rg@gmail.com
🔗 [LinkedIn](https://linkedin.com/in/phanirajivg)

---

## 📄 License

MIT License — free to use for learning.

---

⭐ Found this useful? Give it a star!
