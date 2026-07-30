import streamlit as st
from assistant import load_assistant
from db_save import save_conversation

st.set_page_config(page_title="GeoAI Research Assistant", layout="wide")

@st.cache_resource
def get_assistant():
    return load_assistant()

assistant = get_assistant()

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

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if query := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        with st.spinner("Searching papers..."):
            answer = assistant.rag(query)
        st.write(answer)

        record = assistant.last_call

        st.write(f"Response time: {record.response_time:.2f}s")

        conversation_id = save_conversation(
            record,
            query,
            "geoai-research-assistant",
        )

        st.session_state.conversation_id = conversation_id

    st.session_state.messages.append({"role": "assistant", "content": answer})