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

# Custom Page Style
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
    }
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #06b6d4, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #94a3b8;
        margin-bottom: 40px;
    }
    .upload-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 30px;
        color: #38bdf8;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# Load API Key
# ============================================================
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


def show_pdf(file):
    """
    Display an uploaded PDF inline using Mozilla's secure PDF.js viewer.
    Works perfectly on Streamlit Cloud and all major browsers (Chrome, Edge, Safari).
    """
    import base64
    import streamlit as st
    file.seek(0)
    pdf_bytes = file.read()
    st.download_button(
        label="📥 Download or Open PDF",
        data=pdf_bytes,
        file_name=file.name,
        mime="application/pdf"
    )
    st.success("✅ PDF uploaded successfully. Click above to open in a new tab.")

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

def ats_score(cv_text, jd_text):
    prompt = f"""
    You are an ATS system. Compare the CV with the Job Description.

    --- Candidate CV ---
    {cv_text}

    --- Job Description ---
    {jd_text}

    Respond ONLY in raw JSON like:
    {{ "ats_score": 85 }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    result = response.choices[0].message.content.strip()
    try:
        return float(json.loads(result)["ats_score"])
    except:
        match = re.search(r"(\d+)", result)
        return float(match.group(1)) if match else 0.0

def fix_cv(cv_text, jd_text):
    prompt = f"""
    You are a CV optimization expert.
    Rewrite the CV to best match the job description (without lying).
    Keep formatting and professionalism.
    CV:
    {cv_text}
    JD:
    {jd_text}
    """
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return res.choices[0].message.content.strip()

def generate_cover_letter(cv_text, jd_text):
    prompt = f"""
    Write a professional cover letter based on this CV and job description.
    CV:
    {cv_text}
    JD:
    {jd_text}
    """
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return res.choices[0].message.content.strip()

def cv_suggestions(cv_text, jd_text):
    prompt = f"""
    Provide clear, actionable suggestions to improve this CV for the job description.
    Focus on keywords, skills, structure, and formatting.
    CV:
    {cv_text}
    JD:
    {jd_text}
    """
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return res.choices[0].message.content.strip()

def interview_questions(cv_text, jd_text):
    prompt = f"""
    Create 5 interview questions based on the CV and job description.
    Provide:
    - Why each question matters
    - A detailed step-by-step sample answer
    - Key points to highlight
    CV:
    {cv_text}
    JD:
    {jd_text}
    """
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )
    return res.choices[0].message.content.strip()

# ============================================================
# UI
# ============================================================
st.markdown('<div class="main-title">💼 AI Career Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload your CV & Job Description to get professional AI-powered insights 🚀</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        cv_file = st.file_uploader("📄 Upload CV (PDF)", type=["pdf"])
        if cv_file:
            cv_text = extract_pdf_text(cv_file)
            st.session_state["cv_text"] = cv_text
            show_pdf(cv_file)
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        jd_file = st.file_uploader("📋 Upload Job Description (TXT/DOCX)", type=["txt", "docx"])
        jd_text_input = st.text_area("Or paste Job Description here:")
        if jd_file:
            jd_text = jd_file.read().decode("utf-8") if jd_file.name.endswith(".txt") else extract_docx_text(jd_file)
            st.session_state["jd_text"] = jd_text
        elif jd_text_input.strip():
            st.session_state["jd_text"] = jd_text_input
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# Action Section
# ============================================================
if "cv_text" in st.session_state and "jd_text" in st.session_state:
    st.markdown("---")
    st.markdown('<div class="section-title">🚀 AI Optimization Dashboard</div>', unsafe_allow_html=True)
    if st.button("✨ Analyze & Optimize", type="primary", use_container_width=True):
        with st.spinner("Analyzing your CV..."):
            cv_text = st.session_state["cv_text"]
            jd_text = st.session_state["jd_text"]

            original_score = ats_score(cv_text, jd_text)
            fixed_cv = fix_cv(cv_text, jd_text) if original_score < 90 else cv_text
            optimized_score = ats_score(fixed_cv, jd_text)
            suggestions = cv_suggestions(cv_text, jd_text)
            cover_letter = generate_cover_letter(cv_text, jd_text)
            questions = interview_questions(cv_text, jd_text)

        st.markdown("""
            <style>
            .metric-card {
                background: linear-gradient(135deg, #2563eb, #38bdf8);
                border-radius: 15px;
                color: white;
                text-align: center;
                padding: 25px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                margin: 10px;
            }
            .metric-card h3 {
                margin: 0;
                font-size: 22px;
                color: #e0f2fe;
            }
            .metric-card p {
                font-size: 32px;
                font-weight: bold;
                margin: 5px 0;
            }
            </style>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><h3>Original ATS</h3><p>{original_score:.1f}%</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><h3>Optimized ATS</h3><p>{optimized_score:.1f}%</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><h3>Change</h3><p>{optimized_score-original_score:.1f}%</p></div>', unsafe_allow_html=True)

        st.progress(min(optimized_score / 100, 1.0))

        st.subheader("🧾 Optimized CV")
        st.text_area("Optimized CV Text", fixed_cv, height=400)

        st.subheader("💡 Suggestions for Improvement")
        st.markdown(suggestions)

        st.subheader("✉️ Tailored Cover Letter")
        st.text_area("Cover Letter", cover_letter, height=300)

        st.subheader("🎯 Interview Questions & Answers")
        st.markdown(questions)
else:
    st.info("⬆️ Upload your CV and Job Description to begin your AI-powered career analysis.")
