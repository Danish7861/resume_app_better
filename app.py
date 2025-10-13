# import streamlit as st
import base64
import os
import json
import docx
import re
from pypdf import PdfReader
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# ============================================================
# Setup
# ============================================================
st.set_page_config(page_title="AI Career Assistant", page_icon="💼", layout="wide")

load_dotenv()

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ API key not found. Please add it to .env or Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# ============================================================
# Helper Functions
# ============================================================

# def show_pdf(file):
#     # Always reset the pointer before reading
#     file.seek(0)
#     base64_pdf = base64.b64encode(file.read()).decode("utf-8")
#     pdf_display = f"""
#     <iframe src="data:application/pdf;base64,{base64_pdf}" 
#             width="100%" height="500" 
#             type="application/pdf"></iframe>
#     """
#     st.markdown(pdf_display, unsafe_allow_html=True)

# def show_pdf(file):
#     file.seek(0)
#     pdf_bytes = file.read()
#     st.download_button(
#         label="📥 Download or Open PDF",
#         data=pdf_bytes,
#         file_name=file.name,
#         mime="application/pdf"
#     )
#     st.success("✅ PDF uploaded successfully. Click above to open in a new tab.")

def show_pdf(file):
    import tempfile, os, base64

    file.seek(0)
    pdf_bytes = file.read()

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_path = tmp_file.name

    # Encode local path to Base64 for Streamlit serving
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")

    # Use pdf.js-style embedding (safe and Chrome-compatible)
    pdf_display = f"""
    <iframe
        src="https://mozilla.github.io/pdf.js/web/viewer.html?file=data:application/pdf;base64,{encoded}"
        width="100%"
        height="600"
        style="border:none;"
    ></iframe>
    """

    st.markdown(pdf_display, unsafe_allow_html=True)




def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception:
        return ""

def extract_docx_text(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception:
        return ""

import re

def ats_score(cv_text, jd_text):
    prompt = f"""
    You are an ATS system. Compare the CV with the Job Description.

    --- Candidate CV ---
    {cv_text}

    --- Job Description ---
    {jd_text}

    Respond ONLY in raw JSON. No explanations, no extra text.
    Example:
    {{
        "ats_score": 85
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    # Try parsing JSON directly
    try:
        return float(json.loads(result)["ats_score"])
    except:
        # Fallback: extract number using regex
        match = re.search(r"(\d+)", result)
        if match:
            return float(match.group(1))
        return 0.0


def fix_cv(cv_text, jd_text):
    prompt = f"""
    You are a CV optimization expert.
    Rewrite the CV to best match the job description (without lying).
    Keep professional formatting.

    CV:
    {cv_text}

    JD:
    {jd_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def generate_cover_letter(cv_text, jd_text):
    prompt = f"""
    Write a tailored professional cover letter based on the CV and job description.

    CV:
    {cv_text}

    JD:
    {jd_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def cv_suggestions(cv_text, jd_text):
    prompt = f"""
    Provide actionable suggestions to improve this CV for the job description.
    Focus on missing keywords, skills, structure, and formatting.

    CV:
    {cv_text}

    JD:
    {jd_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def interview_questions(cv_text, jd_text):
    prompt = f"""
    You are an expert interviewer and career coach. 

    Task:
    - Create 5 interview questions based on the CV and Job Description provided.  
    - Focus on the most relevant skills, experiences, and responsibilities.  
    - For each question, also provide a detailed step-by-step sample answer that a strong candidate would give.

    Format your response as:
    1. Question
    - Why this question is important (tie it to CV or JD).
    - Step-by-step sample answer (numbered list).
    - Key points to highlight.

    CV:
    {cv_text}

    JD:
    {jd_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )
    return response.choices[0].message.content.strip()

# ============================================================
# UI
# ============================================================
st.title("💼 AI Career Assistant")
st.markdown("### Upload your CV & Job Description and get AI-powered insights 🚀")

col1, col2 = st.columns(2)

with col1:
    cv_file = st.file_uploader("📄 Upload CV (PDF)", type=["pdf"])
    if cv_file:
        cv_text = extract_pdf_text(cv_file)
        st.session_state["cv_text"] = cv_text
        # cv_file.seek(0)
        # base64_pdf = base64.b64encode(cv_file.read()).decode("utf-8")
        # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400"></iframe>'
        # st.markdown(pdf_display, unsafe_allow_html=True)
        show_pdf(cv_file)



with col2:
    jd_file = st.file_uploader("📋 Upload Job Description (TXT/DOCX)", type=["txt", "docx"])
    jd_text_input = st.text_area("Or paste Job Description here:")
    if jd_file:
        jd_text = jd_file.read().decode("utf-8") if jd_file.name.endswith(".txt") else extract_docx_text(jd_file)
        st.session_state["jd_text"] = jd_text
    elif jd_text_input.strip():
        st.session_state["jd_text"] = jd_text_input

# ============================================================
# Action Button
# ============================================================
if "cv_text" in st.session_state and "jd_text" in st.session_state:
    st.markdown("---")
    if st.button("🚀 Analyze & Optimize", type="primary", use_container_width=True):
        with st.spinner("🔍 Analyzing your CV..."):
            cv_text = st.session_state["cv_text"]
            jd_text = st.session_state["jd_text"]

            original_score = ats_score(cv_text, jd_text)

            if original_score < 85:
                fixed_cv = fix_cv(cv_text, jd_text)
                optimized_score = ats_score(fixed_cv, jd_text)
            elif original_score >= 90:
                fixed_cv = "✅ Your CV already scores high (90+). No major changes needed."
                optimized_score = original_score
            else:
                fixed_cv = fix_cv(cv_text, jd_text)
                optimized_score = ats_score(fixed_cv, jd_text)

            suggestions = cv_suggestions(cv_text, jd_text)
            cover_letter = generate_cover_letter(cv_text, jd_text)
            questions = interview_questions(cv_text, jd_text)

        # Dashboard Styling
        st.markdown("""
            <style>
            .card {
                background: linear-gradient(135deg, #0f172a, #1e293b);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }
            .metric-label {
                font-size: 18px;
                font-weight: bold;
                color: #06b6d4;
            }
            .metric-value {
                font-size: 28px;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="card"><div class="metric-label">📊 Original ATS</div><div class="metric-value">{original_score:.1f}%</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="card"><div class="metric-label">🚀 Optimized ATS</div><div class="metric-value">{optimized_score:.1f}%</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="card"><div class="metric-label">📈 Change</div><div class="metric-value">{(optimized_score-original_score):.1f}%</div></div>', unsafe_allow_html=True)

        st.subheader("📌 Progress Overview")
        st.progress(original_score/100)
        st.progress(optimized_score/100)

        st.subheader("🛠 Optimized CV")
        st.text_area("Optimized CV", fixed_cv, height=400)

        st.subheader("📌 Suggestions for Improvement")
        st.markdown(suggestions)

        st.subheader("✉️ Tailored Cover Letter")
        st.text_area("Cover Letter", cover_letter, height=300)

        st.subheader("🎤 Interview Questions")
        st.markdown(questions)

else:
    st.info("⬆️ Upload your CV and Job Description to get started.")
