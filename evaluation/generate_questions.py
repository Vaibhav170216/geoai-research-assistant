import os
from dotenv import load_dotenv
import json
import random
import sqlite3
from pathlib import Path

from openai import OpenAI
from tqdm import tqdm

load_dotenv()

DB_PATH = "../geoai.db"
OUTPUT_FILE = "questions.json"

MODEL = "llama-3.3-70b-versatile"

TOTAL_QUESTIONS = 100
QUESTIONS_PER_PAPER = 2

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT doc_json FROM docs")
rows = cursor.fetchall()

conn.close()

papers = []

for row in rows:
    doc = json.loads(row[0])
    papers.append(doc)

random.shuffle(papers)

SYSTEM_PROMPT = """
You are generating evaluation questions for a GeoAI research assistant.

Generate exactly 2 high-quality questions that can be answered using ONLY
the supplied paper information.

Rules:

- Questions should be specific.
- Avoid yes/no questions.
- Avoid asking for authors or publication year.
- Focus on technical content.
- Return ONLY valid JSON.

Example:

{
    "questions": [
        "...",
        "..."
    ]
}
"""

questions = []

for paper in tqdm(papers):

    if len(questions) >= TOTAL_QUESTIONS:
        break

    prompt = f"""
Paper Title:
{paper['title']}

Topic:
{paper['topic']}

Abstract:
{paper['answer']}
"""

    try:

        response = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        data = json.loads(response.choices[0].message.content)

        for q in data["questions"]:

            if len(questions) >= TOTAL_QUESTIONS:
                break

            questions.append(
                {
                    "question": q,
                    "paper_title": paper["title"],
                    "topic": paper["topic"],
                    "url": paper["url"],
                }
            )

    except Exception as e:
        print(e)

Path(OUTPUT_FILE).write_text(
    json.dumps(questions, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"\nGenerated {len(questions)} questions.")
print(f"Saved to {OUTPUT_FILE}")