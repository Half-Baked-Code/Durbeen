# import fitz  # PyMuPDF
# import re


# def extract_text_and_tables_markdown(pdf_path):
#     doc = fitz.open(pdf_path)
#     markdown_output = ""

#     for page_num, page in enumerate(doc):
#         blocks = page.get_text("dict")["blocks"]
#         markdown_output += f"\n\n# Page {page_num + 1}\n"

#         for block in blocks:
#             if block["type"] == 0:  # text block
#                 for line in block["lines"]:
#                     spans = line["spans"]
#                     for span in spans:
#                         text = span["text"].strip()

#                         if not text:
#                             continue

#                         # === Heuristics for headings ===
#                         size = span["size"]
#                         if size > 15:
#                             markdown_output += f"\n\n## {text}\n"
#                         elif size > 13:
#                             markdown_output += f"\n\n### {text}\n"
#                         else:
#                             markdown_output += f"{text} "

#             elif block["type"] == 1:  # image or non-text (skip or OCR)
#                 continue

#         # === Table detection heuristic ===
#         text = page.get_text("text")
#         tables = extract_table_like_blocks(text)
#         for table in tables:
#             markdown_output += f"\n\n{table}\n"

#     return markdown_output


# def extract_table_like_blocks(text):
#     lines = text.splitlines()
#     tables = []
#     current_table = []
#     in_table = False

#     for line in lines:
#         if re.match(r"^\s*TABLE\s+\d+", line, re.IGNORECASE):
#             if current_table:
#                 tables.append("\n".join(current_table))
#                 current_table = []
#             in_table = True
#             current_table.append(f"\n**{line.strip()}**\n")
#         elif in_table:
#             if line.strip() == "":
#                 if current_table:
#                     tables.append(convert_to_markdown_table(current_table))
#                     current_table = []
#                     in_table = False
#             else:
#                 current_table.append(line.strip())

#     if current_table:
#         tables.append(convert_to_markdown_table(current_table))

#     return tables


# def convert_to_markdown_table(table_lines):
#     """
#     Convert simple list of rows into Markdown table format.
#     This is heuristic-based. Expects: header, divider, and rows.
#     """
#     header = []
#     rows = []

#     # Flatten and filter lines
#     flat_lines = [line for line in table_lines if line.strip()]
#     data_rows = []

#     for line in flat_lines:
#         if re.match(r"\*\*TABLE", line):
#             continue
#         cols = re.split(r"\s{2,}|\t", line)
#         if cols:
#             data_rows.append(cols)

#     # Pad to max column length
#     max_cols = max(len(row) for row in data_rows)
#     for i in range(len(data_rows)):
#         data_rows[i] += [""] * (max_cols - len(data_rows[i]))

#     if data_rows:
#         header = data_rows[0]
#         rows = data_rows[1:]

#     # Format as Markdown
#     md_table = "| " + " | ".join(header) + " |\n"
#     md_table += "| " + " | ".join(["---"] * len(header)) + " |\n"
#     for row in rows:
#         md_table += "| " + " | ".join(row) + " |\n"

#     return md_table.strip()


# # === Run the extraction ===
# pdf_file = r"C:\Users\Maham Jafri\Documents\Office Tasks\Durbeen\ResearchArticles\research_articles\A Teacher s Guide to Alternative Assessment  Taking the First Steps.pdf"
# md_text = extract_text_and_tables_markdown(pdf_file)

# # Optional: Save to file
# with open(
#     "ATeacher'sGuidetoAlternativeAssessmentTakingtheFirstSteps.md",
#     "w",
#     encoding="utf-8",
# ) as f:
#     f.write(md_text)

# print("✅ Extraction complete. Markdown file saved as 'extracted_article.md'.")

import fitz  # PyMuPDF
import re
import os


def extract_text_and_tables_markdown(pdf_path):
    doc = fitz.open(pdf_path)
    markdown_output = ""

    # Create image output directory
    image_output_dir = "extracted_images"
    os.makedirs(image_output_dir, exist_ok=True)

    image_count = 0  # Global image counter

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

            elif block["type"] == 1:  # image block
                # Extract all images on the page
                for image_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_count += 1
                    # Sanitize the base filename (no spaces or special characters)
                    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
                    base_filename = re.sub(r"[^\w]+", "_", base_filename)

                    image_filename = f"{base_filename}_page{page_num + 1}_img{image_count}.{image_ext}"

                    image_path = os.path.join(image_output_dir, image_filename)

                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    markdown_output += f"\n\n![Image {image_count}]({image_output_dir}/{image_filename})\n"

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
    header = []
    rows = []
    flat_lines = [line for line in table_lines if line.strip()]
    data_rows = []

    for line in flat_lines:
        if re.match(r"\*\*TABLE", line):
            continue
        cols = re.split(r"\s{2,}|\t", line)
        if cols:
            data_rows.append(cols)

    max_cols = max(len(row) for row in data_rows)
    for i in range(len(data_rows)):
        data_rows[i] += [""] * (max_cols - len(data_rows[i]))

    if data_rows:
        header = data_rows[0]
        rows = data_rows[1:]

    md_table = "| " + " | ".join(header) + " |\n"
    md_table += "| " + " | ".join(["---"] * len(header)) + " |\n"
    for row in rows:
        md_table += "| " + " | ".join(row) + " |\n"

    return md_table.strip()


# === Run the extraction ===
pdf_file = r"C:\Users\Maham Jafri\Documents\Office Tasks\Durbeen\ResearchArticles\research_articles\Threats to the Valid Use of Assessments.pdf"
md_text = extract_text_and_tables_markdown(pdf_file)

# Save Markdown output
output_md_file = "Threats to the Valid Use of Assessments.md"
with open(output_md_file, "w", encoding="utf-8") as f:
    f.write(md_text)

print(f"✅ Extraction complete. Markdown file saved as '{output_md_file}'.")
print("🖼️ Images saved in the 'extracted_images/' directory.")
