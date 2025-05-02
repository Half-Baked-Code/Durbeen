# # import os
# # import fitz  # PyMuPDF
# # from markdownify import markdownify as md
# # from pathlib import Path


# # class PDFtoMarkdownConverter:
# #     def __init__(self, input_dir, output_dir="markdown_output"):
# #         self.input_dir = Path(input_dir)
# #         self.output_dir = Path(output_dir)
# #         self.output_dir.mkdir(exist_ok=True)

# #     def convert_all(self):
# #         pdf_files = list(self.input_dir.glob("*.pdf"))
# #         if not pdf_files:
# #             print("No PDF files found in the directory.")
# #             return

# #         for pdf_file in pdf_files:
# #             print(f"Processing {pdf_file.name}...")
# #             html_content = self._extract_text_as_html(pdf_file)
# #             markdown_content = self._convert_html_to_markdown(html_content)
# #             self._save_markdown(pdf_file.stem, markdown_content)
# #             print(
# #                 f"Saved: {self.output_dir / (self._sanitize_filename(pdf_file.stem) + '.md')}"
# #             )

# #     def _extract_text_as_html(self, pdf_path):
# #         doc = fitz.open(pdf_path)
# #         full_text = ""
# #         for page in doc:
# #             full_text += page.get_text("html")  # HTML helps preserve table structure
# #         return full_text

# #     def _convert_html_to_markdown(self, html_text):
# #         return md(html_text, heading_style="ATX")

# #     def _sanitize_filename(self, name):
# #         return "".join(
# #             c if c.isalnum() or c in (" ", "-", "_") else "_" for c in name
# #         ).strip()

# #     def _save_markdown(self, original_name, content):
# #         filename = self._sanitize_filename(original_name) + ".md"
# #         output_path = self.output_dir / filename
# #         with open(output_path, "w", encoding="utf-8") as f:
# #             f.write(content)


# # # === Usage Example ===
# # if __name__ == "__main__":
# #     input_path = r"research_articles"  # 🔁 Replace with actual path
# #     converter = PDFtoMarkdownConverter(input_path)
# #     converter.convert_all()


# import fitz  # PyMuPDF
# import camelot
# from markdownify import markdownify as md
# from pathlib import Path


# class PDFtoMarkdownConverter:
#     def __init__(self, input_dir, output_dir):
#         self.input_dir = Path(input_dir)
#         self.output_dir = Path(output_dir)
#         self.output_dir.mkdir(exist_ok=True)

#     def convert_all(self):
#         for pdf_file in self.input_dir.glob("*.pdf"):
#             print(f"\nProcessing {pdf_file.name}...")
#             html_content = self._extract_text_as_html(pdf_file)
#             tables_md = self._extract_tables_as_markdown(pdf_file)
#             full_md = self._convert_html_to_markdown(html_content) + "\n\n" + tables_md
#             self._save_markdown(pdf_file.stem, full_md)
#             print(
#                 f"Saved: {self.output_dir / (self._sanitize_filename(pdf_file.stem) + '.md')}"
#             )

#     def _extract_text_as_html(self, pdf_path):
#         doc = fitz.open(pdf_path)
#         full_text = ""
#         for page in doc:
#             full_text += page.get_text("html")
#         return full_text

#     def _extract_tables_as_markdown(self, pdf_path):
#         try:
#             tables = camelot.read_pdf(str(pdf_path), pages="all", strip_text="\n")
#             md_tables = ""
#             for i, table in enumerate(tables):
#                 md_tables += f"\n\n**Table {i+1}:**\n\n"
#                 md_tables += table.df.to_markdown(index=False)
#             return md_tables
#         except Exception as e:
#             print(f"Failed to extract tables with Camelot: {e}")
#             return ""

#     def _convert_html_to_markdown(self, html_text):
#         return md(html_text, heading_style="ATX")

#     def _sanitize_filename(self, name):
#         return "".join(
#             c if c.isalnum() or c in (" ", "-", "_") else "_" for c in name
#         ).strip()

#     def _save_markdown(self, original_name, content):
#         filename = self._sanitize_filename(original_name) + ".md"
#         output_path = self.output_dir / filename
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(content)


# def main():
#     input_path = r"research_articles"  # 🔁 Replace with actual path
#     output_path = r"markdown_output"  # Optional: customize output folder

#     converter = PDFtoMarkdownConverter(input_path, output_path)
#     converter.convert_all()


# if __name__ == "__main__":
#     main()

import fitz  # PyMuPDF
import re


def extract_text_and_tables_markdown(pdf_path):
    doc = fitz.open(pdf_path)
    markdown_output = ""

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        markdown_output += f"\n\n# Page {page_num + 1}\n"

        for block in blocks:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    spans = line["spans"]
                    for span in spans:
                        text = span["text"].strip()

                        if not text:
                            continue

                        # === Heuristics for headings ===
                        size = span["size"]
                        if size > 15:
                            markdown_output += f"\n\n## {text}\n"
                        elif size > 13:
                            markdown_output += f"\n\n### {text}\n"
                        else:
                            markdown_output += f"{text} "

            elif block["type"] == 1:  # image or non-text (skip or OCR)
                continue

        # === Table detection heuristic ===
        text = page.get_text("text")
        tables = extract_table_like_blocks(text)
        for table in tables:
            markdown_output += f"\n\n{table}\n"

    return markdown_output


def extract_table_like_blocks(text):
    lines = text.splitlines()
    tables = []
    current_table = []
    in_table = False

    for line in lines:
        if re.match(r"^\s*TABLE\s+\d+", line, re.IGNORECASE):
            if current_table:
                tables.append("\n".join(current_table))
                current_table = []
            in_table = True
            current_table.append(f"\n**{line.strip()}**\n")
        elif in_table:
            if line.strip() == "":
                if current_table:
                    tables.append(convert_to_markdown_table(current_table))
                    current_table = []
                    in_table = False
            else:
                current_table.append(line.strip())

    if current_table:
        tables.append(convert_to_markdown_table(current_table))

    return tables


def convert_to_markdown_table(table_lines):
    """
    Convert simple list of rows into Markdown table format.
    This is heuristic-based. Expects: header, divider, and rows.
    """
    header = []
    rows = []

    # Flatten and filter lines
    flat_lines = [line for line in table_lines if line.strip()]
    data_rows = []

    for line in flat_lines:
        if re.match(r"\*\*TABLE", line):
            continue
        cols = re.split(r"\s{2,}|\t", line)
        if cols:
            data_rows.append(cols)

    # Pad to max column length
    max_cols = max(len(row) for row in data_rows)
    for i in range(len(data_rows)):
        data_rows[i] += [""] * (max_cols - len(data_rows[i]))

    if data_rows:
        header = data_rows[0]
        rows = data_rows[1:]

    # Format as Markdown
    md_table = "| " + " | ".join(header) + " |\n"
    md_table += "| " + " | ".join(["---"] * len(header)) + " |\n"
    for row in rows:
        md_table += "| " + " | ".join(row) + " |\n"

    return md_table.strip()


# === Run the extraction ===
pdf_file = r"C:\Users\Maham Jafri\Documents\Office Tasks\Durbeen\ResearchArticles\research_articles\A Review of Multiple-Choice Item-Writing Guidelines for Classroom Assessment.pdf"
md_text = extract_text_and_tables_markdown(pdf_file)

# Optional: Save to file
with open("extracted_article.md", "w", encoding="utf-8") as f:
    f.write(md_text)

print("✅ Extraction complete. Markdown file saved as 'extracted_article.md'.")
