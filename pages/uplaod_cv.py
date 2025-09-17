import streamlit as st
from main_functions import extraction_of_cv

st.title("Upload your cv")

my_cv = st.file_uploader(
    "Upload pdf files",
    type=["pdf"],
)

if my_cv:
    txt = extraction_of_cv.my_function_for_extracting_pdf_text(my_cv)
    st.session_state["cv_text"] = txt
    st.pdf(my_cv, height=600)