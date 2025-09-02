"""
Initialize RAG system with existing healthcare documents
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def initialize_healthcare_knowledge_base():
    """Initialize the RAG system with existing healthcare documents"""
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OpenAI API key not found. Please check your .env file.")
        return
    
    print("✅ OpenAI API key configured")
    
    # Import after ensuring API key is available
    from core.rag_manager import rag_manager
    
    documents_dir = Path("uploads/documents")
    
    if not documents_dir.exists():
        print("❌ Documents directory not found")
        return
    
    pdf_files = list(documents_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF documents found in uploads/documents/")
        return
    
    print(f"🔍 Found {len(pdf_files)} healthcare documents to index:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name} ({pdf_file.stat().st_size / 1024 / 1024:.1f}MB)")
    
    print("\n📚 Starting healthcare knowledge base initialization...")
    
    success_count = 0
    for pdf_file in pdf_files:
        print(f"\n📄 Processing: {pdf_file.name}")
        try:
            # Add document to RAG system
            if rag_manager.add_document(str(pdf_file)):
                success_count += 1
                print(f"✅ Successfully indexed: {pdf_file.name}")
            else:
                print(f"❌ Failed to index: {pdf_file.name}")
        except Exception as e:
            print(f"❌ Error indexing {pdf_file.name}: {str(e)}")
    
    # Verify the vector store was created
    if rag_manager.vector_store and success_count > 0:
        print(f"\n🎉 Healthcare knowledge base initialized successfully!")
        print(f"📊 Successfully indexed {success_count}/{len(pdf_files)} documents")
        print(f"💾 Vector store saved at: {rag_manager.index_path}")
        
        # Test retrieval
        test_retriever = rag_manager.get_retriever()
        if test_retriever:
            print("✅ Knowledge base retrieval system is working")
            
            # Test query
            try:
                test_docs = test_retriever.get_relevant_documents("diabetes")
                print(f"📋 Test query found {len(test_docs)} relevant documents for 'diabetes'")
            except Exception as e:
                print(f"⚠️ Test query failed: {e}")
        else:
            print("❌ Knowledge base retrieval system failed")
    else:
        print("❌ Failed to create knowledge base")


if __name__ == "__main__":
    print("🏥 SAFESPACE AI Agent - Healthcare Knowledge Base Initializer")
    print("=" * 60)
    initialize_healthcare_knowledge_base()