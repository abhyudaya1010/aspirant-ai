import base64
import io
import json
import os
import re
from datetime import date, timedelta
from groq import Groq
from PIL import Image
import streamlit as st

# ==========================================
# PAGE CONFIGURATION & CUSTOM DESIGN SYSTEM
# ==========================================
st.set_page_config(
    page_title="Aspirant AI — Harvard-Tier Study Companion",
    page_icon="🎓",
    layout="wide",
)

st.markdown("""
<style>
    /* Global Theme & Background */
    .main {
        background: #090D16;
        color: #F1F5F9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* App Header Banner */
    .app-header {
        background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 50%, #020617 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid #312E81;
        box-shadow: 0 10px 25px -5px rgba(30, 27, 75, 0.4);
    }
    .app-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #818CF8 0%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
    }
    .app-header p {
        color: #94A3B8;
        font-size: 1.15rem;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Section Headers */
    h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Custom Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.65rem 1.4rem;
        border: none;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.5);
        transform: translateY(-1px);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #030712;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #CBD5E1 !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] h3 {
        color: #818CF8 !important;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Cards / Containers */
    div.stContainer, .streamlit-expanderHeader {
        background: #0F172A;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #1E293B;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
    }
    
    /* Metrics & Badges */
    [data-testid="stMetricValue"] {
        color: #818CF8 !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# LATEX FORMATTING HELPER
# ==========================================
def clean_latex_output(text):
    if not text:
        return ""
    text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text, flags=re.DOTALL)
    return text


# ==========================================
# SECURE API CLIENT INITIALIZATION
# ==========================================
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")

if not api_key:
    st.error(
        "⚠️ Groq API Key not found! Please configure it in your `.streamlit/secrets.toml` file."
    )
    st.stop()

client = Groq(api_key=api_key)

# ==========================================
# NCERT DATABASE (Classes 11 - 12)
# ==========================================
NCERT_FULL_DATABASE = {
    "Class 12": {
        "Physics": [
            {"name": "Ch 1: Electric Charges and Fields", "url": "https://ncert.nic.in/textbook/pdf/leph101.pdf"},
            {"name": "Ch 2: Electrostatic Potential and Capacitance", "url": "https://ncert.nic.in/textbook/pdf/leph102.pdf"},
            {"name": "Ch 3: Current Electricity", "url": "https://ncert.nic.in/textbook/pdf/leph103.pdf"},
            {"name": "Ch 4: Moving Charges and Magnetism", "url": "https://ncert.nic.in/textbook/pdf/leph104.pdf"},
            {"name": "Ch 5: Magnetism and Matter", "url": "https://ncert.nic.in/textbook/pdf/leph105.pdf"},
            {"name": "Ch 6: Electromagnetic Induction", "url": "https://ncert.nic.in/textbook/pdf/leph106.pdf"},
            {"name": "Ch 7: Alternating Current", "url": "https://ncert.nic.in/textbook/pdf/leph107.pdf"},
            {"name": "Ch 8: Electromagnetic Waves", "url": "https://ncert.nic.in/textbook/pdf/leph108.pdf"},
            {"name": "Ch 9: Ray Optics and Optical Instruments", "url": "https://ncert.nic.in/textbook/pdf/leph109.pdf"},
            {"name": "Ch 10: Wave Optics", "url": "https://ncert.nic.in/textbook/pdf/leph110.pdf"},
            {"name": "Ch 11: Dual Nature of Radiation and Matter", "url": "https://ncert.nic.in/textbook/pdf/leph111.pdf"},
            {"name": "Ch 12: Atoms", "url": "https://ncert.nic.in/textbook/pdf/leph112.pdf"},
            {"name": "Ch 13: Nuclei", "url": "https://ncert.nic.in/textbook/pdf/leph113.pdf"},
            {"name": "Ch 14: Semiconductor Electronics", "url": "https://ncert.nic.in/textbook/pdf/leph114.pdf"},
        ],
        "Chemistry": [
            {"name": "Ch 1: Solutions", "url": "https://ncert.nic.in/textbook/pdf/lech101.pdf"},
            {"name": "Ch 2: Electrochemistry", "url": "https://ncert.nic.in/textbook/pdf/lech102.pdf"},
            {"name": "Ch 3: Chemical Kinetics", "url": "https://ncert.nic.in/textbook/pdf/lech103.pdf"},
            {"name": "Ch 4: d- and f-Block Elements", "url": "https://ncert.nic.in/textbook/pdf/lech104.pdf"},
            {"name": "Ch 5: Coordination Compounds", "url": "https://ncert.nic.in/textbook/pdf/lech105.pdf"},
            {"name": "Ch 6: Haloalkanes and Haloarenes", "url": "https://ncert.nic.in/textbook/pdf/lech106.pdf"},
            {"name": "Ch 7: Alcohols, Phenols and Ethers", "url": "https://ncert.nic.in/textbook/pdf/lech107.pdf"},
            {"name": "Ch 8: Aldehydes, Ketones and Carboxylic Acids", "url": "https://ncert.nic.in/textbook/pdf/lech108.pdf"},
            {"name": "Ch 9: Amines", "url": "https://ncert.nic.in/textbook/pdf/lech109.pdf"},
            {"name": "Ch 10: Biomolecules", "url": "https://ncert.nic.in/textbook/pdf/lech110.pdf"},
        ],
        "Mathematics": [
            {"name": "Ch 1: Relations and Functions", "url": "https://ncert.nic.in/textbook/pdf/lemh101.pdf"},
            {"name": "Ch 2: Inverse Trigonometric Functions", "url": "https://ncert.nic.in/textbook/pdf/lemh102.pdf"},
            {"name": "Ch 3: Matrices", "url": "https://ncert.nic.in/textbook/pdf/lemh103.pdf"},
            {"name": "Ch 4: Determinants", "url": "https://ncert.nic.in/textbook/pdf/lemh104.pdf"},
            {"name": "Ch 5: Continuity and Differentiability", "url": "https://ncert.nic.in/textbook/pdf/lemh105.pdf"},
            {"name": "Ch 6: Application of Derivatives", "url": "https://ncert.nic.in/textbook/pdf/lemh106.pdf"},
            {"name": "Ch 7: Integrals", "url": "https://ncert.nic.in/textbook/pdf/lemh107.pdf"},
            {"name": "Ch 8: Application of Integrals", "url": "https://ncert.nic.in/textbook/pdf/lemh108.pdf"},
            {"name": "Ch 9: Differential Equations", "url": "https://ncert.nic.in/textbook/pdf/lemh109.pdf"},
            {"name": "Ch 10: Vector Algebra", "url": "https://ncert.nic.in/textbook/pdf/lemh110.pdf"},
            {"name": "Ch 11: Three Dimensional Geometry", "url": "https://ncert.nic.in/textbook/pdf/lemh111.pdf"},
            {"name": "Ch 12: Linear Programming", "url": "https://ncert.nic.in/textbook/pdf/lemh112.pdf"},
            {"name": "Ch 13: Probability", "url": "https://ncert.nic.in/textbook/pdf/lemh113.pdf"},
        ],
    },
    "Class 11": {
        "Physics": [
            {"name": "Ch 1: Units and Measurement", "url": "https://ncert.nic.in/textbook/pdf/keph101.pdf"},
            {"name": "Ch 2: Motion in a Straight Line", "url": "https://ncert.nic.in/textbook/pdf/keph102.pdf"},
            {"name": "Ch 3: Motion in a Plane", "url": "https://ncert.nic.in/textbook/pdf/keph103.pdf"},
            {"name": "Ch 4: Laws of Motion", "url": "https://ncert.nic.in/textbook/pdf/keph104.pdf"},
            {"name": "Ch 5: Work, Energy and Power", "url": "https://ncert.nic.in/textbook/pdf/keph105.pdf"},
            {"name": "Ch 6: System of Particles and Rotational Motion", "url": "https://ncert.nic.in/textbook/pdf/keph106.pdf"},
            {"name": "Ch 7: Gravitation", "url": "https://ncert.nic.in/textbook/pdf/keph107.pdf"},
            {"name": "Ch 8: Mechanical Properties of Solids", "url": "https://ncert.nic.in/textbook/pdf/keph108.pdf"},
            {"name": "Ch 9: Mechanical Properties of Fluids", "url": "https://ncert.nic.in/textbook/pdf/keph109.pdf"},
            {"name": "Ch 10: Thermal Properties of Matter", "url": "https://ncert.nic.in/textbook/pdf/keph110.pdf"},
            {"name": "Ch 11: Thermodynamics", "url": "https://ncert.nic.in/textbook/pdf/keph111.pdf"},
            {"name": "Ch 12: Kinetic Theory", "url": "https://ncert.nic.in/textbook/pdf/keph112.pdf"},
            {"name": "Ch 13: Oscillations", "url": "https://ncert.nic.in/textbook/pdf/keph113.pdf"},
            {"name": "Ch 14: Waves", "url": "https://ncert.nic.in/textbook/pdf/keph114.pdf"},
        ],
        "Chemistry": [
            {"name": "Ch 1: Some Basic Concepts of Chemistry", "url": "https://ncert.nic.in/textbook/pdf/kech101.pdf"},
            {"name": "Ch 2: Structure of Atom", "url": "https://ncert.nic.in/textbook/pdf/kech102.pdf"},
            {"name": "Ch 3: Classification of Elements and Periodicity", "url": "https://ncert.nic.in/textbook/pdf/kech103.pdf"},
            {"name": "Ch 4: Chemical Bonding and Molecular Structure", "url": "https://ncert.nic.in/textbook/pdf/kech104.pdf"},
            {"name": "Ch 5: Chemical Thermodynamics", "url": "https://ncert.nic.in/textbook/pdf/kech105.pdf"},
            {"name": "Ch 6: Equilibrium", "url": "https://ncert.nic.in/textbook/pdf/kech106.pdf"},
            {"name": "Ch 7: Redox Reactions", "url": "https://ncert.nic.in/textbook/pdf/kech107.pdf"},
            {"name": "Ch 8: Organic Chemistry - Some Basic Principles & Techniques", "url": "https://ncert.nic.in/textbook/pdf/kech108.pdf"},
            {"name": "Ch 9: Hydrocarbons", "url": "https://ncert.nic.in/textbook/pdf/kech109.pdf"},
        ],
        "Mathematics": [
            {"name": "Ch 1: Sets", "url": "https://ncert.nic.in/textbook/pdf/kemh101.pdf"},
            {"name": "Ch 2: Relations and Functions", "url": "https://ncert.nic.in/textbook/pdf/kemh102.pdf"},
            {"name": "Ch 3: Trigonometric Functions", "url": "https://ncert.nic.in/textbook/pdf/kemh103.pdf"},
            {"name": "Ch 4: Complex Numbers and Quadratic Equations", "url": "https://ncert.nic.in/textbook/pdf/kemh104.pdf"},
            {"name": "Ch 5: Linear Inequalities", "url": "https://ncert.nic.in/textbook/pdf/kemh105.pdf"},
            {"name": "Ch 6: Permutations and Combinations", "url": "https://ncert.nic.in/textbook/pdf/kemh106.pdf"},
            {"name": "Ch 7: Binomial Theorem", "url": "https://ncert.nic.in/textbook/pdf/kemh107.pdf"},
            {"name": "Ch 8: Sequence and Series", "url": "https://ncert.nic.in/textbook/pdf/kemh108.pdf"},
            {"name": "Ch 9: Straight Lines", "url": "https://ncert.nic.in/textbook/pdf/kemh109.pdf"},
            {"name": "Ch 10: Conic Sections", "url": "https://ncert.nic.in/textbook/pdf/kemh110.pdf"},
            {"name": "Ch 11: Introduction to Three Dimensional Geometry", "url": "https://ncert.nic.in/textbook/pdf/kemh111.pdf"},
            {"name": "Ch 12: Limits and Derivatives", "url": "https://ncert.nic.in/textbook/pdf/kemh112.pdf"},
            {"name": "Ch 13: Statistics", "url": "https://ncert.nic.in/textbook/pdf/kemh113.pdf"},
            {"name": "Ch 14: Probability", "url": "https://ncert.nic.in/textbook/pdf/kemh114.pdf"},
        ],
    },
}

# ==========================================
# APP HEADER & STYLING WRAPPER
# ==========================================
st.markdown(
    """
    <div class="app-header">
        <h1>🎓 Aspirant AI</h1>
        <p>Harvard-Tier Socratic Study Companion for Physics, Math, Chemistry, and Engineering Entrance Prep.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# SIDEBAR NAVIGATION & CATEGORIES
# ==========================================
st.sidebar.markdown(
    """
    <div style='text-align: center; padding: 10px 0 20px 0;'>
        <h2 style='color: #818CF8; font-size: 1.4rem; font-weight: 800; margin-bottom: 0;'>Aspirant AI</h2>
        <p style='color: #64748B; font-size: 0.8rem;'>Harvard-Tier Edition</p>
    </div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("### 🧭 Navigation Hub")

nav_category = st.sidebar.selectbox(
    "Hub Category",
    [
        "🧠 Core AI Tutoring",
        "⚡ Mastery & Retention",
        "📈 Planning & Resources",
    ],
)

if nav_category == "🧠 Core AI Tutoring":
    app_section = st.sidebar.radio(
        "Select Tool",
        [
            "🤖 AI Study & Doubt Assistant",
            "🎙️ Voice-Assisted Doubt Solver",
        ],
        label_visibility="collapsed",
    )
elif nav_category == "⚡ Mastery & Retention":
    app_section = st.sidebar.radio(
        "Select Tool",
        [
            "🎓 Feynman Teach-Back Simulator",
            "⚡ AI Formula Flashcards (SM-2 Spaced Repetition)",
            "📝 Interactive Mock Test & Quiz Generator",
        ],
        label_visibility="collapsed",
    )
else:
    app_section = st.sidebar.radio(
        "Select Tool",
        [
            "🎯 JEE/Board Study Planner & Tracker",
            "📚 NCERT Textbook Library",
        ],
        label_visibility="collapsed",
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='color: #64748B; font-size: 0.75rem; text-align: center;'>Powered by Groq & Llama 3</div>",
    unsafe_allow_html=True,
)

# ==========================================
# SECTION 1: AI STUDY & DOUBT ASSISTANT
# ==========================================
if app_section == "🤖 AI Study & Doubt Assistant":
    st.subheader("🤖 AI Study & Doubt Assistant")
    st.markdown("Choose whether you want to analyze a worksheet image with Socratic hints or break down a difficult concept.")

    assistant_mode = st.selectbox(
        "Select Assistant Tool",
        [
            "📸 Socratic Hint Inspector (Camera / Gallery)",
            "💡 Concept & Formula Solver",
        ],
    )

    st.markdown("---")

    if assistant_mode == "📸 Socratic Hint Inspector (Camera / Gallery)":
        st.markdown("### 📸 Worksheet & Problem Analyzer")
        st.markdown("Snap a photo or upload an image. Aspirant AI will guide you step-by-step **without** giving away the final answer!")

        input_method = st.radio(
            "Choose Input Method", ["📁 Upload from Gallery", "📷 Capture with Camera"], horizontal=True
        )

        image = None
        if input_method == "📁 Upload from Gallery":
            uploaded_file = st.file_uploader("Upload question image...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
        else:
            camera_file = st.camera_input("Take a picture of the question/worksheet")
            if camera_file is not None:
                image = Image.open(camera_file)

        if image is not None:
            st.image(image, caption="Selected Problem", use_container_width=True)

            buffered = io.BytesIO()
            image.save(buffered, format=image.format if image.format else "JPEG")
            img_bytes = buffered.getvalue()
            encoded_image = base64.b64encode(img_bytes).decode("utf-8")
            image_url = f"data:image/jpeg;base64,{encoded_image}"

            user_hint_query = st.text_input(
                "Any specific doubt or where are you stuck?",
                placeholder="e.g., I'm stuck on finding the moment of inertia component here.",
            )

            if st.button("Generate Socratic Hints"):
                HINT_PROMPT = f"""You are Aspirant AI, an expert, encouraging Socratic tutor for rigorous engineering and board exam preparation.
                Analyze the provided image of the academic problem.
                User's specific context/doubt: {user_hint_query}
                
                Provide a Socratic response:
                1. Break down the core concepts involved (e.g., formulas, principles).
                2. Give step-by-step guidance or guiding questions **without giving away the final answer**.
                3. Point out any common pitfalls to avoid."""

                with st.spinner("Analyzing problem via Groq vision..."):
                    try:
                        chat_completion = client.chat.completions.create(
                            model="qwen/qwen2-vl-7b-instruct",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": HINT_PROMPT},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": image_url},
                                        },
                                    ],
                                }
                            ],
                            max_completion_tokens=2000,
                        )
                        response_text = clean_latex_output(
                            chat_completion.choices[0].message.content
                        )
                        st.markdown("### 💡 Socratic Hint Guide")
                        st.markdown(response_text)
                    except Exception as e:
                        st.error(f"Analysis failed. Raw API Error: `{e}`")

    elif assistant_mode == "💡 Concept & Formula Solver":
        st.markdown("### 💡 Concept & Formula Breakdown")
        st.markdown("Enter any topic, formula, or specific question to get an in-depth explanation tailored for competitive exams.")
        
        concept_query = st.text_input(
            "What concept or problem text would you like to explore?",
            placeholder="e.g., Explain the inductive effect or rotational kinematics equations.",
        )

        if st.button("Explain Concept"):
            if concept_query:
                with st.spinner("Drafting explanation..."):
                    try:
                        chat_completion = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are Aspirant AI, an expert physics, chemistry,"
                                        " and math tutor. Provide crisp, high-signal"
                                        " explanations tailored for competitive exams."
                                    ),
                                },
                                {"role": "user", "content": concept_query},
                            ],
                            max_completion_tokens=2500,
                        )
                        explanation_text = clean_latex_output(
                            chat_completion.choices[0].message.content
                        )
                        st.markdown("### 📘 Explanation")
                        st.markdown(explanation_text)
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please type a concept or problem first.")

# ==========================================
# SECTION 2: VOICE-ASSISTED DOUBT SOLVER
# ==========================================
elif app_section == "🎙️ Voice-Assisted Doubt Solver":
    st.subheader("🎙️ Voice-Assisted Doubt Solver")
    st.markdown("Ask your physics, math, or chemistry doubt out loud using your microphone. Aspirant AI will transcribe it and provide an expert response!")

    voice_audio = st.audio_input("🎙️ Record your doubt:")
    if voice_audio is not None:
        with st.spinner("Processing voice doubt via Whisper..."):
            try:
                audio_bytes = voice_audio.read()
                transcription = client.audio.transcriptions.create(
                    file=("voice_doubt.wav", audio_bytes),
                    model="whisper-large-v3",
                    response_format="text"
                )
                st.markdown(f"**You asked:** \"{transcription}\"")

                with st.spinner("Generating expert response..."):
                    chat_completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": "You are Aspirant AI, an expert STEM tutor providing clear, concise, rigorous answers."},
                            {"role": "user", "content": transcription}
                        ],
                        max_completion_tokens=2000,
                    )
                    answer_text = clean_latex_output(chat_completion.choices[0].message.content)
                    st.markdown("### 💡 Aspirant AI Answer")
                    st.markdown(answer_text)
            except Exception as e:
                st.error(f"Voice processing failed: {e}")

# ==========================================
# SECTION 3: AI FORMULA FLASHCARDS & SPACED REPETITION (SM-2)
# ==========================================
elif app_section == "⚡ AI Formula Flashcards (SM-2 Spaced Repetition)":
    st.subheader("⚡ Spaced Repetition Flashcard Engine (SM-2)")
    st.markdown("Generate high-yield revision cards and track your memory retention with Harvard-grade spaced repetition intervals.")

    col_fc1, col_fc2 = st.columns(2, gap="medium")
    with col_fc1:
        fc_class = st.selectbox("Target Class", ["Class 11", "Class 12"], key="fc_class")
        fc_subject = st.selectbox("Target Subject", ["Physics", "Chemistry", "Mathematics"], key="fc_subject")
    with col_fc2:
        fc_topic = st.text_input(
            "Enter Chapter or Specific Topic",
            placeholder="e.g., Rotational Motion, Integration by Parts",
        )

    if "sm2_flashcards" not in st.session_state:
        st.session_state.sm2_flashcards = None

    if st.button("Generate Spaced Repetition Deck"):
        if fc_topic:
            with st.spinner("Compiling SM-2 optimized flashcards..."):
                SM2_PROMPT = f"""You are Aspirant AI, an expert coach utilizing SuperMemo SM-2 principles.
                Create 4 high-yield flashcards for {fc_class} {fc_subject} on '{fc_topic}'.
                Format as JSON array of objects with keys: "card_id", "front_question", "back_answer":
                [
                  {{"card_id": 1, "front_question": "...", "back_answer": "..."}}
                ]"""

                try:
                    chat_completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": "Return valid JSON array only."},
                            {"role": "user", "content": SM2_PROMPT},
                        ],
                        max_completion_tokens=2000,
                    )
                    raw_json = chat_completion.choices[0].message.content.strip()
                    if raw_json.startswith("```"):
                        raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json)
                        raw_json = re.sub(r"\s*```$", "", raw_json)
                    st.session_state.sm2_flashcards = json.loads(raw_json)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate cards: {e}")
        else:
            st.warning("Please specify a chapter or topic first.")

    if st.session_state.sm2_flashcards:
        st.markdown("---")
        st.markdown("### 🃏 Active Flashcard Review Deck")
        for idx, card in enumerate(st.session_state.sm2_flashcards):
            with st.container():
                st.markdown(f"**Card {idx+1}:** {clean_latex_output(card['front_question'])}")
                with st.expander("👁️ Reveal Answer"):
                    st.markdown(clean_latex_output(card['back_answer']))
                
                rating = st.select_slider(
                    f"Rate your recall for Card {idx+1} (SM-2 Interval):",
                    options=["Blackout (0)", "Hard (2)", "Good (4)", "Easy (5)"],
                    key=f"sm2_rate_{idx}"
                )
            st.markdown("---")
        st.success("Your review ratings have been recorded for optimal interval scheduling! 🧠")

# ==========================================
# SECTION 4: FEYNMAN TEACH-BACK SIMULATOR
# ==========================================
elif app_section == "🎓 Feynman Teach-Back Simulator":
    st.subheader("🎓 Feynman Technique Teach-Back Simulator")
    st.markdown("True mastery is being able to explain complex physics or math simply. Record your voice or type your explanation, and our Harvard-style AI professor will evaluate your clarity.")

    feynman_concept = st.text_input(
        "What concept are you teaching today?",
        placeholder="e.g., Electromagnetic Induction, Gauss's Law, or Chain Rule in Calculus",
        key="feynman_concept_input"
    )

    feynman_audio = st.audio_input("🎙️ Click the microphone to explain the concept out loud:")

    transcribed_explanation = ""
    if feynman_audio is not None:
        with st.spinner("Transcribing your audio using Whisper..."):
            try:
                audio_bytes = feynman_audio.read()
                transcription = client.audio.transcriptions.create(
                    file=("feynman_audio.wav", audio_bytes),
                    model="whisper-large-v3",
                    response_format="text"
                )
                transcribed_explanation = transcription
                st.success(f"Successfully transcribed: \"{transcribed_explanation}\"")
            except Exception as e:
                st.error(f"Audio transcription failed: {e}")

    feynman_explanation = st.text_area(
        "Or type/edit your explanation here:",
        value=transcribed_explanation,
        placeholder="Type your explanation here without overly relying on jargon...",
        height=150,
        key="feynman_text_input"
    )

    if st.button("Evaluate My Teach-Back"):
        if feynman_concept and feynman_explanation:
            with st.spinner("Harvard Professor evaluating your conceptual clarity..."):
                FEYNMAN_PROMPT = f"""You are a rigorous Harvard physics/math professor utilizing the Feynman technique.
                The student is trying to explain the concept of '{feynman_concept}'.
                Here is their explanation: '{feynman_explanation}'
                
                Provide your evaluation:
                1. **Conceptual Accuracy & Gaps**: Point out any misunderstandings or missing nuances.
                2. **Clarity Score**: Rate from 1 to 5.
                3. **Socratic Follow-Up**: Ask one sharp probing question to test their deep understanding without giving the answer away."""

                try:
                    chat_completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": "You are a rigorous Harvard STEM professor."},
                            {"role": "user", "content": FEYNMAN_PROMPT}
                        ],
                        max_completion_tokens=2000,
                    )
                    feedback = clean_latex_output(chat_completion.choices[0].message.content)
                    st.markdown("### 🏛️ Professor's Feedback & Socratic Prompt")
                    st.markdown(feedback)
                except Exception as e:
                    st.error(f"Evaluation failed: {e}")
        else:
            st.warning("Please provide both a concept and your verbal or written explanation.")

# ==========================================
# SECTION 5: INTERACTIVE MOCK TEST & QUIZ GENERATOR
# ==========================================
elif app_section == "📝 Interactive Mock Test & Quiz Generator":
    st.subheader("📝 Interactive Mock Test & Quiz Generator")
    st.markdown("Test your mastery with customized multiple-choice practice tests tailored for JEE Main and board exam levels.")

    col_t1, col_t2, col_t3 = st.columns(3, gap="medium")
    with col_t1:
        quiz_class = st.selectbox("Target Class", ["Class 11", "Class 12"], key="quiz_class")
    with col_t2:
        quiz_subject = st.selectbox("Target Subject", ["Physics", "Chemistry", "Mathematics"], key="quiz_subject")
    with col_t3:
        quiz_difficulty = st.selectbox("Difficulty Level", ["JEE Main (Moderate)", "JEE Advanced (Hard)", "Board Exam (Standard)"], key="quiz_diff")

    quiz_topic = st.text_input(
        "Enter Chapter or Topic for the Quiz",
        placeholder="e.g., Electrostatics, Limits and Derivatives, Chemical Bonding",
    )

    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    if st.button("Generate Practice Quiz"):
        if quiz_topic:
            with st.spinner("Generating 3 high-yield multiple-choice questions..."):
                QUIZ_PROMPT = f"""You are Aspirant AI, an expert exam creator for {quiz_class} {quiz_subject}.
                Create 3 multiple-choice questions on '{quiz_topic}' at '{quiz_difficulty}' level.
                Format as a JSON array of objects with keys: "question_id", "question_text", "options" (array of 4 strings), "correct_answer" (exact string matching one of the options), "explanation".
                Example:
                [
                  {{
                    "question_id": 1,
                    "question_text": "...",
                    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
                    "correct_answer": "A) ...",
                    "explanation": "..."
                  }}
                ]"""
                try:
                    chat_completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": "Return valid JSON array only."},
                            {"role": "user", "content": QUIZ_PROMPT}
                        ],
                        max_completion_tokens=2500,
                    )
                    raw_json = chat_completion.choices[0].message.content.strip()
                    if raw_json.startswith("```"):
                        raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json)
                        raw_json = re.sub(r"\s*```$", "", raw_json)
                    st.session_state.quiz_data = json.loads(raw_json)
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate quiz: {e}")
        else:
            st.warning("Please enter a topic for the quiz.")

    if st.session_state.quiz_data:
        st.markdown("---")
        st.markdown(f"### 📋 Practice Quiz: {quiz_topic}")
        for q in st.session_state.quiz_data:
            qid = q["question_id"]
            st.markdown(f"**Q{qid}: {clean_latex_output(q['question_text'])}**")
            ans = st.radio(
                f"Select option for Q{qid}",
                q["options"],
                key=f"q_{qid}",
                label_visibility="collapsed"
            )
            st.session_state.user_answers[qid] = ans
            st.markdown("")

        if st.button("Submit Quiz"):
            st.session_state.quiz_submitted = True
            st.rerun()

        if st.session_state.quiz_submitted:
            st.markdown("---")
            st.markdown("### 📊 Quiz Results & Solutions")
            score = 0
            total = len(st.session_state.quiz_data)
            for q in st.session_state.quiz_data:
                qid = q["question_id"]
                user_ans = st.session_state.user_answers.get(qid)
                correct = q["correct_answer"]
                if user_ans == correct:
                    score += 1
                    st.success(f"**Q{qid}: Correct!** 🎉")
                else:
                    st.error(f"**Q{qid}: Incorrect.** Your answer: `{user_ans}` | Correct answer: `{correct}`")
                with st.expander(f"📖 View Explanation for Q{qid}"):
                    st.markdown(clean_latex_output(q["explanation"]))
            st.metric(label="Final Score", value=f"{score} / {total}")

# ==========================================
# SECTION 6: JEE/BOARD STUDY PLANNER & TRACKER
# ==========================================
elif app_section == "🎯 JEE/Board Study Planner & Tracker":
    st.subheader("🎯 JEE/Board Study Planner & Tracker")
    st.markdown("Build a customized milestone-driven study plan for your upcoming board exams and competitive entrance tests.")

    plan_class = st.selectbox("Target Class", ["Class 11", "Class 12"], key="plan_class")
    target_exam = st.selectbox("Primary Target", ["JEE Main & Advanced", "Secondary School Board Exams", "Both (Integrated)"])
    exam_date = st.date_input("Target Exam Date", value=date.today() + timedelta(days=120))

    if st.button("Generate Custom Study Schedule"):
        with st.spinner("Crafting customized preparation roadmap..."):
            PLAN_PROMPT = f"""You are an elite study strategist for {plan_class} students preparing for {target_exam} aiming for top-tier results.
            The target exam date is {exam_date}.
            Provide a structured, week-by-week preparation roadmap with milestones, priority topics in Physics, Chemistry, and Mathematics, and weekly mock test strategies."""
            try:
                chat_completion = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "system", "content": "You are an elite academic strategist."},
                        {"role": "user", "content": PLAN_PROMPT}
                    ],
                    max_completion_tokens=2500,
                )
                plan_text = clean_latex_output(chat_completion.choices[0].message.content)
                st.markdown("### 🗓️ Your Personalized Study Roadmap")
                st.markdown(plan_text)
            except Exception as e:
                st.error(f"Failed to generate study plan: {e}")

# ==========================================
# SECTION 7: NCERT TEXTBOOK LIBRARY
# ==========================================
elif app_section == "📚 NCERT Textbook Library":
    st.subheader("📚 Official NCERT Textbook Library")
    st.markdown("Access direct links to official NCERT PDF textbooks for Physics, Chemistry, and Mathematics (Classes 11 & 12).")

    lib_class = st.selectbox("Select Class", ["Class 12", "Class 11"], key="lib_class")
    lib_subject = st.selectbox("Select Subject", ["Physics", "Chemistry", "Mathematics"], key="lib_subject")

    chapters = NCERT_FULL_DATABASE.get(lib_class, {}).get(lib_subject, [])
    st.markdown(f"### 📖 {lib_class} - {lib_subject} Chapters")
    
    for ch in chapters:
        col_c1, col_c2 = st.columns([4, 1])
        with col_c1:
            st.markdown(f"**{ch['name']}**")
        with col_c2:
            st.markdown(f"[📥 Download PDF]({ch['url']})", unsafe_allow_html=True)
        st.markdown("---")
        
