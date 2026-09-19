"""
STEP 4: The Report Generator
------------------------------
Takes the synthesized findings from Step 3 and formats them into a final,
polished, structured report.

This is the 3rd and final Gemini API call in the agent.
"""

import os
import time
from google import genai
from google.genai import errors

from config import API_KEY
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.6-flash"


def call_gemini_with_retry(prompt: str, max_retries: int = 3, delay_seconds: int = 5) -> str:
    """
    Calls Gemini, automatically retrying if the server is temporarily
    overloaded (503 error). Waits a bit longer each retry.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )
            return response.text.strip()
        except errors.ServerError as e:
            print(f"    Gemini server busy (attempt {attempt}/{max_retries}). Retrying in {delay_seconds}s...")
            if attempt == max_retries:
                raise
            time.sleep(delay_seconds)
            delay_seconds *= 2  # wait longer each time


def generate_report(topic: str, synthesized_findings: str, sources: list[str] = None) -> str:
    """
    Takes the raw synthesized findings text and turns it into a final,
    clean report with a summary and key sections.

    'sources' (optional) is a plain list of URLs. If provided, a Sources
    section is appended at the very end -- built directly in code, not by
    the LLM, so it's always accurate and never clutters the writing.
    """

    prompt = f"""
You are a report writer. Turn the research findings below into a polished,
clean report on the topic: "{topic}"

FINDINGS:
{synthesized_findings}

Format the report using proper Markdown exactly like this:

# {topic}

## Summary
(2-3 sentence high-level overview)

## Key Findings
(Organized into short ### sub-headed sections based on the themes in the
findings. Use **bold** for key terms where useful. Write clean, readable
paragraphs.)

Rules:
- Do NOT mention URLs, sources, or citations anywhere in this text
- Keep it clean and simple -- no clutter, no filler sentences
- Output only the report in this format. No preamble, no extra commentary.
"""

    report = call_gemini_with_retry(prompt)

    if sources:
        unique_sources = list(dict.fromkeys(sources))  # dedupe, keep order
        sources_section = "\n\n## Sources\n" + "\n".join(f"- {url}" for url in unique_sources)
        report += sources_section

    return report
