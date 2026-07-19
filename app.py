"""
🏆 AI-Powered Sports Quiz Generator — Streamlit Dashboard

Main entry point. Coordinates the RAG pipeline and renders an interactive,
polished quiz experience with instant answer feedback and score tracking.

Run with:  streamlit run app.py
"""

import streamlit as st
from src.generator import compile_quiz_data, parse_quiz_questions
from src.database import setup_and_populate_db


# ── Page Configuration ──────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Sports Quiz Agent | AI-Powered",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ── Database Initialization (runs once) ─────────────────────────────────────────

@st.cache_resource
def prepare_knowledge_base():
    """One-time ChromaDB population on app startup."""
    return setup_and_populate_db()


prepare_knowledge_base()


# ── Custom CSS ──────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Google Font ─────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header gradient ─────────────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    }
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.4rem;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1rem;
        margin: 0;
        font-weight: 400;
    }

    /* ── Quiz card ───────────────────────────────────────────────── */
    .quiz-card {
        background: #ffffff;
        border: 1px solid #e8ecf1;
        border-radius: 14px;
        padding: 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        transition: box-shadow 0.2s ease;
    }
    .quiz-card:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    .quiz-number {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 0.6rem;
        letter-spacing: 0.5px;
    }
    .quiz-question {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        line-height: 1.5;
        margin-bottom: 0.3rem;
    }

    /* ── Feedback boxes ──────────────────────────────────────────── */
    .correct-box {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-top: 0.6rem;
        color: #155724;
    }
    .incorrect-box {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border-left: 4px solid #dc3545;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-top: 0.6rem;
        color: #721c24;
    }
    .explanation-text {
        font-size: 0.92rem;
        line-height: 1.5;
        margin-top: 0.4rem;
    }

    /* ── Score banner ────────────────────────────────────────────── */
    .score-banner {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 4px 16px rgba(252, 182, 159, 0.3);
    }
    .score-banner h2 {
        color: #e55d50;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .score-banner p {
        color: #c0392b;
        font-weight: 500;
        margin: 0.3rem 0 0;
    }

    /* ── Sidebar styling ─────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
    }

    /* ── RAG context area ────────────────────────────────────────── */
    .context-header {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.4rem;
    }

    /* ── Hide default Streamlit branding ─────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Header ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🏆 AI-Powered Sports Quiz</h1>
    <p>Challenge your knowledge with AI-generated quizzes powered by RAG — grounded in real facts &amp; live news</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar Controls ────────────────────────────────────────────────────────────

st.sidebar.markdown("## ⚙️ Quiz Settings")
st.sidebar.markdown("---")

SPORTS = ["Cricket", "Football", "Badminton", "Tennis", "Basketball", "Baseball"]

sport_choice = st.sidebar.selectbox(
    "🏅 Select Sport",
    SPORTS,
    index=0,
    help="Choose the sport you want to be quizzed on.",
)

difficulty = st.sidebar.select_slider(
    "📊 Difficulty Level",
    options=["Easy", "Medium", "Hard"],
    value="Medium",
    help="Easy = basic facts, Medium = detailed knowledge, Hard = obscure trivia.",
)

num_questions = st.sidebar.slider(
    "❓ Number of Questions",
    min_value=3,
    max_value=5,
    value=4,
    help="How many quiz questions to generate.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🧠 LLM Settings")

llm_provider = st.sidebar.selectbox(
    "🤖 LLM Provider",
    ["OpenAI", "Gemini"],
    index=0,
    help="Choose the model provider. If you get OpenAI 429 quota errors, switch to Gemini!",
)

api_key_override = st.sidebar.text_input(
    "🔑 API Key Override (Optional)",
    type="password",
    help="Paste your API key here to override the .env file settings.",
)

st.sidebar.markdown("---")

generate_btn = st.sidebar.button(
    "🚀 Generate Fresh Quiz",
    use_container_width=True,
    type="primary",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='text-align:center; font-size:0.75rem; color:#888;'>"
    "Powered by ChromaDB + DuckDuckGo + LLM<br>"
    "Built with Streamlit ❤️"
    "</p>",
    unsafe_allow_html=True,
)


# ── Session State Initialization ────────────────────────────────────────────────

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
    st.session_state.quiz_raw = None
    st.session_state.quiz_context = None
    st.session_state.quiz_sport = None
    st.session_state.quiz_difficulty = None
    st.session_state.user_answers = {}
    st.session_state.submitted = False


# ── Quiz Generation ─────────────────────────────────────────────────────────────

if generate_btn:
    with st.spinner("🔄 Fetching historical facts & scouring the live web..."):
        try:
            raw_text, context_used = compile_quiz_data(
                sport_choice,
                difficulty,
                num_questions,
                provider=llm_provider,
                api_key=api_key_override.strip() if api_key_override.strip() else None,
            )
            parsed = parse_quiz_questions(raw_text)

            if parsed:
                st.session_state.quiz_questions = parsed
                st.session_state.quiz_raw = raw_text
                st.session_state.quiz_context = context_used
                st.session_state.quiz_sport = sport_choice
                st.session_state.quiz_difficulty = difficulty
                st.session_state.user_answers = {}
                st.session_state.submitted = False
                st.success(
                    f"✅ Generated {len(parsed)} questions for "
                    f"**{sport_choice}** ({difficulty})!"
                )
            else:
                st.warning(
                    "⚠️ The AI returned a response but it could not be parsed into "
                    "quiz questions. Try generating again."
                )
                st.text_area("Raw LLM Output (for debugging)", raw_text, height=200)

        except Exception as e:
            st.error(f"❌ Failed to generate quiz: {e}")


# ── Quiz Display ────────────────────────────────────────────────────────────────

if st.session_state.quiz_questions:
    st.markdown(
        f"### 📝 {st.session_state.quiz_sport} Quiz — "
        f"{st.session_state.quiz_difficulty} Difficulty"
    )

    for i, q in enumerate(st.session_state.quiz_questions):
        st.markdown(
            f'<div class="quiz-card">'
            f'<span class="quiz-number">QUESTION {i + 1}</span>'
            f'<div class="quiz-question">{q["question"]}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # Build option labels
        option_labels = []
        option_keys = []
        for letter in ["A", "B", "C", "D"]:
            if letter in q.get("options", {}):
                option_labels.append(f"{letter}) {q['options'][letter]}")
                option_keys.append(letter)

        if option_labels:
            selected = st.radio(
                f"Your answer for Q{i + 1}:",
                option_labels,
                key=f"q_{i}",
                index=None,
                label_visibility="collapsed",
            )

            if selected:
                # Extract the letter from "A) ..."
                selected_letter = selected[0]
                st.session_state.user_answers[i] = selected_letter

    # ── Submit & Score ──────────────────────────────────────────────────────

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_btn = st.button(
            "✅ Submit Answers",
            use_container_width=True,
            type="primary",
            disabled=len(st.session_state.user_answers) == 0,
        )

    if submit_btn:
        st.session_state.submitted = True

    # ── Feedback Display ────────────────────────────────────────────────────

    if st.session_state.submitted:
        score = 0
        total = len(st.session_state.quiz_questions)

        st.markdown("### 📊 Results")

        for i, q in enumerate(st.session_state.quiz_questions):
            user_ans = st.session_state.user_answers.get(i)
            correct_ans = q.get("correct_answer", "")
            is_correct = user_ans == correct_ans

            if is_correct:
                score += 1

            if user_ans:
                if is_correct:
                    st.markdown(
                        f'<div class="correct-box">'
                        f"<strong>Q{i + 1}: ✅ Correct!</strong><br>"
                        f'<div class="explanation-text">{q["explanation"]}</div>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    correct_text = q.get("options", {}).get(correct_ans, correct_ans)
                    st.markdown(
                        f'<div class="incorrect-box">'
                        f"<strong>Q{i + 1}: ❌ Incorrect</strong> — "
                        f"Correct answer: <strong>{correct_ans}) {correct_text}</strong><br>"
                        f'<div class="explanation-text">{q["explanation"]}</div>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    f'<div class="incorrect-box">'
                    f"<strong>Q{i + 1}: ⏭️ Skipped</strong> — "
                    f"Correct answer: <strong>{correct_ans}</strong><br>"
                    f'<div class="explanation-text">{q["explanation"]}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Score banner
        percentage = (score / total * 100) if total > 0 else 0
        emoji = "🎉" if percentage >= 80 else "👏" if percentage >= 50 else "💪"

        st.markdown(
            f'<div class="score-banner">'
            f"<h2>{emoji} {score} / {total}</h2>"
            f"<p>You scored {percentage:.0f}%</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── RAG Context Inspector ───────────────────────────────────────────────

    st.markdown("---")
    with st.expander("🔍 Inspect RAG Context (Ground Truth Sources)"):
        st.markdown('<p class="context-header">Sources used to generate this quiz</p>', unsafe_allow_html=True)
        st.code(st.session_state.quiz_context, language="markdown")

    # ── Copy-Paste Export ───────────────────────────────────────────────────

    with st.expander("📋 Copy Quiz for Social Media"):
        st.text_area(
            "Raw quiz text (copy & paste to your socials)",
            value=st.session_state.quiz_raw,
            height=300,
            label_visibility="collapsed",
        )

else:
    # Empty state
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem; color: #888;">
            <p style="font-size: 3rem; margin-bottom: 0.5rem;">🎯</p>
            <h3 style="color: #555; font-weight: 600;">Ready to test your sports knowledge?</h3>
            <p>Select a sport and difficulty from the sidebar, then hit <strong>Generate Fresh Quiz</strong>!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
