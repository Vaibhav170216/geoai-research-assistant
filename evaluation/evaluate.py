import json
import os
import time
from pathlib import Path

import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv

from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextPrecisionWithoutReference,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "rag_outputs.json"
OUTPUT_CSV = BASE_DIR / "ragas_scores.csv"
OUTPUT_JSON = BASE_DIR / "ragas_summary.json"

TPM_BUDGET = 6000
TPM_SAFETY_MARGIN = 0.75         
EFFECTIVE_TPM = int(TPM_BUDGET * TPM_SAFETY_MARGIN)


MAX_CONTEXT_CHARS_PER_CHUNK = 800
MAX_CONTEXT_CHUNKS = 3

SLEEP_ON_FAILURE_SEC = 60
MAX_SAMPLE_RETRIES = 4


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    rag_outputs = json.load(f)

rows = []

for item in rag_outputs:

    if not item["answer"].strip():
        continue

    contexts = item["contexts"][:MAX_CONTEXT_CHUNKS]
    contexts = [c[:MAX_CONTEXT_CHARS_PER_CHUNK] for c in contexts]

    rows.append(
        {
            "user_input": item["question"],
            "response": item["answer"],
            "retrieved_contexts": contexts,
        }
    )

SAMPLE_LIMIT = 50   
if SAMPLE_LIMIT is not None:
    rows = rows[:SAMPLE_LIMIT]

print(f"Loaded {len(rows)} samples (contexts capped at {MAX_CONTEXT_CHUNKS} chunks x {MAX_CONTEXT_CHARS_PER_CHUNK} chars)")


judge = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

judge_llm = LangchainLLMWrapper(judge)


embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
)

# --------------------------------------------------
# Metrics
# --------------------------------------------------

response_relevancy = ResponseRelevancy()
response_relevancy.strictness = 1

metrics = [
    Faithfulness(),
    response_relevancy,
    LLMContextPrecisionWithoutReference(),
]

run_config = RunConfig(
    max_workers=1,
    timeout=180,
    max_retries=15,
    max_wait=60,
)


def estimate_tokens(row: dict) -> int:
    text = row["user_input"] + row["response"] + "".join(row["retrieved_contexts"])
    base_tokens = len(text) // 4
    call_multiplier = 4
    return base_tokens * call_multiplier


all_results = []

CHUNK_DIR = BASE_DIR / "ragas_chunks"
CHUNK_DIR.mkdir(exist_ok=True)

for i, row in enumerate(rows):

    chunk_path = CHUNK_DIR / f"sample_{i}.csv"

    if chunk_path.exists():
        print(f"Skipping sample {i+1}/{len(rows)} (already done)")
        all_results.append(pd.read_csv(chunk_path))
        continue

    est_tokens = estimate_tokens(row)
    print(f"\nSample {i+1}/{len(rows)} — estimated {est_tokens} tokens")

    single = Dataset.from_list([row])

    attempt = 0
    while attempt < MAX_SAMPLE_RETRIES:
        try:
            result = evaluate(
                dataset=single,
                metrics=metrics,
                llm=judge_llm,
                embeddings=embeddings,
                run_config=run_config,
                raise_exceptions=False,
            )
            df = result.to_pandas()
            df.to_csv(chunk_path, index=False)
            all_results.append(df)
            break
        except Exception as e:
            attempt += 1
            print(f"Sample {i+1} failed (attempt {attempt}/{MAX_SAMPLE_RETRIES}): {e}")
            if attempt < MAX_SAMPLE_RETRIES:
                print(f"Sleeping {SLEEP_ON_FAILURE_SEC}s before retry...")
                time.sleep(SLEEP_ON_FAILURE_SEC)
            else:
                print(f"Giving up on sample {i+1} after {MAX_SAMPLE_RETRIES} attempts.")

    sleep_needed = (est_tokens / EFFECTIVE_TPM) * 60
    sleep_needed = max(sleep_needed, 3)  
    print(f"Sleeping {sleep_needed:.1f}s before next sample...")
    time.sleep(sleep_needed)

# --------------------------------------------------
# Save
# --------------------------------------------------

if not all_results:
    raise SystemExit("No samples completed successfully — nothing to save.")

final_df = pd.concat(all_results, ignore_index=True)

final_df.to_csv(OUTPUT_CSV, index=False)

summary = {}

for col in final_df.columns:

    if col in {
        "user_input",
        "response",
        "retrieved_contexts",
    }:
        continue

    summary[col] = round(float(final_df[col].mean(skipna=True)), 4)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\nAverage Scores")

for k, v in summary.items():
    print(f"{k:35} {v:.4f}")

print(f"\nSaved CSV to {OUTPUT_CSV}")
print(f"Saved summary to {OUTPUT_JSON}")