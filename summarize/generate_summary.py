import re
import os 
import sys
import json 
from pathlib import Path
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUT_DIR, UPLOADS_DIR
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI






def normalize_section_name(header):

    header = header.strip()

    return header.lower()


def extract_sections(md_text):
    
    SECTION_HEADER_PATTERN = re.compile(
        r"^##\s+(.+)$"
    )

    lines = md_text.splitlines()

    sections = {}

    # ---------- پیدا کردن Header ها ----------

    headers = []

    for idx, line in enumerate(lines):

        match = SECTION_HEADER_PATTERN.match(
            line.strip()
        )

        if match:

            headers.append(
                (
                    idx,
                    match.group(1).strip()
                )
            )

    if not headers:
        return None

    # ---------- Title ----------

    title = headers[0][1]

    # ---------- Abstract ----------

    intro_idx = None

    for line_idx, header in headers:

        if "introduction" in header.lower():

            intro_idx = line_idx
            break

    abstract_text = ""

    if intro_idx:

        text_before_intro = "\n".join(
            lines[:intro_idx]
        )

        match = re.search(
            r"abstract\s+(.*)",
            text_before_intro,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:

            abstract_text = match.group(1).strip()

    # ---------- سایر سکشن‌ها ----------

    for i in range(1, len(headers)):

        current_line, current_header = (
            headers[i]
        )

        next_line = (
            headers[i + 1][0]
            if i + 1 < len(headers)
            else len(lines)
        )

        section_text = "\n".join(
            lines[
                current_line + 1:
                next_line
            ]
        ).strip()

        section_name = (
            normalize_section_name(
                current_header
            )
        )
        if section_name in ["references", "bibliography", "orcid", "acknowledgments"]:
            continue
        sections[
            section_name
        ] = section_text

    document_profile = {

        "title": title,

        "abstract": abstract_text,

        "sections_found": list(
            sections.keys()
        ),

        "num_sections": len(
            sections
        )
    }

    return {

        "document_profile":
            document_profile,

        "sections":
            sections
    }



from collections import defaultdict
import re



import re


ROMAN_PATTERN = re.compile(
    r"^(i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv|xvi|xvii|xviii|xix|xx)\.",
    re.IGNORECASE
)

NUMERIC_PATTERN = re.compile(
    r"^(\d+)"
)

SUPPLEMENT_PATTERN = re.compile(
    r"^(s\d+)\.",
    re.IGNORECASE
)

LETTER_PATTERN = re.compile(
    r"^[a-z]\.",
    re.IGNORECASE
)


def get_root_section(section_title):

    title = section_title.strip().lower()

    # 1. Introduction
    m = NUMERIC_PATTERN.match(title)
    if m:
        return m.group(1)

    # iv. Architecture
    m = ROMAN_PATTERN.match(title)
    if m:
        return m.group(1)

    # s14. Something
    m = SUPPLEMENT_PATTERN.match(title)
    if m:
        return m.group(1)

    # a. Dataset
    m = LETTER_PATTERN.match(title)
    if m:
        return "__SUBSECTION__"

    return None

from collections import defaultdict


def create_summary_blocks(output):

    MIN_SECTION_LENGTH = 150

    sections = []

    for title, content in output["sections"].items():

        if len(content.strip()) < MIN_SECTION_LENGTH:
            continue

        sections.append(
            {
                "title": title,
                "content": content
            }
        )

    if not sections:
        return []

    # --------------------------------------------------
    # آیا سکشن شماره گذاری شده داریم؟
    # --------------------------------------------------

    has_numbered_sections = any(

        (
            get_root_section(
                section["title"]
            ) not in (
                None,
                "__SUBSECTION__"
            )
        )

        for section in sections
    )

    # --------------------------------------------------
    # مقاله بدون شماره گذاری
    # --------------------------------------------------

    if not has_numbered_sections:

        return [

            {
                "root_section":
                    section["title"],

                "title":
                    section["title"],

                "content":
                    section["content"]
            }

            for section in sections
        ]

    # --------------------------------------------------
    # مقاله شماره گذاری شده
    # --------------------------------------------------

    grouped_sections = defaultdict(list)

    current_root = None

    for section in sections:

        root = get_root_section(
            section["title"]
        )

        # -----------------------------------------
        # Root section
        # -----------------------------------------

        if root not in (
            None,
            "__SUBSECTION__"
        ):

            current_root = root

            grouped_sections[
                current_root
            ].append(
                section
            )

        # -----------------------------------------
        # a. b. c.
        # -----------------------------------------

        elif root == "__SUBSECTION__":

            if current_root is not None:

                grouped_sections[
                    current_root
                ].append(
                    section
                )

            else:

                grouped_sections[
                    section["title"]
                ].append(
                    section
                )

        # -----------------------------------------
        # data availability
        # references
        # acknowledgements
        # ...
        # -----------------------------------------

        else:

            grouped_sections[
                section["title"]
            ].append(
                section
            )

    summarization_blocks = []

    for root, group in grouped_sections.items():

        merged_text = "\n\n".join(

            section["content"]

            for section in group

        )

        summarization_blocks.append(

            {
                "root_section": root,

                "title":
                    group[0]["title"],

                "content":
                    merged_text
            }
        )

    return summarization_blocks

def section_summary(llm, summarization_blocks, summary_language):
    Section_summary_prompt = """
    You are an expert scientific research assistant.

    Your task is to summarize a section of an academic paper.

    Summary language: {language}

    Instructions:

    - Preserve the technical meaning.
    - Focus on the key ideas, methods, findings, and contributions.
    - Remove redundancy and minor details.
    - Keep important terminology unchanged when necessary.
    - Do not invent information.
    - Do not add your own interpretation.
    - Write in a clear academic style.
    - Produce a concise but informative summary.

    Section Content:

    {content}

    Summary:
    """

    SECTION_SUMMARY_PROMPT = ChatPromptTemplate.from_template(
        Section_summary_prompt
    )

    # Chain
    summary_chain = SECTION_SUMMARY_PROMPT | llm

    section_summaries = []

    for block in summarization_blocks:


        summary = summary_chain.invoke({
            "content":block['content'],
            "language":summary_language}
        )

        section_summaries.append(
            {
                "root_section":
                    block["root_section"],

                "title":
                    block["title"],

                "summary":
                    summary
            }
        )
        for item in section_summaries:
            if isinstance(item.get('summary'), dict) and 'content' in item['summary']:
                # Assuming it's a dict that might contain AIMessage content
                item['summary'] = item['summary']['content'][0]['text']
            elif hasattr(item.get('summary'), 'content') and isinstance(item['summary'].content, list) and item['summary'].content and 'text' in item['summary'].content[0]:
                # Extract the text from the AIMessage object
                item['summary'] = item['summary'].content[0]['text']

        # with open(
        #     "section_summaries.json",
        #     "w",
        #     encoding="utf-8"
        # ) as f:

        #     json.dump(
        #         section_summaries,
        #         f,
        #         indent=2,
        #         ensure_ascii=False
        #     )
    return section_summaries
    
def final_summary(llm, section_summaries, summary_language):
    all_summaries_text = "\n\n".join(

        f"Section: {item['title']}\n"
        f"{item['summary']}"

        for item in section_summaries
    )

    Final_summary_prompt = """
    You are an expert scientific research assistant.
    You have been given summaries of multiple sections from the same academic paper.
    Summary language: {language}

    Your task:

    - Produce a coherent, paper-level summary.
    - State the main goal of the paper.
    - Describe the key methods or approaches.
    - Report the most important findings.
    - Explain the significance of the work.
    - Maintain technical accuracy throughout.
    - Avoid repeating information across sections.
    - Do not add or invent any information.

    Section Summaries:

    {section_summaries}

    Final Paper Summary:
    """
    FINAL_SUMMARY_PROMPT = ChatPromptTemplate.from_template(Final_summary_prompt)
    final_summary_chain = FINAL_SUMMARY_PROMPT | llm

    final_summary = final_summary_chain.invoke({
        "language":summary_language,
        "section_summaries":all_summaries_text}
    )

    return final_summary


def paper_summary(llm, final_summary):

    Document_profile_prompt = """
    You are an expert scientific research assistant.

    Analyze the academic paper summary below.

    Output a JSON object with:

    - research_field
    - research_topics
    - keywords
    - main_contributions
    - methods
    - applications

    Summary:

    {paper_summary}

    JSON:
    """
    DOCUMENT_PROFILE_PROMPT = ChatPromptTemplate.from_template(Document_profile_prompt)
    paper_summary_chain = DOCUMENT_PROFILE_PROMPT | llm

    paper_summary = paper_summary_chain.invoke({
        "paper_summary":final_summary,
        }
    )

    return paper_summary



def main(llm, language):

    for paper_dir in OUTPUT_DIR.iterdir():

        if not paper_dir.is_dir():
            continue
          
        md_file = paper_dir/"text.md" # Correctly creates a Path object for the file
        print(paper_dir)

        if md_file.exists() and md_file.is_file():
            md_text = md_file.read_text(
                encoding="utf-8"
            )
        else:
            print(f"Warning: The file '{md_file}' was not found or is not a regular file.")
            md_text = "" # Assign an empty string or handle the error as appropriate
            continue
        output = extract_sections(md_text)
        # Save to JSON
        with open(
            f"{paper_dir}/root_sections.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                output,
                f,
                indent=2,
                ensure_ascii=False
            )

        summarization_blocks= create_summary_blocks(output)

        # Save to JSON
        with open(
            f"{paper_dir}/summary_blocks.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                summarization_blocks,
                f,
                indent=2,
                ensure_ascii=False
            )

        section_summaries=section_summary(llm, summarization_blocks, language)

        all_summaries_text = "\n\n".join(

        f"Section: {item['title']}\n"
        f"{item['summary']}"

        for item in section_summaries
    )
        final_summary1 = final_summary(llm, section_summaries, language)

        paper_summary1 = paper_summary(llm, final_summary1)

        paper_analysis = {

        "paper_summary":
            final_summary1.content[0]["text"],

        "section_summaries":
            section_summaries,

        "document_profile":
            paper_summary1.content[0]["text"]
    }
        with open(
        f"{paper_dir}/paper_analysis.json",
        "w",
        encoding="utf-8"
        ) as f:

            json.dump(
                paper_analysis,
                f,
                indent=2,
                ensure_ascii=False
            )


