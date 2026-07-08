from rag.retriever import retrieve

query = "startup vs MNC career growth"

result = retrieve(query)

print(result)