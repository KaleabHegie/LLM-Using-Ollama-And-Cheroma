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
from functools import partial

from .models import Document as doc
from .models import LoadedFile

# Initialize constants and models
doc_data = doc.objects.filter().first()
all_docs = doc.objects.all().count()
persist_directory = "./chroma_db"

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

# Initialize Chroma vector store
vector_store = Chroma(
    collection_name="foo",
    embedding_function=embeddings,
    persist_directory=persist_directory
)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

# Get the loaded file object
loaded_file = LoadedFile.objects.filter().first()


async def doc_initialization():
    """
    Initializes the document processing and persists to vector store if required.
    """
    print('-------------------------')
    try:
        # Check if vector store needs updating
        if (
            not os.path.exists(persist_directory) or
            vector_store._collection.count() == 0 or  # Replace with public API if possible
            loaded_file.number != all_docs
        ):
            print("Loading and processing documents...")
            loaded_file.number = all_docs
            loaded_file.save()

            async def process_documents(documents):
                """Processes and adds documents to the vector store."""
                try:
                    # Process documents asynchronously
                    split_docs = await asyncio.gather(*[
                        asyncio.to_thread(load_and_split_documents, doc, text_splitter)
                        for doc in documents
                    ])

                    # Flatten document chunks
                    flattened_docs = [doc for sublist in split_docs for doc in sublist]
                    document_ids = [f"doc-{i}" for i in range(len(flattened_docs))]

                    # Add documents to the vector store
                    vector_store.add_documents(flattened_docs, ids=document_ids)
                    vector_store.persist()
                    print(f"Successfully processed {len(flattened_docs)} document chunks")
                except Exception as e:
                    print(f"Error processing documents: {e}")
                    raise

            def load_and_split_documents(doc, text_splitter):
                """Splits document into smaller chunks."""
                try:
                    chunks = text_splitter.split_text(doc.page_content)
                    return [Document(page_content=chunk, metadata=doc.metadata) for chunk in chunks]
                except Exception as e:
                    print(f"Error splitting document: {e}")
                    return []

            # Load documents from file
            loader = PyMuPDFLoader(doc_data.file.path)  # Ensure `doc_data.file` is a valid file path
            raw_docs = loader.lazy_load()
            await process_documents(raw_docs)
        else:
            print("Using persisted vector store.")
    except Exception as e:
        print(f"Error in doc_initialization: {e}")


async def main():
    """
    Main entry point for document initialization.
    """
    print('here ------++--')
    await doc_initialization()


if __name__ == "__main__":
    print('here ------++--')
    asyncio.run(main())

# Initialize retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Set up document formatting
def format_docs(docs):
    """Formats retrieved documents into a readable string."""
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
