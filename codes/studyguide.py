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

    def read_markdown_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_title(self, note_type: str, doc_names: list[str]) -> str:
        joined_names = ", ".join(doc_names)

        prompt = f"""
            You are a helpful assistant for generating appropriate and informative titles for notes.
            The user is generating a **{note_type}** type of note.
            The document name(s) being summarized are: **{joined_names}**
            Your task is to:
                - Return a clear, descriptive, and concise title based on the type and document name(s).
                - If only one document is listed, base the title on that.
                - If **multiple documents are listed**, generate a general combined title that reflects their collective content or theme. Do **not** make the title specific to just one document in that case.
                - Return only the title, with no bullet points, explanations, or markdown.
            ### Examples:
            For `note_type = "Study Guide"`:
                - Docs: ["Income Tax Basics"] → Title: Study Guide: Income Tax Basics
                - Docs: ["Taxation Policy", "Corporate Filing Rules"] → Title: Comprehensive Study Guide on Taxation and Corporate Filing
            For `note_type = "Briefing Doc"`:
                - Docs: ["Section 114", "Withholding Tax Rules"] → Title: Briefing Document on Key Tax Regulations
            For `note_type = "FAQ"`:
                - Docs: ["Property Tax FAQs"] → Title: Frequently Asked Questions on Property Tax
                - Docs: ["Filing Rules", "Digital Receipts", "Taxpayer Rights"] → Title: Top Taxpayer Questions: Filing, Digital Receipts & Rights
                - Donot give like this:  FAQs from Documents F, A, and Q
            Now generate the title accordingly.
"""

        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.4,
        )

        title = response.choices[0].message.content.strip('"').strip("'")
        return title

    def generate_studyguide(self, doc_paths):
        final_output = ""

        for idx, path in enumerate(doc_paths, start=1):
            filename = os.path.basename(path)
            title = os.path.splitext(filename)[0]
            content = self.read_markdown_file(path)

            prompt = f"""
        You are a highly skilled academic assistant. Read the following scholarly document and create a comprehensive and structured study guide in **markdown format**. The output should follow **this exact format**:
        **Study Guide: {title}**
        This study guide is designed to help you review and understand the key concepts presented in the article **"{title}"** by [Insert Author].
        **Core Concepts**
        Break down the main ideas thematically. For each theme:
        - Use a **bolded heading** for the concept or section (e.g., *Core Concepts of Assessment Purpose*, *Challenging the Formative vs. Summative Distinction*, etc.)
        - Use bullet points or short paragraphs with **precise definitions, arguments, and distinctions** drawn directly from the text.
        - Do **not copy entire paragraphs** verbatim. Summarize content clearly and technically.
        **Discussion Points**
        Highlight the points that need to be discussed inorder to obtain a proper understanding of the idea being discussed in the document
        **Quiz (Short Answer)**  
        Provide 10 thought-provoking short answer questions that test comprehension of the article's key concepts, arguments, and terminology. Do **not** include answers here.
        **Answer Key (Quiz)**
        Now, provide detailed answers to each of the 10 quiz questions from earlier. Answer in full sentences, referencing the article's logic, definitions, or evidence where appropriate.
        **Essay Questions**  
        Provide 5 higher-order essay prompts requiring critical engagement with the article's themes, theory, or implications. Label this section clearly and do **not** include any answers.
        **Glossary of Key Terms**  
        List and define at least 10 of the most important terms or phrases used in the article. Definitions should be concise, technical, and directly grounded in the article's content.
        Here is the content:
        \"\"\"
        {content}
        \"\"\"
        Return only the study guide, in clean and structured markdown. Replace placeholder tags like [Insert Author] with actual values from the document if available, or leave them as-is if not found.
        """

            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
            )
            guide = response.choices[0].message.content
            final_output += guide + "\n\n---\n\n"  # separator between guides

        return final_output

    def generate_briefing_document(self, doc_paths):
        final_output = ""

        for idx, path in enumerate(doc_paths, start=1):
            filename = os.path.basename(path)
            title = os.path.splitext(filename)[0]
            content = self.read_markdown_file(path)
            prompt = f"""
             You are a study assistant. Read the following academic article and generate a detailed **Briefing Document** reviewing the main themes and most important ideas. Structure your output exactly as follows:
            ---
            **Briefing Document: [Insert Title of Article]**
            **Source:** [Insert Citation of Article]
            **Executive Summary**
            [Provide a concise, high-level summary capturing the main argument or thesis of the article, key findings, and overall contribution. Aim for clarity and precision.]

            **Core Concepts and Arguments**
            [Break down the article into its major conceptual components and arguments. Use numbered sub-sections for clarity. Quote or paraphrase key claims or passages. Where applicable, highlight definitions, distinctions, controversies, and theoretical contributions.]

            **Key Arguments and Important Facts/Ideas**
            [Summarize the most important arguments, definitions, terminologies, and insights as bullet points. Focus on facts, claims, and classifications that are central to the article's message.]

            **Implications for Practice and Policy**
            [Identify and discuss the practical or policy-related implications of the article’s findings or arguments. Consider how these insights might influence educators, system designers, or policymakers.]

            **Conclusion:**
            [Summarize the article's overall contribution and why these distinctions matter in education or policy.]
            The document to summarize is below:
            \"\"\"{content}\"\"\"
            Return only the briefing document in markdown format.
            """
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
            )
            brief = response.choices[0].message.content
            print(brief)
            print("NEXT BRIEF")
            final_output += brief + "\n\n---\n\n"

        return final_output

    def generate_faq(self, doc_paths):
        final_output = ""
        for idx, path in enumerate(doc_paths, start=1):
            filename = os.path.basename(path)
            title = os.path.splitext(filename)[0]
            content = self.read_markdown_file(path)
            prompt = f"""
            You are an expert assistant. Based on the following document, generate a helpful FAQ section. Each FAQ should include a common question a student might ask and a clear, concise answer.
            Content:
            \"\"\"{content}\"\"\"
            Return only the list of FAQs in this format:
            **FAQ for [Insert Title of Article]**
            #### Q: ...
            \n
            A: ...
            """
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
            )
            faq = response.choices[0].message.content
            print(faq)
            print("NEXT")
            final_output += faq + "\n\n---\n\n"
        return final_output

    def generate_mindmap(self, doc_paths):
        final_output = ""

        for idx, path in enumerate(doc_paths, start=1):
            filename = os.path.basename(path)
            title = os.path.splitext(filename)[0]
            content = self.read_markdown_file(path)

            prompt = f"""
        You are a highly skilled academic assistant. Your task is to carefully read and analyze the following scholarly document, and then generate a **comprehensive and hierarchical mindmap** in **Markdown format compatible with Markmap**.

        ## Instructions for Mindmap Generation:
        - The mindmap must use proper Markdown syntax:
        - `#` for the document title
        - `##`, `###`, `####` for nested levels (chapters, sections, subpoints, examples)
        - `-` for bullet points where appropriate.
        - **Include all major sections, arguments, and subthemes from the document.**
        - Represent hierarchical relationships clearly (e.g., topics → subtopics → key points → examples).
        - Use **precise, concise** language. Avoid copying full paragraphs — summarize in technical bullet points or short lines.
        - Ensure that the mindmap can be directly rendered by [Markmap](https://markmap.js.org/).
        - Replace placeholder text like [Insert Author] if the author's name is found in the content.
        - Return **only the clean Markdown-formatted mindmap**. Do not include any extra text or commentary.

        Here is the content:
        \"\"\"
        {content}
        \"\"\"
        Return only the final Markmap-compatible Markdown.
        """

            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
            )
            mindmap = response.choices[0].message.content
            final_output += mindmap + "\n\n---\n\n"  # separator between mindmaps
            print(final_output)
            return final_output


# study_tool = StudyGuide()
# study_tool.generate_mindmap(
#     [
#         "C:\\Users\\Maham Jafri\\Documents\\Office Tasks\\Durbeen\\ResearchArticles\\research_mds\\Can a picture ruin a thousand words  The effects of visual resources in exam questions.md"
#     ]
# )
