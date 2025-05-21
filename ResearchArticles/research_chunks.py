# import re
# import json
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# # Load the Markdown content
# with open(
#     r"C:\Users\user\Desktop\Tasks\Durbeen\ResearchArticles\research_mds\Threats to the Valid Use of Assessments.md",
#     "r",
#     encoding="utf-8",
# ) as f:
#     markdown_text = f.read()

# # Initialize text splitter with 10-word overlap
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=300,
#     chunk_overlap=10,
#     length_function=lambda x: len(x.split()),
#     separators=["\n\n", "\n", " ", ""],
# )

# # Regex patterns
# source_pattern = r"^# (.+)"
# page_pattern = r"\*\*Page (\d+)\*\*"
# section_pattern = r"^## (.+)"
# subsection_pattern = r"^### (.+)"
# table_pattern = r"\*\*TABLE \d+\*\*"

# # Initialize tracking variables
# chunks = []
# chunk_id_counter = 1
# current_source = None
# current_page = None
# current_section = None
# current_subsection = None
# current_text_lines = []


# def store_subsection_chunk(text, meta):
#     """Split subsection text if necessary and store with metadata and chunk_id."""
#     global chunk_id_counter
#     if not text.strip():
#         return
#     if len(text.split()) > 300:
#         sub_chunks = text_splitter.split_text(text)
#         for sub_chunk in sub_chunks:
#             chunks.append(
#                 {
#                     "content": sub_chunk.strip(),
#                     "metadata": {**meta, "chunk_id": chunk_id_counter},
#                 }
#             )
#             chunk_id_counter += 1
#     else:
#         chunks.append(
#             {
#                 "content": text.strip(),
#                 "metadata": {**meta, "chunk_id": chunk_id_counter},
#             }
#         )
#         chunk_id_counter += 1


# def flush_current_text():
#     global current_text_lines
#     if current_text_lines:
#         text_block = "\n".join(current_text_lines).strip()
#         store_subsection_chunk(
#             text_block,
#             {
#                 "source": current_source or "Unspecified",
#                 "page": current_page or "Unspecified",
#                 "section": current_section or "Null",
#                 "subsection": current_subsection or "Null",
#             },
#         )
#         current_text_lines = []


# # Split the text into lines
# lines = markdown_text.splitlines()

# i = 0
# while i < len(lines):
#     line = lines[i].strip()

#     if re.match(source_pattern, line):
#         flush_current_text()
#         current_source = re.match(source_pattern, line).group(1)

#     elif re.match(page_pattern, line):
#         flush_current_text()
#         current_page = int(re.match(page_pattern, line).group(1))

#     elif re.match(section_pattern, line):
#         flush_current_text()
#         current_section = re.match(section_pattern, line).group(1)
#         current_subsection = None  # ✅ Reset subsection when a new section is found

#     elif re.match(subsection_pattern, line):
#         flush_current_text()
#         current_subsection = re.match(subsection_pattern, line).group(1)

#     elif re.match(table_pattern, line):
#         flush_current_text()
#         # Collect the entire table block
#         table_lines = [line]
#         i += 1
#         while i < len(lines):
#             next_line = lines[i].strip()
#             if not next_line or re.match(r"^#|##|###|\*\*TABLE \d+\*\*", next_line):
#                 i -= 1  # step back to reprocess heading or new table
#                 break
#             table_lines.append(next_line)
#             i += 1

#         chunks.append(
#             {
#                 "content": "\n".join(table_lines).strip(),
#                 "metadata": {
#                     "source": current_source or "Unspecified",
#                     "page": current_page or "Unspecified",
#                     "section": current_section or "Null",
#                     "subsection": current_subsection or "Null",
#                     "type": "table",
#                     "chunk_id": chunk_id_counter,
#                 },
#             }
#         )
#         chunk_id_counter += 1

#     else:
#         current_text_lines.append(line)

#     i += 1

# # Store any remaining text block
# flush_current_text()

# # Save chunks to JSON
# with open("threats_to_valid_use_chunks.json", "w", encoding="utf-8") as f:
#     json.dump(chunks, f, indent=2, ensure_ascii=False)

# print(f"✅ {len(chunks)} chunks saved to output_chunks.json.")
import re
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load the Markdown content
with open(
    r"C:\Users\user\Desktop\Tasks\Durbeen\ResearchArticles\research_mds\A review of the literature on marking reliability.md",
    "r",
    encoding="utf-8",
) as f:
    markdown_text = f.read()

# Initialize text splitter with 10-word overlap
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=10,
    length_function=lambda x: len(x.split()),
    separators=["\n\n", "\n", " ", ""],
)

# Regex patterns
source_pattern = r"^# (.+)"
page_pattern = r"\*\*Page (\d+)\*\*"
section_pattern = r"^## (.+)"
subsection_pattern = r"^### (.+)"
sub_subsection_pattern = r"^#### (.+)"
table_pattern = r"\*\*TABLE \d+\*\*"

# Tracking variables
chunks = []
chunk_id_counter = 1
current_source = None
current_page = None
current_section = None
current_subsection = None
current_sub_subsection = None
current_text_lines = []


def store_sub_subsection_chunk(text, meta):
    """Split text based on sub-sub-section and store with metadata."""
    global chunk_id_counter
    if not text.strip():
        return
    if len(text.split()) > 300:
        sub_chunks = text_splitter.split_text(text)
        for sub_chunk in sub_chunks:
            chunks.append(
                {
                    "content": sub_chunk.strip(),
                    "metadata": {**meta, "chunk_id": chunk_id_counter},
                }
            )
            chunk_id_counter += 1
    else:
        chunks.append(
            {
                "content": text.strip(),
                "metadata": {**meta, "chunk_id": chunk_id_counter},
            }
        )
        chunk_id_counter += 1


def flush_current_text():
    global current_text_lines
    if current_text_lines:
        text_block = "\n".join(current_text_lines).strip()
        store_sub_subsection_chunk(
            text_block,
            {
                "source": current_source or "Unspecified",
                "page": current_page or "Unspecified",
                "section": current_section or "Null",
                "subsection": current_subsection or "Null",
                "sub_subsection": current_sub_subsection or "Null",
            },
        )
        current_text_lines = []


# Process line by line
lines = markdown_text.splitlines()
i = 0
while i < len(lines):
    line = lines[i].strip()

    if re.match(source_pattern, line):
        flush_current_text()
        current_source = re.match(source_pattern, line).group(1)

    elif re.match(page_pattern, line):
        flush_current_text()
        current_page = int(re.match(page_pattern, line).group(1))

    elif re.match(section_pattern, line):
        flush_current_text()
        current_section = re.match(section_pattern, line).group(1)
        current_subsection = None
        current_sub_subsection = None  # Reset lower levels

    elif re.match(subsection_pattern, line):
        flush_current_text()
        current_subsection = re.match(subsection_pattern, line).group(1)
        current_sub_subsection = None  # Reset lower level

    elif re.match(sub_subsection_pattern, line):
        flush_current_text()
        current_sub_subsection = re.match(sub_subsection_pattern, line).group(1)

    elif re.match(table_pattern, line):
        flush_current_text()
        # Capture table lines
        table_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line or re.match(
                r"^#|##|###|####|\*\*TABLE \d+\*\*", next_line
            ):
                i -= 1  # Reprocess next header or table
                break
            table_lines.append(next_line)
            i += 1

        chunks.append(
            {
                "content": "\n".join(table_lines).strip(),
                "metadata": {
                    "source": current_source or "Unspecified",
                    "page": current_page or "Unspecified",
                    "section": current_section or "Null",
                    "subsection": current_subsection or "Null",
                    "sub_subsection": current_sub_subsection or "Null",
                    "type": "table",
                    "chunk_id": chunk_id_counter,
                },
            }
        )
        chunk_id_counter += 1

    else:
        current_text_lines.append(line)

    i += 1

# Flush any remaining text
flush_current_text()

# Save to JSON
with open("a_review_of_literature_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"✅ {len(chunks)} chunks saved to threats_to_valid_use_chunks.json.")
