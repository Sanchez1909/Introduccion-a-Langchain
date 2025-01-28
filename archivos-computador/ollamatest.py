from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3.2:latest")

print(model.invoke("Que es wikipedia?"))