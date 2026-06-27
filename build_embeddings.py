from ingest import load_geoai_papers
from sentence_transformers import SentenceTransformer
import pickle

documents = load_geoai_papers(max_results=2000)

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDINGS_PATH = "geoai_embeddings.pkl"


def build_vector_index(documents, save_path=EMBEDDINGS_PATH):
    
    model = SentenceTransformer(MODEL_NAME)

    texts = [doc_to_text(doc) for doc in documents]

    print(f"Encoding {len(texts)} documents with {MODEL_NAME}...")

    embeddings = model.encode(
        texts, 
        show_progress_bar=True, 
        batch_size=32
    )

    with open(save_path, "wb") as f:
        pickle.dump({"documents": documents, "embeddings": embeddings}, f)

    print(f"Vector index saved to {save_path}")
    return embeddings


def doc_to_text(doc):

    parts = [
        doc.get("title", ""),
        doc.get("topic", ""),
        doc.get("answer", ""),
    ]
    return " ".join(p for p in parts if p)