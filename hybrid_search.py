import numpy as np
import pickle
import os

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDINGS_PATH = "geoai_embeddings.pkl"


def load_vector_index(load_path=EMBEDDINGS_PATH):

    if not os.path.exists(load_path):
        raise FileNotFoundError(
            f"Vector index not found at {load_path}. "
            "Run build_index.py first."
        )
    with open(load_path, "rb") as f:
        data = pickle.load(f)

    return data["documents"], np.array(data["embeddings"])


def vector_search(query, documents, embeddings, model, num_results=10):
    
    query_embedding = model.encode([query])[0]

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normed = embeddings / np.clip(norms, 1e-10, None)
    query_norm = query_embedding / np.linalg.norm(query_embedding)

    scores = normed @ query_norm
    top_indices = np.argsort(scores)[::-1][:num_results]

    return [(documents[i], float(scores[i])) for i in top_indices]


def reciprocal_rank_fusion(keyword_results, vector_results, k=60):
    
    scores = {} 
    docs_by_title = {}

    for rank, doc in enumerate(keyword_results):

        title = doc.get("title", "")
        scores[title] = scores.get(title, 0) + 1 / (k + rank + 1)
        docs_by_title[title] = doc

    for rank, (doc, _) in enumerate(vector_results):

        title = doc.get("title", "")
        scores[title] = scores.get(title, 0) + 1 / (k + rank + 1)
        docs_by_title[title] = doc

    sorted_titles = sorted(scores, key=lambda t: scores[t], reverse=True)
    
    return [docs_by_title[t] for t in sorted_titles]


