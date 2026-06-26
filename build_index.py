from ingest import load_geoai_papers
from sqlitesearch import TextSearchIndex

documents = load_geoai_papers(max_results=500)

print(f"Loaded {len(documents)} papers")

index = TextSearchIndex(
    text_fields = ["title", "authors", "year", "url", "answer"],
    keyword_fields = ["topic"],
    db_path = "geoai.db"
)

for doc in documents:

    index.add(doc)


index.close()

print("Done. Index saved to geoai.db")