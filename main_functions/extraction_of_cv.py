import docx
from pypdf import PdfReader


def my_function_for_extracting_pdf_text(main_file):
    reader = PdfReader(main_file)
    text = "".join([page.extract_text() or "" for page in reader.pages])
    return text.strip()

    # HOW MANY TIMES LOGGES IN

    # BEFORE AND AFTER ATS

    # LESS THAN 85 THEN MAKE ADJUSTMENT
    

    # IF ABOVE 90 DON;T CHANGE
