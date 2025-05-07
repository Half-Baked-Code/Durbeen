# import fitz  # pip install PyMuPDF
# import re
# import os
# import camelot  # pip install "camelot-py[cv]"
# from collections import OrderedDict


# def infer_structure(page):
#     """Return list of (text, fontsize) tuples from the page in reading order."""
#     blocks = page.get_text("dict")["blocks"]
#     elems = []
#     for b in blocks:
#         if b["type"] == 0:  # text
#             for line in b["lines"]:
#                 for span in line["spans"]:
#                     txt = span["text"].strip()
#                     if txt:
#                         elems.append((span["size"], txt))
#     # Normalize: round font sizes to nearest integer
#     return [(round(sz), txt) for sz, txt in elems]


# def extract_references_block(pages):
#     """Find “References” heading, then collect all text after it."""
#     ref_text = []
#     in_refs = False
#     for page in pages:
#         for size, txt in infer_structure(page):
#             if not in_refs and re.match(r"(?i)^references\b", txt):
#                 in_refs = True
#                 continue
#             if in_refs:
#                 ref_text.append(txt)
#     return "\n".join(ref_text)


# def parse_reference_list(ref_block):
#     """
#     Split the References block into numbered or author–year entries.
#     Return OrderedDict mapping citation keys ("1" or "El Masri et al., 2016") to full entry.
#     """
#     refs = OrderedDict()
#     # First try numeric [1] style:
#     parts = re.split(r"\n\[(\d+)\]\s*", ref_block)
#     if len(parts) > 2:
#         # parts[1] is first ref number, parts[2] its text, etc.
#         for i in range(1, len(parts), 2):
#             key = parts[i]
#             entry = parts[i + 1].strip().replace("\n", " ")
#             refs[key] = entry
#         return refs

#     # Otherwise fallback to author–year detection:
#     # e.g. "Ercikan, S., & Koh, K. (2005). Title…"
#     lines = [ln.strip() for ln in ref_block.split("\n") if ln.strip()]
#     buffer = []
#     for ln in lines:
#         if re.match(r"^[A-Z][A-Za-z]+,.*\(\d{4}\)", ln):
#             # start of new ref
#             if buffer:
#                 full = " ".join(buffer)
#                 cit = re.match(r"^([A-Z][^,]+ et al\., \d{4})", buffer[0])
#                 key = cit.group(1) if cit else buffer[0]
#                 refs[key] = full
#                 buffer = []
#             buffer.append(ln)
#         else:
#             buffer.append(ln)
#     if buffer:
#         full = " ".join(buffer)
#         cit = re.match(r"^([A-Z][^,]+ et al\., \d{4})", buffer[0])
#         key = cit.group(1) if cit else buffer[0]
#         refs[key] = full
#     return refs


# def insert_citations(md, refs):
#     """
#     For each citation key in refs, find its first occurrence in md
#     and append ": full reference" inline.
#     """
#     used = set()

#     def repl(match):
#         key = match.group(1)
#         if key in refs and key not in used:
#             used.add(key)
#             return f"[{key}: {refs[key]}]"
#         else:
#             return match.group(0)

#     # numeric [1]
#     md = re.sub(r"\[(\d+)\]", repl, md)
#     # author–year (Smith et al., 2020)
#     md = re.sub(r"\(([^)]+et al\.,\s*\d{4})\)", repl, md)
#     return md


# def extract_tables(pdf_path, pages="all", output_dir="tables_md"):
#     os.makedirs(output_dir, exist_ok=True)
#     tables_md = ""
#     tables = camelot.read_pdf(pdf_path, pages=pages)
#     for i, tbl in enumerate(tables, 1):
#         csv = f"{output_dir}/table_{i}.csv"
#         tbl.to_csv(csv)
#         # convert CSV to markdown
#         df = tbl.df
#         hdr = df.iloc[0]
#         body = df.iloc[1:]
#         md = "| " + " | ".join(hdr) + " |\n"
#         md += "| " + " | ".join(["---"] * len(hdr)) + " |\n"
#         for _, row in body.iterrows():
#             md += "| " + " | ".join(row) + " |\n"
#         tables_md += f"\n\n**Table {i}.**\n\n" + md
#     return tables_md


# def extract_images(pdf_path, output_dir="images"):
#     os.makedirs(output_dir, exist_ok=True)
#     imgs_md = ""
#     doc = fitz.open(pdf_path)
#     for p in range(len(doc)):
#         for img in doc.get_page_images(p):
#             xref = img[0]
#             pix = fitz.Pixmap(doc, xref)
#             out = f"{output_dir}/img_{p+1}_{xref}.png"
#             if pix.n < 5:
#                 pix.save(out)
#             else:
#                 fitz.Pixmap(fitz.csRGB, pix).save(out)
#             imgs_md += f"\n\n![Figure {p+1}-{xref}]({out})\n\n"
#     return imgs_md


# def pdf_to_markdown(pdf_path, out_md="paper.md"):
#     doc = fitz.open(pdf_path)
#     # 1) Extract references
#     ref_block = extract_references_block(doc)
#     refs = parse_reference_list(ref_block)

#     # 2) Build main body
#     md = ""
#     for page in doc:
#         elems = infer_structure(page)
#         for size, txt in elems:
#             # headings by font size thresholds (you may need to tune these)
#             if size >= 16:
#                 md += f"\n\n# {txt}\n\n"
#             elif size >= 13:
#                 md += f"\n\n## {txt}\n\n"
#             else:
#                 # bullets?
#                 if re.match(r"^[-*•]\s+", txt):
#                     md += f"- {txt[2:]}\n"
#                 else:
#                     md += txt + " "
#         md += "\n\n"

#     # 3) Strip out the original References section
#     md = re.split(r"(?i)^#*\s*References\b", md, flags=re.MULTILINE)[0]

#     # 4) Insert citations inline
#     md = insert_citations(md, refs)

#     # 5) Append tables & images
#     md += "\n\n" + extract_tables(pdf_path) + "\n\n"
#     md += extract_images(pdf_path)

#     with open(out_md, "w", encoding="utf-8") as f:
#         f.write(md)
#     return out_md


# if __name__ == "__main__":
#     pdf = r"C:\Users\Maham Jafri\Documents\Office Tasks\Durbeen\ResearchArticles\research_articles\Language effects in international testing  the case of PISA 2006 science items.pdf"
#     md = pdf_to_markdown(pdf, out_md="Language_Effects_PISA2006.md")
#     print(f"-> Markdown written to {md}")

import pdfplumber
import re


def extract_references(text):
    # Find the start of the reference section
    ref_start = re.search(r"\bREFERENCES\b", text, re.IGNORECASE)
    if not ref_start:
        print("Reference section not found.")
        return [], text

    # Assume the rest of the document is references
    references_text = text[ref_start.end() :].strip()
    main_text = text[: ref_start.start()]

    # Split references by newline assuming each one is on its own line
    references = [ref.strip() for ref in references_text.split("\n") if ref.strip()]
    return references, main_text


def extract_author_year(reference):
    # Capture first author last name and year from reference
    match = re.match(r"([A-Za-z\-]+),\s([A-Za-z\.]+)\s\((\d{4})\)", reference)
    return (match.group(1), match.group(3), reference) if match else (None, None, None)


def insert_references(text, references):
    # Build citation map
    citation_map = {}
    for ref in references:
        author, year, full_reference = extract_author_year(ref)
        if author and year:
            citation_key = f"{author}, {year}"
            citation_map[citation_key] = full_reference

    # Replace in-text citations with full references
    def replace_citation(match):
        citation = match.group(0)
        citation_key = match.group(1)
        full_ref = citation_map.get(citation_key)
        if full_ref:
            return f"({full_ref})"
        else:
            return citation

    # This regex matches in-text citations like (Author, 1999; Author, 1999)
    pattern = r"\(([^)]+?, \d{4}(?:\s*;\s*[^)]+?, \d{4})*)\)"  # Match citations like (Haladyna, 1999; Martinez, 1999)

    # Replace all in-text citations
    return re.sub(pattern, replace_citation, text)


# Extract text from PDF file
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


# Example usage
pdf_path = r"C:\Users\Maham Jafri\Documents\Office Tasks\Durbeen\ResearchArticles\research_articles\A Review of Multiple-Choice Item-Writing Guidelines for Classroom Assessment.pdf"  # Replace with the path to your PDF file

# Step 1: Extract text from the PDF
full_text = extract_text_from_pdf(pdf_path)

# Step 2: Extract references and main body text
references, body_text = extract_references(full_text)

# Debugging: print first few references and body text
print("First 5 references:")
print(references[:5])
print("\nFirst 500 characters of body text:")
print(body_text[:500])

# Step 3: Insert references into the body text
modified_text = insert_references(body_text, references)

# Step 4: Save the modified text with references
with open("modified_text_with_references.txt", "w", encoding="utf-8") as f:
    f.write(modified_text)

print("Done inserting references.")
