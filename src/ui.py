import streamlit as st
import sys
from pathlib import Path

file_path = Path(__file__).resolve()
PROJECT_ROOT = file_path.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import process_document
from src.engine import lexguard_agent, search_knowledge

st.set_page_config(page_title="LexGuard AI", page_icon="🛡️", layout="wide")
st.title("🛡️ LexGuard: Secure Document Intelligence")

if "active_file" not in st.session_state:
    st.session_state.active_file = None

st.markdown("---")

with st.sidebar:
    st.header("📂 Document Ingestion")
    uploaded_file = st.file_uploader("Upload a PDF for analysis", type="pdf")

    if st.button("Index Document") and uploaded_file:
        data_dir = PROJECT_ROOT / "data"
        data_dir.mkdir(exist_ok=True)
        save_path = data_dir / uploaded_file.name

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        progress_bar = st.progress(0)
        status_text = st.empty()

        for percent, result in process_document(str(save_path)):
            progress_bar.progress(percent)
            if result is None:
                status_text.text(f"Processing document: {percent}%")
            elif isinstance(result, int):
                st.session_state.active_file = uploaded_file.name
                st.success(f"Successfully indexed {result} structural clusters.")
                status_text.empty()
            else:
                st.error(f"❌ System Fault: {result}")

st.header("💬 Chat with your Data")

if st.session_state.active_file:
    st.caption(f"Currently analyzing: **{st.session_state.active_file}**")
else:
    st.info("Please index a document in the sidebar to begin.")

user_input = st.text_input("Enter your question about the uploaded document:")

if user_input and st.session_state.active_file:
    with st.spinner("LexGuard Agent is navigating the document manifold..."):
        inputs = {
            "question": user_input,
            "target_file": st.session_state.active_file,
            "documents": [],
            "relevance": "",
            "loop_count": 0,
        }
        result = lexguard_agent.invoke(inputs)

        if result.get("relevance") == "yes":
            st.chat_message("assistant").write(result["generation"])

            with st.expander("📚 Evidence Manifold & Citations"):
                docs = search_knowledge(user_input, filter_file=st.session_state.active_file)
                for doc in docs:
                    page = doc.metadata.get("page_label", "Unknown")
                    st.markdown(f"**Page {page}:** {doc.page_content[:300]}...")
        else:
            st.warning("🔍 **Final Information Gap**")
            st.info("The agent attempted multiple query rewrites but could not identify the data.")