import requests
import xml.etree.ElementTree as ET

TOPICS = [
    "earth observation",
    "remote sensing",
    "satellite imagery",
    
    "vision transformer remote sensing",
    "change detection",
    "multispectral image analysis",
    "self supervised remote sensing",

    "foundation model earth observation",
    "geospatial foundation model",
    "remote sensing foundation model",

    "large language model remote sensing",
    "multimodal earth observation",
    "earth observation transformer",
]

BASE_URL = "https://export.arxiv.org/api/query"


def load_geoai_papers(max_results=2000):

    documents = []

    papers_per_topic = max_results // len(TOPICS)

    namespaces = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    for topic in TOPICS:

        print(f"Fetching papers for: {topic}")

        params = {
            "search_query": f'all:"{topic}"',
            "start": 0,
            "max_results": papers_per_topic,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        for entry in root.findall("atom:entry", namespaces):

            title = entry.find("atom:title", namespaces).text.strip()

            summary = entry.find("atom:summary", namespaces).text.strip()

            published = entry.find("atom:published", namespaces).text[:4]

            url = entry.find("atom:id", namespaces).text

            authors = ", ".join(
                author.find("atom:name", namespaces).text
                for author in entry.findall("atom:author", namespaces)
            )

            documents.append(
                {
                    "topic": topic,
                    "title": title,
                    "answer": summary,
                    "authors": authors,
                    "year": int(published),
                    "url": url,
                }
            )

    return documents