import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

#### INDEXING ####

# Load Documents
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

# Split Documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# Embed Documents
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Set up Retriever
retriever = vectorstore.as_retriever()

#### RETRIEVAL ####

# Question for retrieval
question = "What is Task Decomposition?"

# Retrieve relevant documents
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
docs = retriever.get_relevant_documents(question)

# Format retrieved docs for display
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

formatted_docs = format_docs(docs)

#### GENERATION ####

# Define the prompt
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# LLM Setup
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# Create Chain for RAG
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Get the answer
response = rag_chain.invoke(question)
print(response)
