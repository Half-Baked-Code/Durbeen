import os
import json
from docx import Document as DocxDocument
from PyPDF2 import PdfReader
import openai
from dotenv import load_dotenv


class StudyGuide:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)

    def extract_text(self, doc_path):
        if doc_path.endswith(".pdf"):
            reader = PdfReader(doc_path)
            return "\n".join(
                [page.extract_text() for page in reader.pages if page.extract_text()]
            )
        elif doc_path.endswith(".docx"):
            doc = DocxDocument(doc_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif doc_path.endswith(".txt"):
            with open(doc_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError("Unsupported file type")

    def generate_briefing_document(self, doc_path):
        content = self.extract_text(doc_path)
        prompt = f"""
You are a study assistant. Read the following academic article and generate a detailed **Briefing Document** reviewing the main themes and most important ideas. Structure your output exactly as follows:

---

**Briefing Document: [Insert Title of Article]**

**Source:** [Insert Citation of Article]

**Main Themes:**
[List the 3–6 key themes of the article as bullet points. These are broad, conceptual takeaways.]

**Most Important Ideas and Facts:**
[List specific claims, arguments, terminologies, distinctions, and insights. Use bullet points or numbered points, quoting important lines from the text where necessary.]

**Conclusion:**
[Summarize the article's overall contribution and why these distinctions matter in education or policy.]

The document to summarize is below:
\"\"\"{content[:6000]}\"\"\"

Return only the briefing document in markdown format.
"""
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
        )
        output = response.choices[0].message.content
        print(output)
        return output

    def generate_faq(self, doc_path):
        content = self.extract_text(doc_path)
        prompt = f"""
You are an expert assistant. Based on the following document, generate a helpful FAQ section. Each FAQ should include a common question a student might ask and a clear, concise answer.

Content:
\"\"\"{content[:6000]}\"\"\"

Return only the list of FAQs in this format:
Q: ...
\n
A: ...
"""
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
        )
        output = response.choices[0].message.content
        print(output)
        return output

    def generate_studyguide(self, doc_path):
        content = self.extract_text(doc_path)
        prompt = f"""
You are a study assistant. Read the following content and create a comprehensive study guide that includes:

1. Key Concepts  
2. Important Terms and Definitions  
3. Summary Points by Sections  
4. Relevant Examples  
5. Quick Recap at the end

Content:
\"\"\"{content[:6000]}\"\"\"

Return only the study guide.
"""
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
        )
        output = response.choices[0].message.content
        print(output)
        return output

    def generate_mind_map(self, doc_path):
        content = self.extract_text(doc_path)
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
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
        )
        result = response.choices[0].message.content
        try:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=2))
            return parsed
        except json.JSONDecodeError:
            print("Invalid JSON returned.")
            print(result)
            return result
