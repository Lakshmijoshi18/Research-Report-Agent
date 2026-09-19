"""
MAIN: Runs the full Research & Report Agent end-to-end.

Pipeline: Planner -> Search Tool -> Synthesizer -> Report Generator

Make sure planner.py, search_tool.py, synthesizer.py, and report_generator.py
are all in the SAME folder as this file.
"""

from planner import plan_research
from search_tool import search_web
from fetch_tool import fetch_article_text
from synthesizer import synthesize_findings
from report_generator import generate_report


def run_agent(topic: str) -> str:
    print(f"\n[1/4] Planning research for: {topic}")
    sub_questions = plan_research(topic)

    if not sub_questions:
        return "Could not generate sub-questions. Try again."

    print(f"    Generated {len(sub_questions)} sub-questions.")

    print("[2/4] Searching the web and fetching article content...")
    research_data = []
    for q in sub_questions:
        results = search_web(q, max_results=3)

        for r in results:
            full_text = fetch_article_text(r["url"])
            # If fetching worked, use the full text. Otherwise, fall back
            # to the snippet so we still have *something* for this source.
            r["content"] = full_text if full_text else r["snippet"]

        research_data.append({"question": q, "results": results})
        fetched_count = sum(1 for r in results if r["content"] != r["snippet"])
        print(f"    - '{q}' -> {len(results)} results ({fetched_count} full articles fetched)")

    print("[3/4] Synthesizing findings...")
    findings = synthesize_findings(topic, research_data)

    print("[4/4] Generating final report...")
    # Collect every URL we actually found, so the Sources section (if used)
    # is built from real data, not the LLM's memory
    all_urls = [r["url"] for item in research_data for r in item["results"]]

    # Set include_sources=False below if you don't want a Sources section at all
    include_sources = False
    report = generate_report(topic, findings, sources=all_urls if include_sources else None)

    return report


if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()

    if not topic:
        print("Please enter a topic.")
    else:
        final_report = run_agent(topic)
        print("\n" + "=" * 60)
        print(final_report)
        print("=" * 60)

        # Save to a file too, so you have a copy
        filename = "report_output.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_report)
        print(f"\nReport also saved to {filename}")
