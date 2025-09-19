import streamlit as st
from main_functions import extraction_of_cv, helper

st.title("Upload your CV")

if "cv_text" in st.session_state and "jd_text" in st.session_state and "fixed_cv" in st.session_state:
    my_original_score = helper.ats_score_check_optimized(st.session_state["cv_text"], st.session_state["jd_text"])
    my_optimized_score = helper.ats_score_check_optimized(st.session_state["fixed_cv"], st.session_state["jd_text"])
    my_issues = helper.ats_score_check(st.session_state["cv_text"], st.session_state["jd_text"])

    if my_optimized_score != 0:
        change = round(((my_optimized_score - my_original_score)/my_optimized_score)*100, 2)
    else:
        change = 0

    a, b, c = st.columns(3)
    a.metric("Original ATS", my_original_score, "-9°F")
    b.metric("OPTIMIZED ATS", my_optimized_score, "2 mph")
    c.metric("Percent Change in ATS", change, "2 mph")

    st.write(my_issues)

else:
    st.warning("⚠️ Please upload CV and Job Description first.")
