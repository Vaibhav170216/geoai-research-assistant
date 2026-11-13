import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sqlitesearch import TextSearchIndex

from hybrid_search import load_vector_index
from metrics import RAGWithMetrics

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "geoai.db"
EMBEDDINGS_PATH = BASE_DIR / "geoai_embeddings.pkl"


def ensure_index_files():
    """Download missing RAG indexes from a Hugging Face dataset repository.

    Set ``HF_REPO_ID`` to a dataset repository such as
    ``your-username/geoai-rag-index``. For a private repository, also set
    ``HF_TOKEN`` to a read token. Local index files always take precedence.
    """
    required_files = (DATABASE_PATH, EMBEDDINGS_PATH)
    missing_files = [path for path in required_files if not path.is_file()]
    if not missing_files:
        return

    # Cloud Run environment values and Secret Manager payloads are used
    # literally; trim accidental whitespace/newlines before building the HF URL.
    repo_id = (os.getenv("HF_REPO_ID") or "").strip()
    if not repo_id:
        missing_names = ", ".join(path.name for path in missing_files)
        raise FileNotFoundError(
            f"Missing RAG index file(s): {missing_names}. Build the index locally "
            "or set HF_REPO_ID to a Hugging Face dataset repository."
        )
    if any(character.isspace() for character in repo_id):
        raise ValueError(
            "HF_REPO_ID must be a Hugging Face repo ID such as "
            "'Vaib9/geoai-rag-index', without spaces or line breaks."
        )

    token = (os.getenv("HF_TOKEN") or "").strip() or None
    revision = (os.getenv("HF_REVISION") or "").strip() or None
    for local_path in missing_files:
        print(f"Downloading {local_path.name} from Hugging Face dataset {repo_id}...")
        hf_hub_download(
            repo_id=repo_id,
            repo_type="dataset",
            filename=local_path.name,
            local_dir=BASE_DIR,
            token=token,
            revision=revision,
        )

    still_missing = [path.name for path in required_files if not path.is_file()]
    if still_missing:
        raise FileNotFoundError(
            "Hugging Face download completed but index file(s) are still missing: "
            + ", ".join(still_missing)
        )


def load_assistant():
    ensure_index_files()

    index = TextSearchIndex(
        text_fields=["title", "authors", "answer"],
        keyword_fields=["topic"],
        db_path=DATABASE_PATH,
    )

    documents, embeddings = load_vector_index()

    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    return RAGWithMetrics(
        index=index,
        documents=documents,
        embeddings=embeddings,
        encoder=encoder,
        llm_client=client
    )
