from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory="rag/chroma_db",
    embedding_function=embedding
)

retriever = db.as_retriever(search_kwargs={"k": 2})

def retrieve(query):
    docs = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)