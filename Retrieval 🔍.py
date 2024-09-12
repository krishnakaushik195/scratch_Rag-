# Question for retrieval
question = "What is Task Decomposition?"

# Retrieve relevant documents
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
docs = retriever.get_relevant_documents(question)

# Format retrieved docs for display
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

formatted_docs = format_docs(docs)
