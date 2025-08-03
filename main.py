import uuid
import os
import streamlit as st
from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from src import get_prompt, llm_qa, embeddings_and_retriever
from dotenv import load_dotenv
load_dotenv()

# === Environment Variables ===
os.environ['LANGSMITH_TRACING_V2'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# === Setup ===
prompt = get_prompt.get_prompt()
chatmodel = llm_qa.get_chatmodel()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# === Streamlit UI ===
st.title("📚 RAG-powered Research Assistant")
st.markdown("Upload your documents and ask questions!")

uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
user_input = st.text_input("Enter your prompt:")

latch = False
if st.button("Generate.."):
    if user_input:
        with st.spinner("Processing..."):
            os.makedirs("data", exist_ok=True)
            if uploaded_files:
                file_paths = []
                for uploaded_file in uploaded_files:
                    filename = f"{uuid.uuid4()}_{uploaded_file.name}"
                    path = os.path.join("data", filename)
                    with open(path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                        file_paths.append(path)
                retriever = embeddings_and_retriever.create_documents_and_vectorstore(file_paths)
            
            else:
                retriever = embeddings_and_retriever.load_existing_vectorstore()

        rag_chain = (
            {
                "context": itemgetter("question") | retriever | format_docs,
                "question": itemgetter("question")
            }
            | prompt
            | chatmodel
            | StrOutputParser()
        )

        result = rag_chain.invoke({"question": user_input})
        st.success("Answer generated:")
        st.write(result)