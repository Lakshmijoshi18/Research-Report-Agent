"""
STEP 1: The Planner
--------------------
This is the very first building block of your research agent.

What it does:
  1. Takes a topic from the user (e.g. "AI in healthcare")
  2. Sends it to Gemini with instructions to break it into 3-4 focused
     sub-questions
  3. Parses Gemini's response as JSON and returns the sub-questions

Also supports basic SESSION MEMORY: if you pass in a list of topics
already researched earlier in this session, Gemini is told about them so
it can avoid redundant sub-questions. This only adds a few extra words to
the prompt, so the cost impact is negligible.

SETUP (one-time):
  1. pip install google-genai
  2. Get your API key from https://aistudio.google.com/app/apikey
  3. Set it as an environment variable:
       Mac/Linux:  export GEMINI_API_KEY="your-key-here"
       Windows:    set GEMINI_API_KEY=your-key-here
"""

import json
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
        except errors.ServerError:
            print(f"    Gemini server busy (attempt {attempt}/{max_retries}). Retrying in {delay_seconds}s...")
            if attempt == max_retries:
                raise
            time.sleep(delay_seconds)
            delay_seconds *= 2


def plan_research(topic: str, session_history: list[str] = None) -> list[str]:
    """
    Given a topic, ask Gemini to break it into focused sub-questions.
    Returns a list of sub-question strings.

    session_history (optional): a list of topic titles the user has already
    researched earlier in this same session. This is basic "memory" -- it
    only sends topic titles, not full content, so the extra cost is negligible.
    """

    memory_note = ""
    if session_history:
        past_topics = ", ".join(session_history)
        memory_note = (
            f"\nNote: earlier in this session, the user already researched: "
            f"{past_topics}. Avoid redundant sub-questions if this new topic overlaps."
        )

    prompt = f"""
You are a research planning assistant. Given a topic, break it into 3 to 4
focused, non-overlapping sub-questions that together would give a complete
picture of the topic if answered.

Respond with ONLY a JSON array of strings. No explanation, no markdown,
no code fences.
{memory_note}

Topic: {topic}
"""

    raw_text = call_gemini_with_retry(prompt)

    # Defensive parsing: sometimes models wrap JSON in extra text or fences.
    start = raw_text.find("[")
    end = raw_text.rfind("]") + 1
    json_block = raw_text[start:end]

    try:
        return json.loads(json_block)
    except json.JSONDecodeError:
        print("Could not parse Gemini's response as JSON. Raw response was:")
        print(raw_text)
        return []


if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()

    if not topic:
        print("Please enter a topic.")
    else:
        print(f"\nPlanning research for: {topic}\n")
        questions = plan_research(topic)

        if questions:
            print("Sub-questions generated:")
            for i, q in enumerate(questions, start=1):
                print(f"  {i}. {q}")
        else:
            print("No sub-questions were generated. Try running it again.")
