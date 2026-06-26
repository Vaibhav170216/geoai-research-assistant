from sqlitesearch import TextSearchIndex
from rag_helper import RAGBase
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

st.set_page_config(page_title="FAQ RAG Helper", layout="wide")

@st.cache_resource
def load_assistant():
    index = TextSearchIndex(
        text_fields=["title", "authors", "year", "url", "answer"],
        keyword_fields=["topic"],
        db_path="geoai.db"
    )
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    return RAGBase(index=index, llm_client=client)

assistant = load_assistant()

with st.sidebar:
    st.title("Knowledge Base")
    st.metric("Papers", assistant.index.count())
    topic = st.selectbox("Topic", [
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
    ])
    assistant.topic = topic

st.title("GeoAI Research Assistant")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if query := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            answer = assistant.rag(query)
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})