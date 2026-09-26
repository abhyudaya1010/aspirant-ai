import base64
import io
import os
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
        "Socratic Hint Inspector (Image/Worksheet)",
        "Concept & Problem Solver",
    ],
)

# ==========================================
# MODE 1: SOCRATIC HINT INSPECTOR
# ==========================================
if study_mode == "Socratic Hint Inspector (Image/Worksheet)":
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
    st.image(image, caption="Uploaded Problem", width="stretch")

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
          # Capped max_completion_tokens to prevent hitting free tier rate limits (OTPM)
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
          response_text = chat_completion.choices[0].message.content
          st.markdown("### 💡 Socratic Hint Guide")
          st.markdown(response_text)
        except Exception as e:
          st.error(f"Analysis failed. Raw API Error: `{e}`")

# ==========================================
# MODE 2: CONCEPT & PROBLEM SOLVER
# ==========================================
elif study_mode == "Concept & Problem Solver":
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
              model="llama-3.3-70b-versatile",
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
          )
          st.markdown("### 📘 Explanation")
          st.markdown(chat_completion.choices[0].message.content)
        except Exception as e:
          st.error(f"Error: {e}")
    else:
      st.warning("Please type a concept or problem first.")
