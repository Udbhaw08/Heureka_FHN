# pyright: reportMissingImports=false
import os
from app.utils.pdf_utils import extract_text_from_pdf # type: ignore

text = extract_text_from_pdf('data/resumes/ANON-623D41B540F3_1.pdf')
with open('resume_extracted.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print("Dumped to resume_extracted.txt")
