import streamlit as st
from main_functions import extraction_of_cv
import base64

st.title("Upload your CV")

my_cv = st.file_uploader("Upload PDF file", type=["pdf"])

if my_cv:
    # Extract text
    txt = extraction_of_cv.my_function_for_extracting_pdf_text(my_cv)
    st.session_state["cv_text"] = txt

    # Show PDF preview using iframe
    base64_pdf = base64.b64encode(my_cv.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
