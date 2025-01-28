from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
loader = WebBaseLoader("https://es.wikipedia.org/wiki/Leo_Atrox")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)


local_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)
"""question = "What are the approaches to Task Decomposition?"
docs = vectorstore.similarity_search(question)
print(len(docs))
print(docs[0])
print("___________________________________________________________________________________________________________________")
"""
model = ChatOllama(
    model="llama3.2:latest",
)
"""
response_message = model.invoke(
    "Simulate a rap battle between Stephen Colbert and John Oliver"
)

print(response_message.content)
print("_____________________________________________________________________________________________________________________")
prompt = ChatPromptTemplate.from_template(
    "Summarize the main themes in these retrieved docs: {docs}"
)
"""
# Convert loaded documents into strings by concatenating their content
# and ignoring metadata
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


#chain = {"docs": format_docs} | prompt | model | StrOutputParser()

RAG_TEMPLATE = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

<context>
{context}
</context>

Answer the following question:

{question}"""

rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

chain = (
    RunnablePassthrough.assign(context=lambda input: format_docs(input["context"]))
    | rag_prompt
    | model
    | StrOutputParser()
)

question = "cual es la capacidad de procesamiento de la super computadora?"
while(question != "bye"):
    docs = vectorstore.similarity_search(question)
    result=chain.invoke({"context": docs, "question": question})
    print(result)
    question=input("You: ")