import re
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load the Markdown content
with open(
    r"C:\Users\Maham Jafri\Documents\Office Tasks\Durbeen\CoreTextbooks\measure_and_assess_teaching\measurement_and_assement_in_teaching.MD",
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

# Updated Regex patterns to match new structure
source_pattern = r"^# (.+)"
book_section_pattern = r"^## (.+)"
chapter_pattern = r"^### (.+)"
section_pattern = r"^#### (.+)"
subsection_pattern = r"^##### (.+)"
page_pattern = r"\*\*Page (\d+)\*\*"
table_pattern = r"\*\*TABLE-[^\*]+\*\*"

# Tracking variables
chunks = []
chunk_id_counter = 1
current_source = None
current_page = None
current_book_section = None
current_chapter = None
current_section = None
current_subsection = None
current_text_lines = []


def store_sub_subsection_chunk(text, meta, force_single_chunk=False):
    """Store text as a chunk, optionally forcing it to not split (e.g., for tables)."""
    global chunk_id_counter
    if not text.strip():
        return

    if force_single_chunk:
        chunks.append(
            {
                "content": text.strip(),
                "metadata": {**meta, "chunk_id": chunk_id_counter},
            }
        )
        chunk_id_counter += 1
    elif len(text.split()) > 300:
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
                "book_section": current_book_section or "Null",
                "chapter": current_chapter or "Null",
                "section": current_section or "Null",
                "subsection": current_subsection or "Null",
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

    elif re.match(book_section_pattern, line):
        flush_current_text()
        current_book_section = re.match(book_section_pattern, line).group(1)
        current_chapter = None
        current_section = None
        current_subsection = None

    elif re.match(chapter_pattern, line):
        flush_current_text()
        current_chapter = re.match(chapter_pattern, line).group(1)
        current_section = None
        current_subsection = None

    elif re.match(section_pattern, line):
        flush_current_text()
        current_section = re.match(section_pattern, line).group(1)
        current_subsection = None

    elif re.match(subsection_pattern, line):
        flush_current_text()
        current_subsection = re.match(subsection_pattern, line).group(1)

    elif re.match(page_pattern, line):
        flush_current_text()
        current_page = int(re.match(page_pattern, line).group(1))

    elif re.match(table_pattern, line):
        flush_current_text()
        table_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line or re.match(
                r"^#|##|###|####|#####|\*\*TABLE-[^\*]+\*\*", next_line
            ):
                i -= 1
                break
            table_lines.append(next_line)
            i += 1

        store_sub_subsection_chunk(
            "\n".join(table_lines).strip(),
            {
                "source": current_source or "Unspecified",
                "page": current_page or "Unspecified",
                "book_section": current_book_section or "Null",
                "chapter": current_chapter or "Null",
                "section": current_section or "Null",
                "subsection": current_subsection or "Null",
                "type": "table",
            },
            force_single_chunk=True,
        )

    else:
        current_text_lines.append(line)

    i += 1

flush_current_text()

# Save to JSON
with open("measure_assess_teaching.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"✅ {len(chunks)} chunks saved to clay_and_root_chunks.json.")
