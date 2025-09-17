import streamlit as st
from main_functions import extraction_of_cv


st.title("Upload JOB DESCRIPTION")

import streamlit as st

uploaded_jd = st.file_uploader("Upload Job Description (TXT/DOCX)", type=["txt", "docx"])

jd_text_input = st.text_area("Or paste job description here:")

if uploaded_jd:
    jd_text = extraction_of_cv.my_function_for_extracting_pdf_text(uploaded_jd)
    st.session_state["jd_text"] = jd_text
    st.success("✅ Job description uploaded!")
elif jd_text_input.strip():
    st.session_state["jd_text"] = jd_text_input
    st.success("✅ Job description saved!")