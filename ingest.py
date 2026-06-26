import arxiv

TOPICS = [
    "geoai",
    "earth observation",
    "remote sensing",
    "sentinel-2",
    "land use land cover classification",
    "vision transformer",
    "foundation models",
    "change detection",
    "satellite imagery",
    "self-supervised learning"
]

def load_geoai_papers(max_results = 500):

    documents = []

    papers_per_topic = max_results // len(TOPICS)

    for topic in TOPICS:

        print(f"Fetching papers for: {topic}")

        search = arxiv.Search(
            query = topic,
            max_results = papers_per_topic,
            sort_by = arxiv.SortCriterion.Relevance
        )

        for paper in search.results():

            documents.append({
                "topic": topic,
                "title": paper.title,
                "answer": paper.summary,
                "authors": ", ".join(
                    author.name for author in paper.authors
                ),
                "year": paper.published.year,
                "url": paper.entry_id
            })

    return documents
