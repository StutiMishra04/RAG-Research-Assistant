RAG-Powered Research Assistant:

This is a local RAG (Retrieval-Augmented Generation) application built using LangChain, Hugging Face Embeddings, and Streamlit. Upload PDF files, ask questions, and receive contextually accurate answers based on your documents.

Features it provides are:
--> Upload one or multiple PDFs
--> Automatic chunking and embedding using Sentence Transformers
--> Vector database using ChromaDB with persistence
--> Fast, context-aware answers using Hugging Face + LangChain
--> Built with modular, reusable Python code

This is a primitive project. Chunking and processing of documents that are uploaded may take time.

Project Structure:

|
├── main.py # Main Streamlit app
├── src/
│ ├── pdf_processor.py # PDF & image chunking logic
│ ├── embeddings_and_retriever.py # Vectorstore logic (create/load)
│ ├── get_prompt.py # Prompt template
│ ├── llm_qa.py # Chat model wrapper
│ └── **init**.py
├── chroma_db/ # Vectorstore (auto-generated)
├── data/ # Uploaded PDFs
├── requirements.txt
└── README.md

To-Do / Future Enhancements:
--> Add caching to avoid re-embedding existing files
--> Support for non-PDF formats (CSV, DOCX)
--> Highlight answer spans in source document
--> Deploy on Hugging Face Spaces / GitHub Pages

MIT License. Use freely, but give credit if reused
