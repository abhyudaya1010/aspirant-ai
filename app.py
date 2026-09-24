import sys
import asyncio
import platform
if sys.platform.startswith("win"):
    try:
        asyncio.get_event_loop_policy()
    except Exception:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
import io
import time
import random
from PIL import Image
import streamlit as st
import pytesseract
from google import genai
from google.genai import types

# Auto-configure local Windows path for Tesseract (safe for Streamlit Cloud Linux too)
if platform.system() == "Windows":
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    except Exception:
        pass

st.set_page_config(page_title="Aspirant AI", layout="wide")

# Safe client initialization
try:
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=api_key) if api_key else None

st.title("🎯 Aspirant AI")
st.caption("Personalized engineering & academic command center.")

with st.sidebar:
    st.header("🛠️ Workspace Modules")
    active_feature = st.radio(
        "Select Active Feature",
        [
            "📚 NCERT Textbook Reader (Class 9–12)",
            "📸 Multi-Question Socratic Hint Inspector"
        ]
    )
    st.markdown("---")
    if not client:
        st.warning("⚠️ GEMINI_API_KEY not found in secrets/env. AI features require it.")

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
        ]
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
        ]
    }
}

HINT_SYSTEM_PROMPT = """
You are an expert JEE Main/Advanced & Board STEM tutor. Analyze the provided problems.
Instructions:
1. Detect **every single question, sub-question, or problem**.
2. For *every single question*, output:
   - **Q[No.]: [Short summary/transcription]**
   - **Key Concept / Formula**: [Formula name or expression needed]
   - **Socratic Hint**: [Guiding question to trigger insight]
   - **First Kickstart Step**: [Exact first line/setup to begin solving]
"""

if active_feature == "📚 NCERT Textbook Reader (Class 9–12)":
    st.subheader("📖 Official NCERT Textbook Portal")
    col_c, col_s = st.columns([1, 1], gap="medium")
    with col_c:
        selected_class = st.selectbox("Select Class", list(NCERT_FULL_DATABASE.keys()))
    with col_s:
        selected_subject = st.selectbox("Select Subject", list(NCERT_FULL_DATABASE[selected_class].keys()))

    st.markdown("---")
    chapters = NCERT_FULL_DATABASE[selected_class][selected_subject]
    st.markdown(f"**Showing {len(chapters)} official chapters for {selected_class} — {selected_subject}**")

    for ch in chapters:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{ch['name']}**")
            with col2:
                st.markdown(
                    f'<a href="{ch["url"]}" target="_blank">'
                    f'<button style="width:100%; background-color:#2563EB; color:white; border:none; padding:8px 12px; border-radius:4px; font-weight:bold; cursor:pointer;">Open PDF ↗</button>'
                    f'</a>',
                    unsafe_allow_html=True
                )

elif active_feature == "📸 Multi-Question Socratic Hint Inspector":
    st.subheader("📸 Local OCR & Socratic Hint Engine")
    st.caption("Upload an image (processed locally via Tesseract) or use Direct Text mode.")

    user_context = st.text_input("Optional context (e.g., 'Class 11 rotational dynamics sheet')", "")
    input_mode = st.radio("Choose Input Mode", ["🖼️ Image Upload (Local OCR)", "✍️ Direct Text / Paste"], horizontal=True)

    if not client:
        st.error("Gemini client not initialized. Check your GEMINI_API_KEY secret.")
    else:
        if input_mode == "🖼️ Image Upload (Local OCR)":
            uploaded_img = st.file_uploader("Upload notebook/worksheet snapshot", type=["png", "jpg", "jpeg"])
            if uploaded_img:
                col_img, col_diag = st.columns([1, 1], gap="large")
                with col_img:
                    image = Image.open(uploaded_img)
                    st.image(image, caption="Your Snapshot", use_container_width=True)

                with col_diag:
                    if st.button("🔍 Extract Text & Generate Hints", type="primary"):
                        with st.spinner("Extracting text locally..."):
                            try:
                                extracted_text = pytesseract.image_to_string(image)
                            except Exception as ocr_err:
                                extracted_text = ""
                                st.error(f"Tesseract error: {ocr_err}")

                        if not extracted_text.strip():
                            st.warning("⚠️ No text detected cleanly. Switch to **Direct Text / Paste** mode below.")
                        else:
                            st.text_area("Detected Text (Editable):", value=extracted_text, height=120, key="ocr_edit")
                            
                            with st.spinner("Generating Socratic breakdown..."):
                                try:
                                    res = client.models.generate_content(
                                        model="gemini-3.6-flash",
                                        contents=f"Context: {user_context}\n\n{HINT_SYSTEM_PROMPT}\n\nExtracted Problems:\n{extracted_text}"
                                    )
                                    st.markdown("### 💡 Socratic Hint Guide")
                                    st.markdown(res.text)
                                except Exception as e:
                                    st.error(f"Error communicating with AI: {e}")

        else:
            pasted_text = st.text_area(
                "Paste question text / statement / formula list:",
                height=180,
                placeholder="1. A 2kg block slides down a 30° rough incline with mu=0.2...\n2. Integrate from 0 to pi/2..."
            )
            if st.button("🚀 Generate Socratic Guide", type="primary"):
                if not pasted_text.strip():
                    st.warning("Please paste or type a question first.")
                else:
                    with st.spinner("Generating breakdown..."):
                        try:
                            res = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=f"Context: {user_context}\n\n{HINT_SYSTEM_PROMPT}\n\nProblems:\n{pasted_text}"
                            )
                            st.markdown("### 💡 Socratic Hint Guide")
                            st.markdown(res.text)
                        except Exception as e:
                            st.error(f"Error: {e}")
