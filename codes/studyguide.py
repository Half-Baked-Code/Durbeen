import os
from docx import Document as DocxDocument
from PyPDF2 import PdfReader
import openai

from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


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


def generate_studyguide(doc_path):
    content = extract_text_from_doc(doc_path)
    prompt = f"""
You are a study assistant. Read the following content and create a comprehensive study guide that includes:

1. Key Concepts
2. Important Terms and Definitions
3. Summary Points by Sections
4. Relevant Examples
5. Quick Recap at the end

Content:
\"\"\"{content[:6000]}\"\"\"  # Truncate or chunk for long documents

Return only the study guide.
"""
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": prompt},
        ],
        temperature=0.3,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content
