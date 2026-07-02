from sqlitesearch import TextSearchIndex
from rag_helper import RAGBase
from hybrid_search import load_vector_index
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def load_assistant():
    index = TextSearchIndex(
        text_fields=["title", "authors", "answer"],
        keyword_fields=["topic"],
        db_path="geoai.db"
    )

    documents, embeddings = load_vector_index()

    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    return RAGBase(
        index=index,
        documents=documents,
        embeddings=embeddings,
        encoder=encoder,
        llm_client=client
    )