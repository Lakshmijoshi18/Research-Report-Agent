"""
STEP 3: The Synthesizer
------------------------
Takes all the search results gathered for every sub-question and asks
Gemini to merge them into clean, coherent findings -- while tracking
which source each fact came from.

This is the 2nd Gemini API call in the whole agent (Step 1's planner was
the 1st).
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


def synthesize_findings(topic: str, research_data: list[dict]) -> str:
    """
    research_data is a list of dicts like:
      {
        "question": "What are the current AI diagnostic tools?",
        "results": [ {"title": ..., "url": ..., "snippet": ...}, ... ]
      }

    Returns a single block of synthesized text with inline source mentions.
    """

    # Build a plain-text dump of everything gathered, so Gemini can read it
    context_blocks = []
    for item in research_data:
        block = f"Sub-question: {item['question']}\n"
        for r in item["results"]:
            # 'content' is the full fetched article text if available,
            # otherwise it falls back to the short snippet
            text = r.get("content", r.get("snippet", ""))
            block += f"- Title: {r['title']}\n  Content: {text}\n"
        context_blocks.append(block)

    full_context = "\n\n".join(context_blocks)

    prompt = f"""
You are a research synthesizer. Below is raw research gathered from the web
for the topic: "{topic}"

{full_context}

Your task:
- Merge these findings into clear, well-organized paragraphs
- Group related points together, don't just list snippets
- Do NOT mention URLs, sources, or citations anywhere in this text -- just
  write the findings as clean, standalone paragraphs
- Skip anything irrelevant or too vague to be useful
- Do not add information that isn't in the research above
- Write in plain, direct language, no fluff

Output only the synthesized findings text. No preamble.
"""

    return call_gemini_with_retry(prompt)
