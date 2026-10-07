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
            {
                "name": "Ch 1: Electric Charges and Fields",
                "url": "https://ncert.nic.in/textbook/pdf/leph101.pdf",
            },
            {
                "name": "Ch 2: Electrostatic Potential and Capacitance",
                "url": "https://ncert.nic.in/textbook/pdf/leph102.pdf",
            },
            {
                "name": "Ch 3: Current Electricity",
                "url": "https://ncert.nic.in/textbook/pdf/leph103.pdf",
            },
            {
                "name": "Ch 4: Moving Charges and Magnetism",
                "url": "https://ncert.nic.in/textbook/pdf/leph104.pdf",
            },
            {
                "name": "Ch 5: Magnetism and Matter",
                "url": "https://ncert.nic.in/textbook/pdf/leph105.pdf",
            },
            {
                "name": "Ch 6: Electromagnetic Induction",
                "url": "https://ncert.nic.in/textbook/pdf/leph106.pdf",
            },
            {
                "name": "Ch 7: Alternating Current",
                "url": "https://ncert.nic.in/textbook/pdf/leph107.pdf",
            },
            {
                "name": "Ch 8: Electromagnetic Waves",
                "url": "https://ncert.nic.in/textbook/pdf/leph108.pdf",
            },
            {
                "name": "Ch 9: Ray Optics and Optical Instruments",
                "url": "https://ncert.nic.in/textbook/pdf/leph109.pdf",
            },
            {
                "name": "Ch 10: Wave Optics",
                "url": "https://ncert.nic.in/textbook/pdf/leph110.pdf",
            },
            {
                "name": "Ch 11: Dual Nature of Radiation and Matter",
                "url": "https://ncert.nic.in/textbook/pdf/leph111.pdf",
            },
            {
                "name": "Ch 12: Atoms",
                "url": "https://ncert.nic.in/textbook/pdf/leph112.pdf",
            },
            {
                "name": "Ch 13: Nuclei",
                "url": "https://ncert.nic.in/textbook/pdf/leph113.pdf",
            },
            {
                "name": "Ch 14: Semiconductor Electronics",
                "url": "https://ncert.nic.in/textbook/pdf/leph114.pdf",
            },
        ],
        "Chemistry": [
            {
                "name": "Ch 1: Solutions",
                "url": "https://ncert.nic.in/textbook/pdf/lech101.pdf",
            },
            {
                "name": "Ch 2: Electrochemistry",
                "url": "https://ncert.nic.in/textbook/pdf/lech102.pdf",
            },
            {
                "name": "Ch 3: Chemical Kinetics",
                "url": "https://ncert.nic.in/textbook/pdf/lech103.pdf",
            },
            {
                "name": "Ch 4: d- and f-Block Elements",
                "url": "https://ncert.nic.in/textbook/pdf/lech104.pdf",
            },
            {
                "name": "Ch 5: Coordination Compounds",
                "url": "https://ncert.nic.in/textbook/pdf/lech105.pdf",
            },
            {
                "name": "Ch 6: Haloalkanes and Haloarenes",
                "url": "https://ncert.nic.in/textbook/pdf/lech106.pdf",
            },
            {
                "name": "Ch 7: Alcohols, Phenols and Ethers",
                "url": "https://ncert.nic.in/textbook/pdf/lech107.pdf",
            },
            {
                "name": "Ch 8: Aldehydes, Ketones and Carboxylic Acids",
                "url": "https://ncert.nic.in/textbook/pdf/lech108.pdf",
            },
            {
                "name": "Ch 9: Amines",
                "url": "https://ncert.nic.in/textbook/pdf/lech109.pdf",
            },
            {
                "name": "Ch 10: Biomolecules",
                "url": "https://ncert.nic.in/textbook/pdf/lech110.pdf",
            },
        ],
        "Mathematics": [
            {
                "name": "Ch 1: Relations and Functions",
                "url": "https://ncert.nic.in/textbook/pdf/lemh101.pdf",
            },
            {
                "name": "Ch 2: Inverse Trigonometric Functions",
                "url": "https://ncert.nic.in/textbook/pdf/lemh102.pdf",
            },
            {
                "name": "Ch 3: Matrices",
                "url": "https://ncert.nic.in/textbook/pdf/lemh103.pdf",
            },
            {
                "name": "Ch 4: Determinants",
                "url": "https://ncert.nic.in/textbook/pdf/lemh104.pdf",
            },
            {
                "name": "Ch 5: Continuity and Differentiability",
                "url": "https://ncert.nic.in/textbook/pdf/lemh105.pdf",
            },
            {
                "name": "Ch 6: Application of Derivatives",
                "url": "https://ncert.nic.in/textbook/pdf/lemh106.pdf",
            },
            {
                "name": "Ch 7: Integrals",
                "url": "https://ncert.nic.in/textbook/pdf/lemh107.pdf",
            },
            {
                "name": "Ch 8: Application of Integrals",
                "url": "https://ncert.nic.in/textbook/pdf/lemh108.pdf",
            },
            {
                "name": "Ch 9: Differential Equations",
                "url": "https://ncert.nic.in/textbook/pdf/lemh109.pdf",
            },
            {
                "name": "Ch 10: Vector Algebra",
                "url": "https://ncert.nic.in/textbook/pdf/lemh110.pdf",
            },
            {
                "name": "Ch 11: Three Dimensional Geometry",
                "url": "https://ncert.nic.in/textbook/pdf/lemh111.pdf",
            },
            {
                "name": "Ch 12: Linear Programming",
                "url": "https://ncert.nic.in/textbook/pdf/lemh112.pdf",
            },
            {
                "name": "Ch 13: Probability",
                "url": "https://ncert.nic.in/textbook/pdf/lemh113.pdf",
            },
        ],
    },
    "Class 11": {
        "Physics": [
            {
                "name": "Ch 1: Units and Measurement",
                "url": "https://ncert.nic.in/textbook/pdf/keph101.pdf",
            },
            {
                "name": "Ch 2: Motion in a Straight Line",
                "url": "https://ncert.nic.in/textbook/pdf/keph102.pdf",
            },
            {
                "name": "Ch 3: Motion in a Plane",
                "url": "https://ncert.nic.in/textbook/pdf/keph103.pdf",
            },
            {
                "name": "Ch 4: Laws of Motion",
                "url": "https://ncert.nic.in/textbook/pdf/keph104.pdf",
            },
            {
                "name": "Ch 5: Work, Energy and Power",
                "url": "https://ncert.nic.in/textbook/pdf/keph105.pdf",
            },
            {
                "name": "Ch 6: System of Particles and Rotational Motion",
                "url": "https://ncert.nic.in/textbook/pdf/keph106.pdf",
            },
            {
                "name": "Ch 7: Gravitation",
                "url": "https://ncert.nic.in/textbook/pdf/keph107.pdf",
            },
            {
                "name": "Ch 8: Mechanical Properties of Solids",
                "url": "https://ncert.nic.in/textbook/pdf/keph108.pdf",
            },
            {
                "name": "Ch 9: Mechanical Properties of Fluids",
                "url": "https://ncert.nic.in/textbook/pdf/keph109.pdf",
            },
            {
                "name": "Ch 10: Thermal Properties of Matter",
                "url": "https://ncert.nic.in/textbook/pdf/keph110.pdf",
            },
            {
                "name": "Ch 11: Thermodynamics",
                "url": "https://ncert.nic.in/textbook/pdf/keph111.pdf",
            },
            {
                "name": "Ch 12: Kinetic Theory",
                "url": "https://ncert.nic.in/textbook/pdf/keph112.pdf",
            },
            {
                "name": "Ch 13: Oscillations",
                "url": "https://ncert.nic.in/textbook/pdf/keph113.pdf",
            },
            {
                "name": "Ch 14: Waves",
                "url": "https://ncert.nic.in/textbook/pdf/keph114.pdf",
            },
        ],
        "Chemistry": [
            {
                "name": "Ch 1: Some Basic Concepts of Chemistry",
                "url": "https://ncert.nic.in/textbook/pdf/kech101.pdf",
            },
            {
                "name": "Ch 2: Structure of Atom",
                "url": "https://ncert.nic.in/textbook/pdf/kech102.pdf",
            },
            {
                "name": "Ch 3: Classification of Elements and Periodicity",
                "url": "https://ncert.nic.in/textbook/pdf/kech103.pdf",
            },
            {
                "name": "Ch 4: Chemical Bonding and Molecular Structure",
                "url": "https://ncert.nic.in/textbook/pdf/kech104.pdf",
            },
            {
                "name": "Ch 5: Chemical Thermodynamics",
                "url": "https://ncert.nic.in/textbook/pdf/kech105.pdf",
            },
            {
                "name": "Ch 6: Equilibrium",
                "url": "https://ncert.nic.in/textbook/pdf/kech106.pdf",
            },
            {
                "name": "Ch 7: Redox Reactions",
                "url": "https://ncert.nic.in/textbook/pdf/kech107.pdf",
            },
            {
                "name": "Ch 8: Organic Chemistry - Some Basic Principles & Techniques",
                "url": "https://ncert.nic.in/textbook/pdf/kech108.pdf",
            },
            {
                "name": "Ch 9: Hydrocarbons",
                "url": "https://ncert.nic.in/textbook/pdf/kech109.pdf",
            },
        ],
        "Mathematics": [
            {
                "name": "Ch 1: Sets",
                "url": "https://ncert.nic.in/textbook/pdf/kemh101.pdf",
            },
            {
                "name": "Ch 2: Relations and Functions",
                "url": "https://ncert.nic.in/textbook/pdf/kemh102.pdf",
            },
            {
                "name": "Ch 3: Trigonometric Functions",
                "url": "https://ncert.nic.in/textbook/pdf/kemh103.pdf",
            },
            {
                "name": "Ch 4: Complex Numbers and Quadratic Equations",
                "url": "https://ncert.nic.in/textbook/pdf/kemh104.pdf",
            },
            {
                "name": "Ch 5: Linear Inequalities",
                "url": "https://ncert.nic.in/textbook/pdf/kemh105.pdf",
            },
            {
                "name": "Ch 6: Permutations and Combinations",
                "url": "https://ncert.nic.in/textbook/pdf/kemh106.pdf",
            },
            {
                "name": "Ch 7: Binomial Theorem",
                "url": "https://ncert.nic.in/textbook/pdf/kemh107.pdf",
            },
            {
                "name": "Ch 8: Sequence and Series",
                "url": "https://ncert.nic.in/textbook/pdf/kemh108.pdf",
            },
            {
                "name": "Ch 9: Straight Lines",
                "url": "https://ncert.nic.in/textbook/pdf/kemh109.pdf",
            },
            {
                "name": "Ch 10: Conic Sections",
                "url": "https://ncert.nic.in/textbook/pdf/kemh110.pdf",
            },
            {
                "name": "Ch 11: Introduction to Three Dimensional Geometry",
                "url": "https://ncert.nic.in/textbook/pdf/kemh111.pdf",
            },
            {
                "name": "Ch 12: Limits and Derivatives",
                "url": "https://ncert.nic.in/textbook/pdf/kemh112.pdf",
            },
            {
                "name": "Ch 13: Statistics",
                "url": "https://ncert.nic.in/textbook/pdf/kemh113.pdf",
            },
            {
                "name": "Ch 14: Probability",
                "url": "https://ncert.nic.in/textbook/pdf/kemh114.pdf",
            },
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
        <p>Socratic Study Companion for Physics, Math, Chemistry, and Engineering Entrance Prep.</p>
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

# Grouped navigation options for better UX
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
    "<div style='color: #64748B; font-size: 0.75rem; text-align:"
    " center;'>Powered by Groq & Llama 3</div>",
    unsafe_allow_html=True,
)
# ==========================================
# SECTION 1: AI STUDY & DOUBT ASSISTANT
# ==========================================
if app_section == "🤖 AI Study & Doubt Assistant":
  st.subheader("🤖 AI Study & Doubt Assistant")
  st.markdown(
      "Choose whether you want to analyze a worksheet image with Socratic hints"
      " or break down a difficult concept."
  )

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
    st.markdown(
        "Snap a photo or upload an image. Aspirant AI will guide you"
        " step-by-step **without** giving away the final answer!"
    )

    input_method = st.radio(
        "Choose Input Method",
        ["📁 Upload from Gallery", "📷 Capture with Camera"],
        horizontal=True,
    )

    image = None
    if input_method == "📁 Upload from Gallery":
      uploaded_file = st.file_uploader(
          "Upload question image...", type=["jpg", "jpeg", "png"]
      )
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
          placeholder=(
              "e.g., I'm stuck on finding the moment of inertia component"
              " here."
          ),
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
                max_completion_tokens=8000,
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
    st.markdown(
        "Enter any topic, formula, or specific question to get an in-depth"
        " explanation tailored for competitive exams."
    )

    concept_query = st.text_input(
        "What concept or problem text would you like to explore?",
        placeholder=(
            "e.g., Explain the inductive effect or rotational kinematics"
            " equations."
        ),
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
                max_completion_tokens=8000,
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
# SECTION 2: AI FORMULA FLASHCARDS & SPACED REPETITION (SM-2)
# ==========================================
elif app_section == "⚡ AI Formula Flashcards (SM-2 Spaced Repetition)":
  st.subheader("⚡ Spaced Repetition Flashcard Engine (SM-2)")
  st.markdown(
      "Generate high-yield revision cards and track your memory retention with"
      " Harvard-grade spaced repetition intervals."
  )

  col_fc1, col_fc2 = st.columns(2, gap="medium")
  with col_fc1:
    fc_class = st.selectbox(
        "Target Class", ["Class 11", "Class 12"], key="fc_class"
    )
    fc_subject = st.selectbox(
        "Target Subject",
        ["Physics", "Chemistry", "Mathematics"],
        key="fc_subject",
    )
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
              max_completion_tokens=8000,
          )
          raw_json = chat_completion.choices[0].message.content.strip()
          if raw_json.startswith("```"):
            raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json)
            raw_json = re.sub(r"\s*```$", "", raw_json)

          # Fix unescaped backslashes commonly found in LaTeX strings (e.g. \frac -> \\frac)
          fixed_json = re.sub(
              r"\\(?![" + r'\\"/bfnrtu' + r"])", r"\\\\", raw_json
          )

          st.session_state.sm2_flashcards = json.loads(fixed_json)
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
        st.markdown(
            f"**Card {idx+1}:**"
            f" {clean_latex_output(card['front_question'])}"
        )
        with st.expander("👁️ Reveal Answer"):
          st.markdown(clean_latex_output(card["back_answer"]))

        rating = st.select_slider(
            f"Rate your recall for Card {idx+1} (SM-2 Interval):",
            options=["Blackout (0)", "Hard (2)", "Good (4)", "Easy (5)"],
            key=f"sm2_rate_{idx}",
        )
      st.markdown("---")
    st.success(
        "Your review ratings have been recorded for optimal interval"
        " scheduling! 🧠"
    )
# ==========================================
# SECTION 3: FEYNMAN TEACH-BACK SIMULATOR
# ==========================================
elif app_section == "🎓 Feynman Teach-Back Simulator":
  st.subheader("🎓 Feynman Technique Teach-Back Simulator")
  st.markdown(
      "True mastery is being able to explain complex physics or math simply."
      " Record your voice or type your explanation, and our Harvard-style AI"
      " professor will evaluate your clarity."
  )

  feynman_concept = st.text_input(
      "What concept are you teaching today?",
      placeholder=(
          "e.g., Electromagnetic Induction, Gauss's Law, or Chain Rule in"
          " Calculus"
      ),
      key="feynman_concept_input",
  )

  feynman_audio = st.audio_input(
      "🎙️ Click the microphone to explain the concept out loud:"
  )

  transcribed_explanation = ""
  if feynman_audio is not None:
    with st.spinner("Transcribing your audio using Whisper..."):
      try:
        audio_bytes = feynman_audio.read()
        transcription = client.audio.transcriptions.create(
            file=("feynman_audio.wav", audio_bytes),
            model="whisper-large-v3",
            response_format="text",
        )
        transcribed_explanation = transcription
        st.success(f'Successfully transcribed: "{transcribed_explanation}"')
      except Exception as e:
        st.error(f"Audio transcription failed: {e}")

  feynman_explanation = st.text_area(
      "Or type/edit your explanation here:",
      value=transcribed_explanation,
      placeholder=(
          "Type your explanation here without overly relying on jargon..."
      ),
      height=150,
      key="feynman_text_input",
  )

  if st.button("Evaluate My Teach-Back"):
    if feynman_concept and feynman_explanation:
      with st.spinner("evaluating your conceptual clarity..."):
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
                  {
                      "role": "system",
                      "content": (
                          "You are a rigorous Harvard STEM professor."
                      ),
                  },
                  {"role": "user", "content": FEYNMAN_PROMPT},
              ],
              max_completion_tokens=8000,
          )
          feedback = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.markdown("### 🏛️ Professor's Feedback & Socratic Prompt")
          st.markdown(feedback)
        except Exception as e:
          st.error(f"Evaluation failed: {e}")
    else:
      st.warning(
          "Please provide both a concept and your verbal or written"
          " explanation."
      )
# ==========================================
# SECTION 4: INTERACTIVE MOCK TEST & QUIZ GENERATOR
# ==========================================
elif app_section == "📝 Interactive Mock Test & Quiz Generator":
  st.subheader("📝 Interactive Mock Test & Quiz Generator")
  st.markdown(
      "Test your mastery with rigorous, elite-tier multiple-choice practice"
      " tests tailored for JEE Main and Advanced levels."
  )

  col_t1, col_t2, col_t3 = st.columns(3, gap="medium")
  with col_t1:
    quiz_class = st.selectbox(
        "Target Class", ["Class 11", "Class 12"], key="quiz_class"
    )
  with col_t2:
    quiz_subject = st.selectbox(
        "Target Subject",
        ["Physics", "Chemistry", "Mathematics"],
        key="quiz_subject",
    )
  with col_t3:
    quiz_difficulty = st.selectbox(
        "Difficulty Level",
        [
            "JEE Main (Moderate)",
            "JEE Advanced (Hard)",
            "Board Exam (Standard)",
        ],
        key="quiz_diff",
    )

  quiz_topic = st.text_input(
      "Enter Chapter or Topic for the Quiz",
      placeholder=(
          "e.g., Electrostatics, Limits and Derivatives, Chemical Bonding"
      ),
  )

  if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
  if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
  if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

  if st.button("Generate Practice Quiz"):
    if quiz_topic:
      with st.spinner(
          "Generating elite JEE-level practice questions and solutions..."
      ):
        QUIZ_PROMPT = """You are Aspirant AI, an elite IIT-JEE question paper setter (former IIT Professor). 
        Generate a rigorous 5-question multiple-choice practice quiz for {quiz_class} {quiz_subject} on the topic: '{quiz_topic}' at '{quiz_difficulty}' level.
        
        DIFFICULTY GUIDELINES:
        - If JEE Advanced (Hard): Include multi-concept integration, non-trivial boundary conditions, calculus-heavy derivations, or trick options designed to catch common conceptual errors. Avoid trivial direct formula substitution.
        - If JEE Main (Moderate): Include standard high-yield numerical application, statement-based questions, or tricky algebraic/conceptual twists typical of recent NTA papers.
        
        CRITICAL FORMATTING RULES:
        1. Wrap ALL mathematical expressions and variables in standard single dollar signs (e.g., $R$, $\\sigma$, $\\int_{0}^{R} ...$). Do NOT use parentheses like (\\frac{{...}}{{...}}).
        2. Ensure clean question text without repeating characters or variables.
        3. Format your output strictly as valid JSON matching this exact structure, with no markdown code blocks outside or extra text:
        [
          {{
            "question_number": 1,
            "question": "Advanced question text here using $...$ for math",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct_answer": "A",
            "explanation": "Rigorous, step-by-step advanced derivation and solution here using $...$ for math"
          }}
        ]""".format(
            quiz_class=quiz_class,
            quiz_subject=quiz_subject,
            quiz_topic=quiz_topic,
            quiz_difficulty=quiz_difficulty,
        )

        try:
          chat_completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "You are a JSON-only API that outputs valid JSON"
                          " array of questions. Always use $...$ for LaTeX"
                          " math expressions inside strings."
                      ),
                  },
                  {"role": "user", "content": QUIZ_PROMPT},
              ],
              max_completion_tokens=8000,
          )
          raw_content = chat_completion.choices[0].message.content.strip()
          if raw_content.startswith("```"):
            raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
            raw_content = re.sub(r"\s*```$", "", raw_content)

          parsed_data = None
          try:
            fixed_content = re.sub(
                r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", raw_content
            )
            parsed_data = json.loads(fixed_content)
          except Exception:
            py_ready = (
                raw_content.replace("true", "True")
                .replace("false", "False")
                .replace("null", "None")
            )
            parsed_data = ast.literal_eval(py_ready)

          st.session_state.quiz_data = parsed_data
          st.session_state.user_answers = {}
          st.session_state.quiz_submitted = False
          st.rerun()
        except Exception as e:
          st.error(
              f"Failed to generate and parse quiz data: {e}\n\nRaw output"
              f" received:\n{raw_content}"
          )
    else:
      st.warning("Please enter a chapter or topic for the quiz.")

  if st.session_state.quiz_data:
    st.markdown("---")
    st.markdown("### 📋 Quiz in Progress")

    for idx, q in enumerate(st.session_state.quiz_data):
      st.markdown(f"**Q{idx+1}: {clean_latex_output(q['question'])}**")
      options = q["options"]
      selected_option = st.radio(
          f"Select your answer for Q{idx+1}:",
          options,
          key=f"q_{idx}",
          index=(
              None
              if f"q_{idx}" not in st.session_state.user_answers
              else options.index(st.session_state.user_answers[f"q_{idx}"])
          ),
      )
      if selected_option:
        st.session_state.user_answers[f"q_{idx}"] = selected_option
      st.markdown("---")

    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
      if st.button("📤 Submit Quiz & View Score"):
        st.session_state.quiz_submitted = True
        st.rerun()
    with col_sub2:
      if st.button("🔄 Reset Quiz"):
        st.session_state.quiz_data = None
        st.session_state.user_answers = {}
        st.session_state.quiz_submitted = False
        st.rerun()

  if st.session_state.quiz_submitted and st.session_state.quiz_data:
    st.markdown("### 📊 Quiz Results & Solutions")
    score = 0
    total = len(st.session_state.quiz_data)

    for idx, q in enumerate(st.session_state.quiz_data):
      user_ans = st.session_state.user_answers.get(f"q_{idx}", "")
      correct_letter = q["correct_answer"].strip().upper()

      is_correct = False
      if user_ans and user_ans.strip().startswith(correct_letter):
        is_correct = True

      if is_correct:
        score += 1
        st.success(f"**Q{idx+1}: Correct!** 🎉")
      else:
        st.error(f"**Q{idx+1}: Incorrect.** (Your answer: {user_ans or 'None'})")

      st.markdown(f"**Correct Answer Option:** `{q['correct_answer']}`")
      st.markdown(f"**Explanation:** {clean_latex_output(q['explanation'])}")
      st.markdown("---")

    if "quiz_history" not in st.session_state:
      st.session_state.quiz_history = []

    quiz_identifier = f"{quiz_topic}_{score}_{total}"
    if not any(
        h.get("identifier") == quiz_identifier
        for h in st.session_state.quiz_history
    ):
      st.session_state.quiz_history.append({
          "identifier": quiz_identifier,
          "topic": quiz_topic,
          "subject": quiz_subject,
          "score": score,
          "total": total,
      })

    st.metric(
        label="Final Score",
        value=f"{score} / {total} ({int((score/total)*100)}%)",
    )
# ==========================================
# SECTION 5: VOICE-ASSISTED DOUBT SOLVER
# ==========================================
elif app_section == "🎙️ Voice-Assisted Doubt Solver":
  st.subheader("🎙️ Voice-Assisted & Text Doubt Solver")
  st.markdown(
      "Record your voice or type any difficult physics, chemistry, or math"
      " concept to receive a structured breakdown."
  )

  audio_file = st.audio_input("🎙️ Click the microphone to record your doubt:")

  transcribed_doubt = ""
  if audio_file is not None:
    with st.spinner("Transcribing your audio using Whisper..."):
      try:
        audio_bytes = audio_file.read()
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3",
            response_format="text",
        )
        transcribed_doubt = transcription
        st.success(f'Successfully transcribed: "{transcribed_doubt}"')
      except Exception as e:
        st.error(f"Audio transcription failed: {e}")

  doubt_input = st.text_area(
      "Type or edit your transcribed doubt here:",
      value=transcribed_doubt,
      placeholder=(
          "e.g., Explain why the terminal velocity of a spherical body depends"
          " on the square of its radius."
      ),
      height=120,
  )

  if st.button("Solve Doubt"):
    if doubt_input:
      with st.spinner("Generating expert solution..."):
        SOLVER_PROMPT = f"""You are Aspirant AI, an expert tutor for engineering entrance exams.
        Provide a structured, rigorous explanation for the following student doubt:
        '{doubt_input}'
        
        Structure your response as follows:
        1. **Core Concept Overview**: Define the primary principle or law.
        2. **Detailed Derivation / Explanation**: Step-by-step mathematical/conceptual derivation using LaTeX.
        3. **Formula & Key Takeaway**: The core result to remember for exams."""

        try:
          chat_completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "You are Aspirant AI, an expert tutor for STEM"
                          " competitive exams."
                      ),
                  },
                  {"role": "user", "content": SOLVER_PROMPT},
              ],
              max_completion_tokens=8000,
          )
          solution_text = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.markdown("### 💡 Expert Solution & Breakdown")
          st.markdown(solution_text)
        except Exception as e:
          st.error(f"Failed to generate solution: {e}")
    else:
      st.warning("Please record your voice or type a doubt first.")

# ==========================================
# SECTION 6: JEE/BOARD STUDY PLANNER & TRACKER
# ==========================================
elif app_section == "🎯 JEE/Board Study Planner & Tracker":
  st.subheader("🎯 JEE/Board Study Planner & Tracker")
  st.markdown(
      "Generate a custom study schedule tailored to your target exam date, and"
      " track your daily preparation progress."
  )

  col_p1, col_p2 = st.columns(2, gap="medium")
  with col_p1:
    planner_class = st.selectbox(
        "Target Class/Level",
        ["Class 11", "Class 12", "JEE Main Targeter"],
        key="planner_class",
    )
    target_exam_date = st.date_input(
        "Target Exam Date", value=date.today() + timedelta(days=90)
    )
  with col_p2:
    focus_subjects = st.multiselect(
        "Focus Subjects",
        ["Physics", "Chemistry", "Mathematics"],
        default=["Physics", "Chemistry", "Mathematics"],
    )
    study_hours = st.slider("Daily Study Hours Available", 2, 12, 6)

  if "study_plan_data" not in st.session_state:
    st.session_state.study_plan_data = None
  if "checked_topics" not in st.session_state:
    st.session_state.checked_topics = {}

  if st.button("Generate Custom Study Plan"):
    if focus_subjects:
      with st.spinner("Generating personalized study roadmap..."):
        PLANNER_PROMPT = f"""You are Aspirant AI, an expert exam strategist and study planner.
        Create a high-efficiency study plan for a student in {planner_class} studying {', '.join(focus_subjects)}.
        Target Exam Date: {target_exam_date}
        Daily study hours: {study_hours} hours.
        
        Provide a structured weekly or milestone-based study plan broken down into actionable phases, key chapters to cover, and weekly goals."""

        try:
          chat_completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {
                      "role": "system",
                      "content": "You are Aspirant AI, an expert study coach.",
                  },
                  {"role": "user", "content": PLANNER_PROMPT},
              ],
              max_completion_tokens=8000,
          )
          st.session_state.study_plan_data = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.session_state.checked_topics = {}
          st.rerun()
        except Exception as e:
          st.error(f"Failed to generate study plan: {e}")
    else:
      st.warning("Please select at least one focus subject.")

  if st.session_state.study_plan_data:
    st.markdown("---")
    st.markdown("### 🗓️ Your Personalized Study Roadmap")
    st.markdown(st.session_state.study_plan_data)

    st.markdown("---")
    st.markdown("### ✅ Quick Topic Completion Checklist")
    st.markdown("Check off major milestones as you complete them:")

    sample_milestones = [
        "Complete NCERT reading & solved examples",
        "Solve previous years' questions (PYQs) for the chapter",
        "Take timed chapter mock test",
        "Review formula revision flashcards",
    ]

    for idx, milestone in enumerate(sample_milestones):
      checked = st.checkbox(milestone, key=f"milestone_{idx}")
      st.session_state.checked_topics[milestone] = checked

    completed_count = sum(
        1 for v in st.session_state.checked_topics.values() if v
    )
    total_milestones = len(sample_milestones)
    progress_pct = int((completed_count / total_milestones) * 100)

    st.markdown(f"**Overall Milestone Progress: {progress_pct}%**")
    st.progress(progress_pct / 100.0)
# ==========================================
# SECTION 7: NCERT TEXTBOOK LIBRARY
# ==========================================
elif app_section == "📚 NCERT Textbook Library":
  st.subheader("📚 NCERT Textbook Library")
  st.markdown(
      "Access official Class 11 and Class 12 NCERT chapters directly for"
      " Physics, Chemistry, and Mathematics."
  )

  lib_class = st.selectbox(
      "Select Class", ["Class 11", "Class 12"], key="lib_class"
  )
  lib_subject = st.selectbox(
      "Select Subject",
      ["Physics", "Chemistry", "Mathematics"],
      key="lib_subject",
  )

  chapters = NCERT_FULL_DATABASE[lib_class][lib_subject]

  st.markdown(f"### {lib_class} — {lib_subject} Chapters")
  for ch in chapters:
    col_ch1, col_ch2 = st.columns([4, 1])
    with col_ch1:
      st.markdown(f"**{ch['name']}**")
    with col_ch2:
      st.markdown(f"[📥 Download PDF]({ch['url']})", unsafe_allow_html=True)
    st.markdown("---")
# ==========================================
# SECTION 8: AI PERFORMANCE ANALYTICS & WEAKNESS DIAGNOSTIC
# ==========================================
elif app_section == "📊 AI Performance Analytics & Weakness Diagnostic":
  st.subheader("📊 AI Performance Analytics & Weakness Diagnostic")
  st.markdown(
      "Analyze your mock test history, identify recurring weak areas, and get"
      " AI-driven revision prescriptions."
  )

  if (
      "quiz_history" not in st.session_state
      or not st.session_state.quiz_history
  ):
    st.info(
        "No quiz attempts recorded yet! Take a few practice quizzes in the"
        " **Interactive Mock Test & Quiz Generator** section to unlock"
        " performance analytics."
    )
  else:
    total_tests = len(st.session_state.quiz_history)
    total_correct = sum(item["score"] for item in st.session_state.quiz_history)
    total_questions = sum(
        item["total"] for item in st.session_state.quiz_history
    )
    overall_accuracy = (
        (total_correct / total_questions) * 100 if total_questions > 0 else 0
    )

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
      st.metric("Total Quizzes Taken", total_tests)
    with col_m2:
      st.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
    with col_m3:
      st.metric(
          "Subjects Tracked",
          len(set(item["subject"] for item in st.session_state.quiz_history)),
      )

    st.markdown("---")
    st.markdown("### 📈 Recent Quiz Performance History")

    for h in reversed(st.session_state.quiz_history):
      col_h1, col_h2, col_h3, col_h4 = st.columns([3, 2, 2, 2])
      with col_h1:
        st.markdown(f"**Topic:** {h['topic']}")
      with col_h2:
        st.markdown(f"**Subject:** {h['subject']}")
      with col_h3:
        st.markdown(f"**Score:** {h['score']} / {h['total']}")
      with col_h4:
        pct = (h["score"] / h["total"]) * 100
        if pct >= 80:
          st.success(f"{pct:.0f}% — Excellent")
        elif pct >= 50:
          st.warning(f"{pct:.0f}% — Moderate")
        else:
          st.error(f"{pct:.0f}% — Needs Work")
      st.markdown("---")

    st.markdown("### 🩺 AI Weakness Diagnostic & Revision Prescription")
    if "diagnostic_report" not in st.session_state:
      st.session_state.diagnostic_report = None

    if st.button("Generate AI Diagnostic Report"):
      with st.spinner(
          "Analyzing your quiz history and identifying knowledge gaps..."
      ):
        history_summary = "\n".join([
            f"- Subject: {h['subject']}, Topic: {h['topic']}, Score:"
            f" {h['score']}/{h['total']}"
            for h in st.session_state.quiz_history
        ])

        DIAGNOSTIC_PROMPT = f"""You are Aspirant AI, an expert exam strategist and analytical coach. 
        Based on the student's quiz attempt history below, analyze their weak areas, identify recurring mistakes or conceptual gaps, and provide a targeted 3-step revision prescription with high-yield focus topics.
        
        Quiz History:
        {history_summary}
        
        Provide a structured, encouraging diagnostic report with actionable recommendations."""

        try:
          chat_completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "You are Aspirant AI, an expert analytical study"
                          " coach."
                      ),
                  },
                  {"role": "user", "content": DIAGNOSTIC_PROMPT},
              ],
              max_completion_tokens=4000,
          )
          st.session_state.diagnostic_report = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.rerun()
        except Exception as e:
          st.error(f"Failed to generate diagnostic report: {e}")

    if st.session_state.diagnostic_report:
      st.markdown("---")
      st.markdown("### 📋 Your Personalized Diagnostic Report")
      st.markdown(st.session_state.diagnostic_report)
