import base64
import io
import os
import re
from groq import Groq
from PIL import Image
import streamlit as st

# ==========================================
# PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="Aspirant AI — Advanced Study Companion",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
    /* Global Theme Styling */
    .main {
        background-color: #F8FAFC;
    }
    
    /* App Header Styling */
    .app-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .app-header h1 {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    .app-header p {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 0;
    }

    /* Section Headers */
    h2, h3 {
        color: #1E293B;
        font-weight: 700;
    }

    /* Custom Buttons */
    .stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    .stButton > button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    section[data-testid="stSidebar"] .stSelectbox label, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span {
        color: #F8FAFC !important;
    }

    /* Cards / Containers */
    div.stContainer {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 0.75rem;
    }

    /* ========================================== */
    /* FLOATING ROBOT & POPUP CARD STYLES         */
    /* ========================================== */
    @keyframes floatRobot {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); }
        70% { box-shadow: 0 0 0 14px rgba(37, 99, 235, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
    }

    .floating-robot-wrapper {
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 99999;
    }

    .floating-robot-wrapper div.stButton > button {
        width: 64px !important;
        height: 64px !important;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%), url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H15A2,2 0 0,1 17,9V18A2,2 0 0,1 15,20H9A2,2 0 0,1 7,18V9A2,2 0 0,1 9,7H11V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M12,4A1,1 0 0,0 11,5A1,1 0 0,0 12,6A1,1 0 0,0 13,5A1,1 0 0,0 12,4M9,9V13H15V9H9M10,15A1,1 0 0,0 9,16A1,1 0 0,0 10,17A1,1 0 0,0 11,16A1,1 0 0,0 10,15M14,15A1,1 0 0,0 13,16A1,1 0 0,0 14,17A1,1 0 0,0 15,16A1,1 0 0,0 14,15Z'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 32px 32px !important;
        border-radius: 50% !important;
        color: transparent !important;
        font-size: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        animation: floatRobot 3s ease-in-out infinite, pulseGlow 2.5s infinite;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.5) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        padding: 0 !important;
        cursor: pointer !important;
        transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .floating-robot-wrapper div.stButton > button:hover {
        transform: scale(1.12) rotate(6deg) !important;
        background-color: #1D4ED8 !important;
    }

    /* Floating Popup Modal Window (Pinned directly above robot) */
    .floating-modal-backdrop {
        position: fixed;
        bottom: 105px;
        right: 25px;
        width: 380px;
        max-height: 82vh;
        overflow-y: auto;
        background: #0F172A;
        border: 2px solid #2563EB;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        z-index: 99998;
    }

    .floating-answer-box {
        background: #1E293B;
        padding: 12px;
        border-radius: 8px;
        margin-top: 12px;
        color: #F8FAFC;
        font-size: 0.95rem;
        max-height: 250px;
        overflow-y: auto;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State for Quick Voice Mode Toggle
if "voice_modal_active" not in st.session_state:
  st.session_state.voice_modal_active = False


# ==========================================
# LATEX FORMATTING HELPER
# ==========================================
def clean_latex_output(text):
  """Converts raw LaTeX notations so they render cleanly in Streamlit."""
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
# NCERT DATABASE (Classes 9 - 12)
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
                "name": (
                    "Ch 8: Organic Chemistry - Some Basic Principles &"
                    " Techniques"
                ),
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
                "name": (
                    "Ch 11: Introduction to Three Dimensional Geometry"
                ),
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
        <h1>🤖 Aspirant AI</h1>
        <p>Your intelligent Socratic study companion for Physics, Math, Chemistry, and Engineering Entrance Prep.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Sidebar configuration - Navigation
st.sidebar.markdown("### ⚙️ Navigation")
app_section = st.sidebar.radio(
    "Select Feature Hub",
    [
        "🤖 AI Study & Doubt Assistant",
        "⚡ AI Formula & Revision Flashcards",
        "📝 Interactive Mock Test & Quiz Generator",
        "🎙️ Voice-Assisted Doubt Solver",
        "📚 NCERT Textbook Library",
    ],
)

# ==========================================
# FLOATING ROBOT LOGO & POPUP WIDGET
# ==========================================
st.markdown('<div class="floating-robot-wrapper">', unsafe_allow_html=True)
if st.button("", help="Click to open AI Voice Doubt Solver!"):
  st.session_state.voice_modal_active = not st.session_state.voice_modal_active
st.markdown("</div>", unsafe_allow_html=True)

# Floating Voice Modal Card Popup
if st.session_state.voice_modal_active:
  st.markdown('<div class="floating-modal-backdrop">', unsafe_allow_html=True)
  with st.container():
    st.markdown("""
        <div>
            <h3 style="color: white; margin-top: 0; margin-bottom: 4px; font-size: 1.15rem;">🎙️ AI Voice & Dictation Assistant</h3>
            <p style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;">Dictate or type your doubt for an instant breakdown.</p>
        </div>
        """, unsafe_allow_html=True)

    voice_doubt_input = st.text_area(
        "Dictate or type your problem description:",
        placeholder=(
            "e.g., What is the condition for maximum power transfer?"
        ),
        key="floating_voice_input",
        label_visibility="collapsed",
    )

    col_vm1, col_vm2 = st.columns(2)
    with col_vm1:
      solve_floating_btn = st.button(
          "🚀 Solve Doubt", key="floating_solve_btn", use_container_width=True
      )
    with col_vm2:
      close_floating_btn = st.button(
          "❌ Close", key="close_modal_btn", use_container_width=True
      )

    if close_floating_btn:
      st.session_state.voice_modal_active = False
      st.rerun()

    if solve_floating_btn:
      if voice_doubt_input:
        with st.spinner("Resolving..."):
          VOICE_PROMPT = f"""You are Aspirant AI, an expert physics, chemistry, and mathematics tutor for engineering entrance exams.
            A student has asked the following question via voice dictation:
            '{voice_doubt_input}'
            
            Provide a structured, rigorous, yet intuitive explanation:
            1. **Core Concept Overview**: Briefly define the main principle.
            2. **Step-by-Step Breakdown**: Clear mathematical or conceptual steps using LaTeX.
            3. **Key Takeaway / Formula**: The ultimate result to remember for exams."""

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
                    {"role": "user", "content": VOICE_PROMPT},
                ],
                max_completion_tokens=2000,
            )
            voice_response = clean_latex_output(
                chat_completion.choices[0].message.content
            )
            st.markdown('<div class="floating-answer-box">', unsafe_allow_html=True)
            st.markdown("**Answer & Explanation:**")
            st.markdown(voice_response)
            st.markdown("</div>", unsafe_allow_html=True)
          except Exception as e:
            st.error(f"Failed to generate explanation: {e}")
      else:
        st.warning("Please dictate or type your doubt first.")
  st.markdown("</div>", unsafe_allow_html=True)

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

  # Sub-mode 1: Socratic Hint Inspector
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
                model="qwen/qwen3.8-27b",
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

  # Sub-mode 2: Concept & Problem Solver
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
# SECTION 2: AI FORMULA & REVISION FLASHCARDS
# ==========================================
elif app_section == "⚡ AI Formula & Revision Flashcards":
  st.subheader("⚡ AI Formula & Quick Revision Deck")
  st.markdown("Generate high-yield revision flashcards for any chapter or sub-topic to boost retention for engineering entrance and board exams.")

  col_fc1, col_fc2 = st.columns(2, gap="medium")
  with col_fc1:
    fc_class = st.selectbox("Target Class", ["Class 11", "Class 12"], key="fc_class")
    fc_subject = st.selectbox("Target Subject", ["Physics", "Chemistry", "Mathematics"], key="fc_subject")
  with col_fc2:
    fc_topic = st.text_input(
        "Enter Chapter or Specific Topic",
        placeholder="e.g., Rotational Motion, Integration by Parts, Chemical Kinetics",
    )

  if st.button("Generate Flashcard Deck"):
    if fc_topic:
      with st.spinner("Compiling high-yield revision flashcards..."):
        FLASHCARD_PROMPT = f"""You are Aspirant AI, an expert coach for engineering entrance examinations.
        Create a concise, high-yield revision flashcard deck for {fc_class} {fc_subject} focusing on the topic: '{fc_topic}'.
        
        Provide the output formatted into 4 clear flashcards:
        1. **Core Formulas & Definitions** (Key mathematical expressions and standard constants)
        2. **Key Concepts & Theorems** (Core principles needed to solve problems)
        3. **Shortcuts & Tricks** (Mental models or shortcut formulas for fast problem-solving)
        4. **Common Traps / Pitfalls** (Where students usually make mistakes)
        
        Use clear formatting with Markdown and LaTeX for equations."""

        try:
          chat_completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {
                      "role": "system",
                      "content": "You are Aspirant AI, an expert study coach for STEM competitive exams.",
                  },
                  {"role": "user", "content": FLASHCARD_PROMPT},
              ],
              max_completion_tokens=2500,
          )
          flashcards_text = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.markdown("### 🃏 Your Revision Flashcards")
          st.markdown(flashcards_text)
        except Exception as e:
          st.error(f"Failed to generate flashcards: {e}")
    else:
      st.warning("Please specify a chapter or topic first.")

# ==========================================
# SECTION 3: INTERACTIVE MOCK TEST & QUIZ GENERATOR
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
      with st.spinner("Generating custom mock test questions..."):
        QUIZ_PROMPT = f"""You are Aspirant AI, an expert engineering entrance exam test creator.
        Generate a 5-question multiple-choice practice quiz for {quiz_class} {quiz_subject} on the topic: '{quiz_topic}' at '{quiz_difficulty}' level.
        
        You MUST format your response strictly as a clear list of 5 questions. For each question, provide:
        - **Question [Number]**: [Question text with LaTeX for math/physics expressions]
        - **A)** [Option A]
        - **B)** [Option B]
        - **C)** [Option C]
        - **D)** [Option D]
        - **Correct Answer**: [A, B, C, or D]
        - **Explanation**: [Step-by-step solution]
        
        Ensure options are clearly labeled and the correct answer and explanation are explicitly provided at the end of each question."""

        try:
          chat_completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {
                      "role": "system",
                      "content": "You are Aspirant AI, an expert exam creator for STEM competitive exams.",
                  },
                  {"role": "user", "content": QUIZ_PROMPT},
              ],
              max_completion_tokens=3000,
          )
          st.session_state.quiz_data = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.session_state.user_answers = {}
          st.session_state.quiz_submitted = False
        except Exception as e:
          st.error(f"Failed to generate quiz: {e}")
    else:
      st.warning("Please specify a chapter or topic first.")

  if st.session_state.quiz_data:
    st.markdown("---")
    st.markdown("### 📋 Your Custom Practice Test")
    st.markdown(st.session_state.quiz_data)
    
    st.markdown("---")
    st.markdown("### ✨ Test Submission & Evaluation")
    st.markdown("Want an AI evaluation of your answers or want to test yourself further? Enter your selected answers below (e.g., Q1: A, Q2: C, etc.) or click below to check your solutions.")

    eval_input = st.text_area(
        "Enter your answers or any doubts on specific questions:",
        placeholder="e.g., My answers are: 1-B, 2-C, 3-A, 4-D, 5-B. Please evaluate my score and explain any mistakes.",
    )

    if st.button("Evaluate Answers & Get Detailed Solutions"):
      if eval_input:
        with st.spinner("Evaluating your performance..."):
          EVAL_PROMPT = f"""You are Aspirant AI, an expert exam coach. 
          Here is the quiz that was generated:
          {st.session_state.quiz_data}
          
          Here are the user's submitted answers / notes:
          {eval_input}
          
          Please grade the user's answers against the correct answers, calculate their total score out of 5, and provide detailed step-by-step corrections for any incorrect answers."""

          try:
            eval_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Aspirant AI, an expert tutor grading mock tests.",
                    },
                    {"role": "user", "content": EVAL_PROMPT},
                ],
                max_completion_tokens=2000,
            )
            eval_result = clean_latex_output(
                eval_completion.choices[0].message.content
            )
            st.markdown("### 📊 Performance Report & Solutions")
            st.markdown(eval_result)
          except Exception as e:
            st.error(f"Evaluation failed: {e}")
      else:
        st.warning("Please enter your answers before submitting for evaluation.")

# ==========================================
# SECTION 4: VOICE-ASSISTED DOUBT SOLVER
# ==========================================
elif app_section == "🎙️ Voice-Assisted Doubt Solver":
  st.subheader("🎙️ Voice & Dictation Doubt Solver")
  st.markdown("Dictate your physics, chemistry, or mathematics questions directly via voice input (or type them) to receive instant, crystal-clear explanations.")

  voice_doubt_input = st.text_area(
      "Dictate or type your problem description:",
      placeholder="e.g., What is the condition for maximum power transfer in a DC circuit, and how is it derived?",
      help="You can use your browser/device voice-to-text keyboard dictation feature to speak your doubt directly into this box!",
  )

  col_v1, col_v2 = st.columns([1, 4], vertical_alignment="center")
  with col_v1:
    solve_voice_btn = st.button("Solve Doubt")

  if solve_voice_btn:
    if voice_doubt_input:
      with st.spinner("Resolving your doubt..."):
        VOICE_PROMPT = f"""You are Aspirant AI, an expert physics, chemistry, and mathematics tutor for engineering entrance exams.
        A student has asked the following question via voice dictation:
        '{voice_doubt_input}'
        
        Provide a structured, rigorous, yet intuitive explanation:
        1. **Core Concept Overview**: Briefly define the main principle.
        2. **Step-by-Step Breakdown / Derivation**: Clear mathematical or conceptual steps using LaTeX.
        3. **Key Takeaway / Formula**: The ultimate result to remember for exams."""

        try:
          chat_completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {
                      "role": "system",
                      "content": "You are Aspirant AI, an expert tutor for STEM competitive exams.",
                  },
                  {"role": "user", "content": VOICE_PROMPT},
              ],
              max_completion_tokens=2500,
          )
          voice_response = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.markdown("### 🎧 Answer & Explanation")
          st.markdown(voice_response)
        except Exception as e:
          st.error(f"Failed to generate explanation: {e}")
    else:
      st.warning("Please dictate or type your doubt first.")

# ==========================================
# SECTION 5: NCERT TEXTBOOK LIBRARY
# ==========================================
elif app_section == "📚 NCERT Textbook Library":
  st.subheader("📖 Official NCERT Textbook Library")
  st.markdown("Select your class and subject to directly access verified curriculum textbooks and PDFs.")
  
  col_c, col_s = st.columns(2, gap="medium")
  with col_c:
    selected_class = st.selectbox("Select Class", list(NCERT_FULL_DATABASE.keys()))
  with col_s:
    selected_subject = st.selectbox(
        "Select Subject", list(NCERT_FULL_DATABASE[selected_class].keys())
    )

  st.markdown("---")
  chapters = NCERT_FULL_DATABASE[selected_class][selected_subject]
  st.markdown(
      f"**Showing {len(chapters)} official chapters for {selected_class} —"
      f" {selected_subject}**"
  )

  for ch in chapters:
    with st.container():
      col1, col2 = st.columns([4, 1], vertical_alignment="center")
      with col1:
        st.markdown(f"**{ch['name']}**")
      with col2:
        st.markdown(
            f'<a href="{ch["url"]}" target="_blank" style="text-decoration: none;">'
            '<button style="width:100%; background-color:#2563EB; color:white;'
            " border:none; padding:8px 12px; border-radius:6px;"
            ' font-weight:600; cursor:pointer;">Open PDF ↗</button>'
            "</a>",
            unsafe_allow_html=True,
        )
