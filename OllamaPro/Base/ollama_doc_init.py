from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import asyncio

from .models import Document as doc
from .models import LoadedFile
doc_data = doc.objects.filter().first()

all_docs = doc.objects.all().count()


# Initialize LLM
llm = ChatOllama(
    model="llama3.2",
    temperature=0,
    stream=True,
)

# Initialize Embeddings
embeddings = OllamaEmbeddings(
    model="znbang/bge:large-en-v1.5-f16",
)

# Set persistence directory
persist_directory = "./chroma_db"

# Initialize Chroma vector store
vector_store = Chroma(
    collection_name="foo",
    embedding_function=embeddings,
    persist_directory=persist_directory  # Add persistence directory
)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Number of characters per chunk
    chunk_overlap=50,  # Overlap between chunks to maintain context
)


loaded_file = LoadedFile.objects.filter().first()
# Load and process documents if vector store is empty
if not os.path.exists(persist_directory) or vector_store._collection.count() == 0 or loaded_file.number != all_docs:
    print("Loading and processing documents...")

    loaded_file.number = all_docs
    loaded_file.save()


    # Load PDF using PyMuPDFLoader
    loader = PyMuPDFLoader(doc_data.file)

    def load_and_split_documents(loader, text_splitter):
        """
        Loads and splits documents into chunks using the text splitter.
        """
        try:
            raw_docs = loader.lazy_load()
            documents = [
                Document(page_content=chunk, metadata=raw_doc.metadata)
                for raw_doc in raw_docs
                for chunk in text_splitter.split_text(raw_doc.page_content)
            ]
            return documents
        except Exception as e:
            print(f"Error loading or processing documents: {e}")
            return []

    # Load and split documents
    documents = load_and_split_documents(loader, text_splitter)

    # Assign unique string IDs to documents
    document_ids = [f"doc-{i}" for i in range(len(documents))]

    # Add documents to the vector store and persist data
    try:
        vector_store.add_documents(documents=documents, ids=document_ids)
        vector_store.persist()
        print("Documents added successfully and persisted!")
    except Exception as e:
        print(f"Error adding documents to vector store: {e}")
else:
    print("Using persisted vector store.")

# Initialize retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Set up document formatting
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Define a prompt template for the chain
template = """
You are an assistant that formats responses in Markdown. 

## Context

{context}

## Question

**{question}**

## Response

Provide the response in Markdown format:
"""

prompt = PromptTemplate.from_template(template)

# Build the chain of operations
chain = (
    {
        'context': retriever | format_docs,
        'question': RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

