import fitz
import docx

def extract_text_from_pdf(pdf_path) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page in doc:
        text = page.get_text()
        full_text += text

    doc.close()
    return full_text

def extract_text_from_docx(docx_path) -> str:
    doc = docx.Document(docx_path)
    full_text = []
    
    for para in doc.paragraphs:
        full_text.append(para.text)
        
    return "\n".join(full_text)

def extract_resume_text(file_path) -> str:
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    
    else:
        raise ValueError("Unsupported file format! Please upload a PDF or DOCX.")