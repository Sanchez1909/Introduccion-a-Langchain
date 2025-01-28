import asyncio
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Carga y divide los documentos
loader = WebBaseLoader("https://cgsait.udg.mx/es/cads#:~:text=LEO%20%C3%81TROX%2C%20superc%C3%B3mputo%20a%20tu,poder%20de%20procesamiento%20de%20datos.&text=150%20nodos%20c%C3%B3mputo%2C%20con%20un,c%C3%B3mputo%20con%20tecnolog%C3%ADa%20XEON%20PHI%20.")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Configuración de embeddings y vectorstore
local_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)

# Configuración del modelo de lenguaje y plantilla de RAG
model = ChatOllama(model="llama3.2:latest")

RAG_TEMPLATE = """
Eres un asiste de preguntas y respuestas. Usa la informacion recuperada para contestar las preguntas, relacionadas al CADS. Si no sabes la respuesta, solo di que no conoces la respuesta. Usa tres sentencias como maximo para dar una respuesta concisa.

<context>
{context}
</context>

Contesta la siguiente pregunta: 

{question}"""

rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

# Definir la función para formatear documentos
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
"""
chain = (
    RunnablePassthrough.assign(context=lambda input: format_docs(input["context"]))
    | rag_prompt
    | model
    | StrOutputParser()
)
"""
retriever = vectorstore.as_retriever()

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)
# Función asíncrona para manejar la entrada y respuesta por stream
"""async def chat_loop():
    question = "cual es la capacidad de procesamiento de la super computadora?"
    while question != "bye" and question != "adios":
        docs = vectorstore.similarity_search(question)
        async for chunk in chain.astream({"context": docs, "question": question}):
            print(chunk, end="", flush=True)
        question = input("\nYou: ").lower()

# Ejecutar la función asíncrona
asyncio.run(chat_loop())
"""

async def chat_loop():
    #global retriever
    question = "cual es la capacidad de procesamiento de la super computadora?"
    while question != "bye" and question != "adios":
        #retriever = vectorstore.as_retriever()
        async for chunk in chain.astream(question):
            print(chunk, end="", flush=True)
        question = input("\nYou: ").lower()

# Ejecutar la función asíncrona
asyncio.run(chat_loop())