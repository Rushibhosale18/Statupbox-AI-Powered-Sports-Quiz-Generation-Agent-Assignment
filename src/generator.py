"""
RAG Orchestration module (generator).
Combines ChromaDB historical context with live DuckDuckGo results,
constructs a grounded prompt, and calls the OpenAI LLM to generate
structured multiple-choice quiz questions.
"""

import re
from openai import OpenAI
from google import genai
from google.genai import types

from src.config import OPENAI_API_KEY, OPENAI_MODEL_NAME, GEMINI_API_KEY, GEMINI_MODEL_NAME
from src.database import query_historic_facts
from src.search import get_live_news_context


# ── Prompt Templates ────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """\
You are an expert sports quiz creator. Your job is to write multiple-choice quiz \
questions that are engaging, educational, and accurate.

STRICT RULES:
1. Base every question ONLY on the Context provided below. Do NOT use outside knowledge.
2. If the context lacks enough facts, create fewer questions rather than inventing information.
3. Each question must have exactly 4 options (A, B, C, D) with only ONE correct answer.
4. The explanation must reference specific details from the Context.

CONTEXT DETAILS:
{context}
"""

USER_PROMPT_TEMPLATE = """\
Generate exactly {num_questions} unique multiple-choice questions for the sport: {sport}.
Difficulty target: {difficulty}.

Difficulty guide:
- Easy: Basic facts, well-known records, founding dates.
- Medium: Specific statistics, notable but less commonly known achievements.
- Hard: Obscure records, detailed historical events, tricky distractors.

Format each question EXACTLY as follows (this format is required for parsing):

Question: [Question text here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Single letter, e.g., A]
Explanation: [Detailed reasoning referencing the context]
---
"""


# ── Quiz Generation ─────────────────────────────────────────────────────────────

def compile_quiz_data(sport, difficulty, num_questions=4, provider="OpenAI", api_key=None):
    """
    End-to-end RAG pipeline supporting both OpenAI and Google Gemini:
    1. Queries ChromaDB for historical context.
    2. Queries DuckDuckGo for live web context.
    3. Merges both into a unified prompt.
    4. Calls the selected LLM provider (OpenAI or Gemini).

    Args:
        sport:          The sport category (e.g. "Cricket").
        difficulty:     One of "Easy", "Medium", "Hard".
        num_questions:  Number of quiz questions to generate.
        provider:       "OpenAI" or "Gemini".
        api_key:        Optional key override from the Streamlit UI.

    Returns:
        Tuple of (raw_quiz_text, unified_context).
    """
    # ── Step 1: Historical context from ChromaDB ─────────────────────────────
    db_query = f"{sport} history championships records rules achievements"
    db_matches = query_historic_facts(sport=sport, query_text=db_query, n_results=3)
    db_context = "\n".join(f"• {fact}" for fact in db_matches) if db_matches else "No historical data available."

    # ── Step 2: Live context from DuckDuckGo ─────────────────────────────────
    web_context = get_live_news_context(sport)

    # ── Step 3: Merge contexts ───────────────────────────────────────────────
    unified_context = (
        f"=== HISTORICAL FACTS (from Knowledge Base) ===\n{db_context}\n\n"
        f"=== LIVE WEB NEWS (from Internet Search) ===\n{web_context}"
    )

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=unified_context)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        num_questions=num_questions,
        sport=sport,
        difficulty=difficulty,
    )

    # ── Step 4: Call LLM ─────────────────────────────────────────────────────
    if provider == "OpenAI":
        # Use provided key or fall back to environment variable
        active_key = api_key if api_key else OPENAI_API_KEY
        if not active_key or active_key == "your-api-key-here":
            raise ValueError("OpenAI API Key is missing. Please provide it in the sidebar or .env file.")

        client = OpenAI(api_key=active_key)
        response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        raw_quiz_text = response.choices[0].message.content

    elif provider == "Gemini":
        # Use provided key or fall back to environment variable
        active_key = api_key if api_key else GEMINI_API_KEY
        if not active_key:
            raise ValueError("Gemini API Key is missing. Please provide it in the sidebar or .env file.")

        client = genai.Client(api_key=active_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=2000,
            )
        )
        raw_quiz_text = response.text

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    return raw_quiz_text, unified_context


# ── Quiz Parsing ────────────────────────────────────────────────────────────────

def parse_quiz_questions(raw_text):
    """
    Parses the raw LLM output into a structured list of question dicts.

    Each dict contains:
        - question:       str
        - options:        dict  {"A": "...", "B": "...", "C": "...", "D": "..."}
        - correct_answer: str   (single letter, e.g. "A")
        - explanation:    str

    Returns:
        List of question dicts. May be empty if parsing fails entirely.
    """
    questions = []

    # Split on the "---" separator
    blocks = re.split(r"\n-{3,}\n?", raw_text.strip())

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        q = {}

        # Extract question text
        q_match = re.search(r"Question:\s*(.+?)(?=\n[A-D][).]\s)", block, re.DOTALL)
        if q_match:
            q["question"] = q_match.group(1).strip()
        else:
            continue  # Can't parse this block

        # Extract options (supports both "A)" and "A." formats)
        options = {}
        for letter in ["A", "B", "C", "D"]:
            opt_match = re.search(
                rf"{letter}[).]\s*(.+?)(?=\n[A-D][).]\s|\nCorrect|\Z)",
                block,
                re.DOTALL,
            )
            if opt_match:
                options[letter] = opt_match.group(1).strip()
        q["options"] = options

        # Extract correct answer
        ans_match = re.search(r"Correct Answer:\s*([A-D])", block)
        if ans_match:
            q["correct_answer"] = ans_match.group(1).strip()
        else:
            q["correct_answer"] = "A"  # Fallback

        # Extract explanation
        exp_match = re.search(r"Explanation:\s*(.+)", block, re.DOTALL)
        if exp_match:
            q["explanation"] = exp_match.group(1).strip()
        else:
            q["explanation"] = "No explanation provided."

        # Only add if we have a valid question with at least 2 options
        if q.get("question") and len(q.get("options", {})) >= 2:
            questions.append(q)

    return questions
