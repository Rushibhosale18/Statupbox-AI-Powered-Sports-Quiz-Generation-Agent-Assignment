# 🏆 AI-Powered Sports Quiz Generation Agent

An interactive web application that generates engaging, factually accurate sports quizzes using **Retrieval-Augmented Generation (RAG)**. The system combines a local **ChromaDB** vector database of historical sports facts with live **DuckDuckGo** web search results to ground every question in verified information.

![Python](https://img.shields.io/badge/Python-3.9--3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.22+-green)

---

## 📋 Features

- **6 Sports**: Cricket, Football, Badminton, Tennis, Basketball, Baseball
- **3 Difficulty Levels**: Easy, Medium, Hard
- **RAG Pipeline**: Combines offline historical facts (ChromaDB) with live web results (DuckDuckGo)
- **Interactive Quiz UI**: Radio-button answer selection with instant feedback
- **Score Tracking**: Real-time scoring with percentage display
- **RAG Transparency**: Inspect the exact context sources used for each quiz
- **Social Media Export**: Copy-paste ready quiz output

---

## 🏗️ Architecture

```
User (Sport + Difficulty)
       │
       ▼
 ┌─────────────┐
 │  Streamlit   │  ← Interactive web dashboard
 │   app.py     │
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ generator.py │  ← RAG orchestration: merge contexts → LLM prompt → parse output
 └──┬───────┬──┘
    │       │
    ▼       ▼
 database.py  search.py
 (ChromaDB)   (DuckDuckGo)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9, 3.10, or 3.11** (avoid 3.12+ for ChromaDB compatibility)
- **OpenAI API Key** (get one at [platform.openai.com](https://platform.openai.com))

### 1. Clone & Navigate

```bash
cd sports-quiz-agent
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure API Key

Open the `.env` file and replace the placeholder with your real key:

```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

> ⚠️ **Never commit your API key to version control!** The `.gitignore` already excludes `.env`.

### 5. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
sports-quiz-agent/
│
├── .env                   # API key (never commit this!)
├── .gitignore             # Excludes secrets & generated files
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── data/
│   └── sports_facts.json  # 26 curated historical sports facts
│
├── chroma_db/             # Auto-created by ChromaDB on first run
│
├── src/
│   ├── __init__.py        # Package init
│   ├── config.py          # Environment & path configuration
│   ├── database.py        # ChromaDB: init, populate, semantic query
│   ├── search.py          # DuckDuckGo live web search wrapper
│   └── generator.py       # RAG orchestration & quiz parsing
│
└── app.py                 # Streamlit dashboard entry point
```

---

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `MODEL_NAME` | `gpt-3.5-turbo` | LLM model (set in `.env` to override, e.g. `gpt-4o`) |

---

## 🛠️ Troubleshooting

### ChromaDB SQLite Error

If you see a SQLite version error, install the binary package:

```bash
pip install pysqlite3-binary
```

Then add these lines at the **very top** of `src/database.py`:

```python
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

### API Key Issues

- Ensure `.env` contains `OPENAI_API_KEY=sk-proj-...` (no quotes needed)
- Check that the key is valid and has credits at [platform.openai.com](https://platform.openai.com)

### Quiz Parsing Problems

If the quiz output looks garbled, try:
1. Regenerating (the LLM output varies each time)
2. Switching to `gpt-4o` in `.env` for more consistent formatting

---

## 📄 License

This project is for educational purposes as part of the Statupbox AI Product/Engineer Intern Assignment.
