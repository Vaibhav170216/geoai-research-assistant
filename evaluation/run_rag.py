import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
from tqdm import tqdm
import time


from assistant import load_assistant

assistant = load_assistant()

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

results = []

for item in tqdm(questions):

    question = item["question"]

    answer, docs = assistant.rag(
        question,
        return_context=True,
        num_results = 2
    )
    time.sleep(6)

    contexts = []

    for doc in docs:
        contexts.append(doc["answer"])

    results.append(
        {
            "question": question,
            "answer": answer,
            "contexts": contexts,
        }
    )

with open("rag_outputs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved {len(results)} examples.")