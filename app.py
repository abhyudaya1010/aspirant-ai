import base64
import io
import os
import re
from groq import Groq
from PIL import Image
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Aspirant AI - Socratic Study Companion",
    page_icon="🎓",
    layout="wide",
)


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
# APP UI & HEADER
# ==========================================
st.title("🎓 Aspirant AI")
st.markdown(
    "Your intelligent Socratic study companion for Physics, Math, Chemistry, and"
    " Engineering Entrance Prep."
)

# Sidebar configuration
st.sidebar.header("Control Panel")
study_mode = st.sidebar.selectbox(
    "Select Mode",
    [
        "📚 NCERT Textbook Reader (Class 11-12)",
        "📸 Socratic Hint Inspector (Image/Worksheet)",
        "💡 Concept & Problem Solver",
    ],
)

# ==========================================
# MODE 1: NCERT TEXTBOOK READER
# ==========================================
if study_mode == "📚 NCERT Textbook Reader (Class 11-12)":
  st.subheader("📖 Official NCERT Textbook Portal")
  col_c, col_s = st.columns([1, 1], gap="medium")
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
    with st.container(border=True):
      col1, col2 = st.columns([4, 1])
      with col1:
        st.markdown(f"**{ch['name']}**")
      with col2:
        st.markdown(
            f'<a href="{ch["url"]}" target="_blank">'
            '<button style="width:100%; background-color:#2563EB; color:white;'
            " border:none; padding:8px 12px; border-radius:4px;"
            ' font-weight:bold; cursor:pointer;">Open PDF ↗</button>'
            "</a>",
            unsafe_allow_html=True,
        )

# ==========================================
# MODE 2: SOCRATIC HINT INSPECTOR
# ==========================================
elif study_mode == "📸 Socratic Hint Inspector (Image/Worksheet)":
  st.subheader("📸 Socratic Worksheet & Problem Analyzer")
  st.markdown(
      "Upload an image of your question or worksheet. Aspirant AI will give"
      " you conceptual hints **without** spoiling the final answer!"
  )

  uploaded_file = st.file_uploader(
      "Upload question image...", type=["jpg", "jpeg", "png"]
  )

  if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Problem", use_container_width=True)

    # Convert uploaded image to base64 data URL for the API
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
              max_completion_tokens=800,
          )
          response_text = clean_latex_output(
              chat_completion.choices[0].message.content
          )
          st.markdown("### 💡 Socratic Hint Guide")
          st.markdown(response_text)
        except Exception as e:
          st.error(f"Analysis failed. Raw API Error: `{e}`")

# ==========================================
# MODE 3: CONCEPT & PROBLEM SOLVER
# ==========================================
elif study_mode == "💡 Concept & Problem Solver":
  st.subheader("📚 Quick Concept & Formula Breakdown")
  concept_query = st.text_input(
      "What concept, formula, or problem text would you like to explore?",
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
              max_completion_tokens=1024,
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
