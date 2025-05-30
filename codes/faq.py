from docx import Document as DocxDocument
from PyPDF2 import PdfReader
import openai


def extract_text_from_doc(doc_path):
    if doc_path.endswith(".pdf"):
        reader = PdfReader(doc_path)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif doc_path.endswith(".docx"):
        doc = DocxDocument(doc_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif doc_path.endswith(".txt"):
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type")


def generate_faq(doc_path):
    content = extract_text_from_doc(doc_path)
    prompt = f"""
You are an expert assistant. Based on the following document, generate a helpful FAQ section. Each FAQ should include a common question a student might ask and a clear, concise answer.

Content:
\"\"\"{content[:6000]}\"\"\"

Return only the list of FAQs in this format:
Q: ...
A: ...
"""
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0.6
    )
    return response["choices"][0]["message"]["content"]
