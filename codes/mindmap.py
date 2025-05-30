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


def generate_mind_map(doc_path):
    content = extract_text_from_doc(doc_path)
    prompt = f"""
You are an AI skilled in organizing knowledge into a hierarchical structure. Convert the document below into a JSON-formatted mind map.
Structure it with a main topic and subtopics, breaking down ideas logically.

Content:
\"\"\"{content[:6000]}\"\"\"

Return only valid JSON like:
{{
  "main_topic": "Subject Name",
  "subtopics": [
    {{
      "title": "Main Idea 1",
      "children": [
        {{ "title": "Detail A" }},
        {{ "title": "Detail B" }}
      ]
    }},
    ...
  ]
}}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0.3
    )
    import json

    return json.loads(response["choices"][0]["message"]["content"])
