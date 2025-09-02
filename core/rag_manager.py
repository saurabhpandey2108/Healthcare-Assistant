import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Corrected the import variable name from OPEN_API_KEY to OPENAI_API_KEY
from backend.config import OPENAI_API_KEY


class RAGManager:
    def __init__(self, index_path="faiss_index"):
        self.index_path = index_path
        
        # Try to initialize embeddings with error handling
        try:
            self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI embeddings: {e}")
            # For now, we'll continue without embeddings for testing
            self.embeddings = None
            self.vector_store = None
            return

        if os.path.exists(self.index_path) and self.embeddings:
            try:
                self.vector_store = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
                print(f"✅ Loaded existing knowledge base from {self.index_path}")
            except Exception as e:
                print(f"Warning: Could not load existing index: {e}")
                self.vector_store = None
        else:
            self.vector_store = None
            print("📚 Knowledge base not found - will be created when documents are added")

    def add_document(self, file_path):
        """Add a document to the knowledge base"""
        if not self.embeddings:
            print("❌ Cannot add document: embeddings not initialized")
            return False
            
        try:
            print(f"📄 Processing document: {file_path}")
            
            # Corrected typo from startswitch to startswith
            if file_path.startswith("http"):
                loader = WebBaseLoader(file_path)
            elif file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path)

            documents = loader.load()
            print(f"📚 Loaded {len(documents)} document sections")
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = text_splitter.split_documents(documents)
            print(f"✂️ Split into {len(docs)} chunks")

            if self.vector_store:
                self.vector_store.add_documents(docs)
            else:
                self.vector_store = FAISS.from_documents(docs, self.embeddings)

            self.vector_store.save_local(self.index_path)
            print(f"💾 Saved to knowledge base: {self.index_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def get_retriever(self):
        if self.vector_store:
            return self.vector_store.as_retriever()
        return None


# Initialize the RAG manager
rag_manager = RAGManager()