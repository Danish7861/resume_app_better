import streamlit as st
from main_functions import extraction_of_cv

st.title("Upload JOB DESCRIPTION")

uploaded_jd = st.file_uploader("Upload Job Description (TXT/DOCX)", type=["txt", "docx"])
jd_text_input = st.text_area("Or paste job description here:")

if uploaded_jd:
    if uploaded_jd.name.endswith(".txt"):
        jd_text = uploaded_jd.read().decode("utf-8")
    else:  # .docx
        jd_text = extraction_of_cv.extract_docx_text(uploaded_jd)  # <- Make sure this exists
    st.session_state["jd_text"] = jd_text
    st.success("✅ Job description uploaded!")

elif jd_text_input.strip():
    st.session_state["jd_text"] = jd_text_input
    st.success("✅ Job description saved!")
