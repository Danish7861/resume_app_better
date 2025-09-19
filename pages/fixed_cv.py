import streamlit as st
from main_functions import helper

st.title("🛠 Optimized CV")

if "cv_text" in st.session_state and "jd_text" in st.session_state:
    fixed_cv = helper.fix_cv(st.session_state["cv_text"], st.session_state["jd_text"])
    st.text_area(
        "AI Optimized CV", 
        fixed_cv, 
        height=500, 
        disabled=True, 
        label_visibility="collapsed"
    )
    st.session_state["fixed_cv"] = fixed_cv
    st.success("✅ FIXED CV IS IN SESSION")
else:
    st.warning("⚠️ Please upload CV and Job Description first.")
