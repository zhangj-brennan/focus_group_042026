from docx import Document
import json
import re

INPUT_DOCX = "nointro_04.27.26 Attitudes on the Supreme Court_CLEAN.docx"
OUTPUT_JSON = "data_topics.json"

TOPICS = [
    "Perceptions of the Supreme Court",
    "Checks and balances",
    "Lifetime appointments vs. term limits",
    "Ethics concerns",
    "Court reform priorities"
]


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def paragraph_text(paragraph):
    return clean_text("".join(run.text for run in paragraph.runs))


def get_bold_prefix(paragraph):
    bold_text = ""

    for run in paragraph.runs:
        if not run.text:
            continue

        if run.bold:
            bold_text += run.text
        else:
            if bold_text.strip():
                break

    return clean_text(bold_text)


def is_topic(text):
    cleaned = clean_text(text).lstrip("o ").strip()
    for topic in TOPICS:
        if cleaned.lower() == topic.lower():
            return topic
    return None


def parse_docx(path):
    doc = Document(path)

    sections = []
    current_header_parts = []
    current_section = None
    current_topic = None

    for para in doc.paragraphs:
        text = paragraph_text(para)

        if not text:
            continue

        topic = is_topic(text)
        if topic:
            current_topic = topic
            continue

        bold_prefix = get_bold_prefix(para)

        if bold_prefix:
            pattern = rf"^{re.escape(bold_prefix)}\s*\((.*?)\)\s*:\s*(.*)$"
            match = re.match(pattern, text, flags=re.DOTALL)

            if match:
                person = bold_prefix
                id_info = match.group(1).strip()
                quote = match.group(2).strip()

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
                    "topic": current_topic,
                    "quote": quote
                })

                continue

        # Non-quote paragraphs become section intro/header text
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