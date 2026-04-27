from docx import Document
import json
import re

INPUT_DOCX = "04.20.26 Attitudes on the Supreme Court_ss gs.docx"
OUTPUT_JSON = "data.json"


def paragraph_text(paragraph):
    return "".join(run.text for run in paragraph.runs).strip()


def get_bold_prefix(paragraph):
    """
    Returns the bolded text at the beginning of a paragraph.
    Example:
    Bold runs: "Jane Doe"
    Full paragraph: "Jane Doe (ID 123): This is the quote."
    """
    bold_text = ""

    for run in paragraph.runs:
        text = run.text

        if not text:
            continue

        if run.bold:
            bold_text += text
        else:
            # stop once normal text begins
            if bold_text.strip():
                break

    return bold_text.strip()


def parse_docx(path):
    doc = Document(path)

    sections = []
    current_header_parts = []
    current_section = None

    for para in doc.paragraphs:
        text = paragraph_text(para)

        if not text:
            continue

        bold_prefix = get_bold_prefix(para)

        # Detect quote paragraph:
        # Bolded name + (id): quote
        if bold_prefix:
            pattern = rf"^{re.escape(bold_prefix)}\s*\((.*?)\)\s*:\s*(.*)$"
            match = re.match(pattern, text, flags=re.DOTALL)

            if match:
                person = bold_prefix.strip()
                id_info = match.group(1).strip()
                quote = match.group(2).strip()

                # Start a new section if needed
                if current_section is None:
                    header = "\n\n".join(current_header_parts).strip()
                    current_section = {
                        "header": header,
                        "conversation": []
                    }
                    sections.append(current_section)
                    current_header_parts = []

                current_section["conversation"].append({
                    "person": person,
                    "id": id_info,
                    "quote": quote
                })

                continue

        # If paragraph is not a quote, treat it as intro/header text.
        # Once we've already started a section, a new intro paragraph starts a new section.
        if current_section is not None:
            current_section = None
            current_header_parts = [text]
        else:
            current_header_parts.append(text)

    return sections


data = parse_docx(INPUT_DOCX)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Saved {OUTPUT_JSON}")
print(f"Sections found: {len(data)}")
print(f"Total quotes found: {sum(len(section['conversation']) for section in data)}")