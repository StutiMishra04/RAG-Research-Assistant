from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src import pdf_processor
import os


def create_documents_and_vectorstore(pdf_path: str):
    documents = []

    all_chunks = pdf_processor.process_pdf_with_images(pdf_path)
    for chunk in all_chunks:
        doc = Document(
            page_content=chunk['content'],
            metadata={
                'page': chunk['page'],
                'type': chunk['type'],
                'source': pdf_path  # Add source info
                }
            )
        documents.append(doc)
        
    # Now create the vectorstore
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"  # Popular lightweight model
    )
    
    vectorstore = Chroma.from_documents(
        documents=documents,  # Use the converted documents
        embedding=embeddings
    )
    
    # Create a retriever from your vectorstore
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}  # Get top 5 most relevant chunks
    )

    return retriever