from ingest import load_geoai_papers
from sqlitesearch import TextSearchIndex
from build_embeddings import build_vector_index

documents = load_geoai_papers(max_results=2000)

print(f"Loaded {len(documents)} papers")

index = TextSearchIndex(
    text_fields = ["title", "authors", "answer"],
    keyword_fields = ["topic"],
    db_path = "geoai.db"
)

for doc in documents:

    index.add(doc)


index.close()

print("Done. Index saved to geoai.db")

build_vector_index(documents)