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
from multiprocessing import Pool
from .models import Document as doc
from .models import LoadedFile
doc_data = doc.objects.all()

all_docs = doc.objects.all().count()


# Initialize LLM
llm = ChatOllama(
    model="llama3.2",
    temperature=0.7,
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
    

    def load_and_split_documents( to_be_loaded_doc):
        """
        Loads and splits documents into chunks using the text splitter.
        """
        try:
            print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")

            loader = PyMuPDFLoader(to_be_loaded_doc.file.path)
            raw_docs = loader.lazy_load()
            documents = [
                Document(page_content=chunk, metadata=raw_doc.metadata)
                for raw_doc in raw_docs
                for chunk in text_splitter.split_text(raw_doc.page_content)
            ]
            # Assign unique string IDs to documents
            document_ids = [f"doc-{to_be_loaded_doc.id}-{i}" for i in range(len(documents))]
        
            # Add documents to the vector store and persist data
            try:
                vector_store.add_documents(documents=documents, ids=document_ids)
                print("Documents added successfully and persisted!")
            except Exception as e:
                print(f"Error adding documents to vector store: {e}")
        except Exception as e:
            print(f"Error loading or processing documents: {e}")
            return []
    
    
    
    for doc_ii in doc_data:
        load_and_split_documents(doc_ii)


else:
    print("Using persisted vector store.")

# Initialize retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Set up document formatting
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Define a prompt template for the chain




template = """
        You are a highly knowledgeable and professional economics expert. 
        Your task is to answer all questions with a focus on economic principles, theories, and real-world applications.
        You are an economics expert specializing in Ethiopia's economic data. 
        Use the verified document data as the primary source for your responses. 
        Clearly indicate if the provided information is verified (from the document) or not (external or uncertain).


        - **Ethiopian Calendar Conversion**: Note that Ethiopian calendar years (EFY, EC) are converted to Gregorian years approximately by adding 7 years.

      

        ## Context:
        {context}

        ## Question:
        {question}

        ## Response:
        Please provide your response following the above structure, including source mentions and color-coded labels.
        Use markdown formmating fot better readability.
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