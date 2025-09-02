"""
Knowledge Base Component for SAFESPACE AI AGENT Streamlit Interface

This module provides the knowledge base management panel for document uploads and RAG.
"""

import streamlit as st
import requests
import os
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Any
import urllib.parse

if TYPE_CHECKING:
    from frontend.components.session_manager import SessionManager

from frontend.utils.config import (
    ENDPOINTS, SUPPORTED_DOC_FORMATS, MAX_DOC_SIZE_MB,
    DOCS_UPLOAD_DIR, ERROR_MESSAGES
)
from frontend.utils.styling import create_alert


def render_knowledge_base(session_manager: 'SessionManager'):
    """Render the complete knowledge base management panel"""
    
    st.markdown('<div class="knowledge-base-container">', unsafe_allow_html=True)
    
    st.header("📚 Knowledge Base")
    st.markdown("Enhance conversations with your own documents and sources")
    
    # Tabs for different knowledge sources
    tab1, tab2, tab3 = st.tabs(["📄 Documents", "🌐 Websites", "📊 Manage"])
    
    with tab1:
        render_document_upload_panel(session_manager)
    
    with tab2:
        render_website_upload_panel(session_manager)
    
    with tab3:
        render_knowledge_management_panel(session_manager)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_document_upload_panel(session_manager: 'SessionManager'):
    """Render document upload panel"""
    
    st.subheader("📄 Upload Documents")
    st.markdown("Add PDFs, text files, and other documents to enhance AI responses")
    
    # Document upload
    uploaded_docs = st.file_uploader(
        "Choose document files",
        type=SUPPORTED_DOC_FORMATS,
        accept_multiple_files=True,
        key="doc_uploader",
        help=f"Supported formats: {', '.join(SUPPORTED_DOC_FORMATS)}"
    )
    
    if uploaded_docs:
        for doc in uploaded_docs:
            process_uploaded_document(doc, session_manager)
    
    # Upload options
    with st.expander("⚙️ Document Processing Options"):
        chunk_size = st.slider("Text Chunk Size", 500, 2000, 1000, 100)
        overlap = st.slider("Chunk Overlap", 50, 300, 100, 50)
        extract_metadata = st.checkbox("Extract Metadata", value=True)
        auto_summarize = st.checkbox("Auto-generate Summary", value=False)
    
    # Bulk upload
    st.markdown("**Bulk Upload:**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Upload from Folder", key="bulk_upload"):
            st.info("Folder upload feature coming soon!")
    
    with col2:
        if st.button("☁️ Import from Cloud", key="cloud_import"):
            st.info("Cloud import feature coming soon!")
    
    # Document templates
    render_document_templates()


def process_uploaded_document(uploaded_file, session_manager: 'SessionManager'):
    """Process and index uploaded document"""
    
    # Check file size
    if uploaded_file.size > MAX_DOC_SIZE_MB * 1024 * 1024:
        st.error(f"File size exceeds {MAX_DOC_SIZE_MB}MB limit")
        return
    
    # Check if already indexed
    indexed_items = session_manager.get_indexed_items()
    if uploaded_file.name in indexed_items:
        st.warning(f"📄 {uploaded_file.name} is already indexed in this chat")
        return
    
    try:
        # Save to uploads directory
        file_path = DOCS_UPLOAD_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Index the document
        with st.spinner(f"📚 Indexing {uploaded_file.name}..."):
            response = requests.post(
                ENDPOINTS['upload_document'],
                json={"file_path": str(file_path)},
                timeout=60
            )
            
            if response.status_code == 200:
                # Add to session's indexed items
                session_manager.add_indexed_item(uploaded_file.name)
                
                # Add to chat history
                session_manager.add_message(
                    "system",
                    f"📄 **Document Added:** {uploaded_file.name} has been indexed and added to the knowledge base.",
                    {
                        "type": "document_indexed",
                        "filename": uploaded_file.name,
                        "file_path": str(file_path)
                    }
                )
                
                st.success(f"✅ {uploaded_file.name} indexed successfully!")
                st.rerun()
                
            else:
                st.error(f"❌ Failed to index {uploaded_file.name}")
                # Clean up file if indexing failed
                if file_path.exists():
                    file_path.unlink()
                    
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")


def render_document_templates():
    """Render document template section"""
    
    with st.expander("📋 Document Templates"):
        st.markdown("**Sample documents you can upload:**")
        
        templates = [
            {
                "name": "Mental Health Handbook",
                "description": "Comprehensive mental health resources and coping strategies",
                "type": "PDF"
            },
            {
                "name": "Therapy Session Notes",
                "description": "Template for organizing therapy session insights",
                "type": "Text"
            },
            {
                "name": "Medication Guide",
                "description": "Information about psychiatric medications",
                "type": "PDF"
            },
            {
                "name": "Crisis Intervention Plan",
                "description": "Step-by-step crisis response procedures",
                "type": "Text"
            }
        ]
        
        for template in templates:
            st.markdown(f"- **{template['name']}** ({template['type']}): {template['description']}")


def render_website_upload_panel(session_manager: 'SessionManager'):
    """Render website content upload panel"""
    
    st.subheader("🌐 Add Website Content")
    st.markdown("Extract and index content from websites for enhanced knowledge")
    
    # URL input form
    with st.form("website_form", clear_on_submit=True):
        url = st.text_input(
            "Website URL",
            placeholder="https://example.com/article",
            help="Enter a valid URL to extract and index its content"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            extract_full_site = st.checkbox("Extract Full Site", value=False)
        with col2:
            follow_links = st.checkbox("Follow Internal Links", value=False)
        
        submitted = st.form_submit_button("🔗 Add Website")
        
        if submitted and url:
            process_website_url(url, extract_full_site, follow_links, session_manager)
    
    # Website processing options
    with st.expander("⚙️ Website Processing Options"):
        st.markdown("**Content Extraction:**")
        extract_text = st.checkbox("Extract Text Content", value=True)
        extract_images = st.checkbox("Extract Image Descriptions", value=False)
        extract_metadata = st.checkbox("Extract Page Metadata", value=True)
        
        st.markdown("**Filtering:**")
        min_content_length = st.slider("Minimum Content Length", 100, 1000, 300)
        exclude_nav = st.checkbox("Exclude Navigation Content", value=True)
        exclude_ads = st.checkbox("Exclude Advertisement Content", value=True)
    
    # Common mental health websites
    render_suggested_websites(session_manager)


def process_website_url(url: str, extract_full_site: bool, follow_links: bool, session_manager: 'SessionManager'):
    """Process and index website content"""
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        st.error("Please enter a valid URL starting with http:// or https://")
        return
    
    # Check if already indexed
    indexed_items = session_manager.get_indexed_items()
    if url in indexed_items:
        st.warning(f"🌐 {url} is already indexed in this chat")
        return
    
    try:
        with st.spinner(f"🌐 Processing website: {url}"):
            # Make request to index website
            response = requests.post(
                ENDPOINTS['upload_document'],
                json={
                    "file_path": url,
                    "file_type": "web",
                    "extract_full_site": extract_full_site,
                    "follow_links": follow_links
                },
                timeout=120  # Website processing can take longer
            )
            
            if response.status_code == 200:
                # Add to session's indexed items
                session_manager.add_indexed_item(url)
                
                # Get domain name for display
                domain = urllib.parse.urlparse(url).netloc
                
                # Add to chat history
                session_manager.add_message(
                    "system",
                    f"🌐 **Website Added:** Content from {domain} has been indexed and added to the knowledge base.",
                    {
                        "type": "website_indexed",
                        "url": url,
                        "domain": domain
                    }
                )
                
                st.success(f"✅ Website content from {domain} indexed successfully!")
                st.rerun()
                
            else:
                st.error(f"❌ Failed to index website content from {url}")
                
    except Exception as e:
        st.error(f"Error processing website: {str(e)}")


def render_suggested_websites(session_manager: 'SessionManager'):
    """Render suggested mental health websites"""
    
    with st.expander("🌟 Suggested Mental Health Resources"):
        st.markdown("**Trusted mental health websites to add to your knowledge base:**")
        
        websites = [
            {
                "name": "National Institute of Mental Health (NIMH)",
                "url": "https://www.nimh.nih.gov/health/topics",
                "description": "Comprehensive mental health information and research"
            },
            {
                "name": "Mental Health America",
                "url": "https://www.mhanational.org/conditions",
                "description": "Mental health conditions and treatment information"
            },
            {
                "name": "American Psychological Association",
                "url": "https://www.apa.org/topics/mental-health",
                "description": "Psychology and mental health resources"
            },
            {
                "name": "Crisis Text Line Resources",
                "url": "https://www.crisistextline.org/topics",
                "description": "Crisis support and mental health topics"
            }
        ]
        
        for website in websites:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{website['name']}**")
                st.markdown(f"{website['description']}")
                st.markdown(f"`{website['url']}`")
            
            with col2:
                if st.button(f"Add", key=f"add_{website['name']}"):
                    process_website_url(website['url'], False, False, session_manager)


def render_knowledge_management_panel(session_manager: 'SessionManager'):
    """Render knowledge base management panel"""
    
    st.subheader("📊 Knowledge Base Management")
    
    # Check for existing documents in the uploads/documents folder
    sync_existing_documents(session_manager)
    
    # Current session knowledge
    indexed_items = session_manager.get_indexed_items()
    
    if indexed_items:
        st.markdown(f"**Knowledge Items in Current Chat:** {len(indexed_items)}")
        
        # Search through knowledge
        search_query = st.text_input(
            "🔍 Search Knowledge Base",
            placeholder="Enter keywords to search through indexed content...",
            key="kb_search"
        )
        
        if search_query:
            search_knowledge_base(search_query, session_manager)
        
        st.markdown("---")
        
        # List indexed items
        st.markdown("**Indexed Content:**")
        
        for item in indexed_items:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Determine item type and icon
                if item.startswith(('http://', 'https://')):
                    icon = "🌐"
                    display_name = urllib.parse.urlparse(item).netloc
                elif item.endswith('.pdf'):
                    icon = "📄"
                    display_name = item
                else:
                    icon = "📝"
                    display_name = item
                
                st.markdown(f"{icon} {display_name}")
            
            with col2:
                if st.button("ℹ️", key=f"info_{item}", help="View details"):
                    show_item_details(item, session_manager)
            
            with col3:
                if st.button("🗑️", key=f"remove_{item}", help="Remove from knowledge base"):
                    remove_from_knowledge_base(item, session_manager)
        
    else:
        st.info("No knowledge items in current chat. Upload documents or add websites to get started!")
    
    # Knowledge base statistics
    render_knowledge_statistics(session_manager)
    
    # Export knowledge base
    st.markdown("---")
    
    # Refresh and Export buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Knowledge Base", use_container_width=True, help="Re-scan for documents and sync with RAG system"):
            # Clear current session items and re-sync
            active_chat_id = st.session_state.active_chat_id
            st.session_state.all_chats[active_chat_id]["indexed_items"] = set()
            sync_existing_documents(session_manager)
            st.success("Knowledge base refreshed!")
            st.rerun()
    
    with col2:
        if st.button("📤 Export Knowledge Base", use_container_width=True):
            export_knowledge_base(session_manager)


def search_knowledge_base(query: str, session_manager: 'SessionManager'):
    """Search through the knowledge base"""
    
    try:
        with st.spinner("🔍 Searching knowledge base..."):
            # Note: This would require implementing search in the backend
            # For now, we'll add the search query to chat
            session_manager.add_message(
                "user",
                f"Please search the knowledge base for: {query}",
                {"type": "knowledge_search", "query": query}
            )
            
            st.success("Search query added to conversation!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Error searching knowledge base: {str(e)}")


def show_item_details(item: str, session_manager: 'SessionManager'):
    """Show details about a knowledge base item"""
    
    # Store selected item for modal display
    st.session_state.selected_kb_item = item
    st.session_state.show_kb_details = True


def remove_from_knowledge_base(item: str, session_manager: 'SessionManager'):
    """Remove item from knowledge base"""
    
    # Show confirmation dialog
    if f"confirm_delete_{item}" not in st.session_state:
        st.session_state[f"confirm_delete_{item}"] = False
    
    if not st.session_state[f"confirm_delete_{item}"]:
        st.session_state[f"confirm_delete_{item}"] = True
        st.warning(f"Are you sure you want to remove '{item}' from the knowledge base? This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Remove", key=f"confirm_yes_{item}", type="primary"):
                perform_removal(item, session_manager)
        with col2:
            if st.button("Cancel", key=f"confirm_no_{item}"):
                st.session_state[f"confirm_delete_{item}"] = False
                st.rerun()
        
        st.stop()


def perform_removal(item: str, session_manager: 'SessionManager'):
    """Perform the actual removal of the item"""
    
    try:
        # Remove from session's indexed items using the session manager method
        session_manager.remove_indexed_item(item)
        
        # Try to remove from actual RAG system
        removal_success = remove_document_from_rag(item)
        
        if removal_success:
            # Add removal message to chat
            session_manager.add_message(
                "system",
                f"🗑️ **Removed from Knowledge Base:** {item} has been successfully removed from both the chat session and the document storage.",
                {"type": "knowledge_removed", "item": item}
            )
            
            st.success(f"✅ Successfully removed {item} from knowledge base")
        else:
            # Add partial removal message
            session_manager.add_message(
                "system",
                f"⚠️ **Partially Removed:** {item} was removed from the chat session, but there may have been issues removing it from the document storage.",
                {"type": "knowledge_partially_removed", "item": item}
            )
            
            st.warning(f"⚠️ Partially removed {item} - check logs for details")
        
        # Reset confirmation state
        st.session_state[f"confirm_delete_{item}"] = False
        st.rerun()
        
    except Exception as e:
        st.error(f"Error removing item: {str(e)}")
        st.session_state[f"confirm_delete_{item}"] = False


def render_knowledge_statistics(session_manager: 'SessionManager'):
    """Render knowledge base statistics"""
    
    indexed_items = session_manager.get_indexed_items()
    
    with st.expander("📈 Knowledge Base Statistics", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_items = len(indexed_items)
            st.metric("Total Items", total_items)
        
        with col2:
            # Count different types
            websites = sum(1 for item in indexed_items if item.startswith(('http://', 'https://')))
            st.metric("Websites", websites)
        
        with col3:
            documents = len(indexed_items) - websites
            st.metric("Documents", documents)
        
        # Storage information
        if documents > 0:
            st.markdown("**Document Storage:**")
            total_size = 0
            for item in indexed_items:
                if not item.startswith(('http://', 'https://')):
                    file_path = DOCS_UPLOAD_DIR / item
                    if file_path.exists():
                        total_size += file_path.stat().st_size
            
            if total_size > 0:
                st.markdown(f"- Total Size: {total_size / (1024*1024):.1f} MB")
                st.markdown(f"- Average per Document: {(total_size / documents) / (1024*1024):.1f} MB")
        
        # RAG System Status
        st.markdown("**RAG System Status:**")
        from core.rag_manager import rag_manager
        
        if rag_manager.vector_store:
            # Try to get document count from vector store
            try:
                # This is an approximation - FAISS doesn't directly give document count
                st.markdown("✅ Vector store is active and ready")
                st.markdown(f"📋 Knowledge base index exists at: `{rag_manager.index_path}`")
            except Exception as e:
                st.markdown(f"⚠️ Vector store status unclear: {str(e)}")
        else:
            st.markdown("❌ Vector store not initialized")
        
        # Most recent additions
        if indexed_items:
            st.markdown("**Recently Added:**")
            # Show last 3 items (this is simplified - in reality you'd track timestamps)
            recent_items = list(indexed_items)[-3:]
            for item in recent_items:
                icon = "🌐" if item.startswith(('http://', 'https://')) else "📄"
                display_name = item[:30] + "..." if len(item) > 30 else item
                st.markdown(f"- {icon} {display_name}")


def export_knowledge_base(session_manager: 'SessionManager'):
    """Export knowledge base information"""
    
    indexed_items = session_manager.get_indexed_items()
    active_chat = session_manager.get_active_chat()
    
    if not indexed_items:
        st.warning("No knowledge items to export")
        return
    
    # Create export data
    export_data = {
        "chat_title": active_chat.get('title', 'Unknown'),
        "export_timestamp": str(datetime.now()),
        "total_items": len(indexed_items),
        "indexed_items": list(indexed_items)
    }
    
    # Convert to JSON
    import json
    export_json = json.dumps(export_data, indent=2)
    
    # Offer download
    st.download_button(
        label="💾 Download Knowledge Base Export",
        data=export_json,
        file_name=f"knowledge_base_export_{active_chat.get('title', 'chat').replace(' ', '_')}.json",
        mime="application/json"
    )


# Handle knowledge base item details modal
if st.session_state.get('show_kb_details', False):
    item = st.session_state.get('selected_kb_item', '')
    
    with st.modal(f"Knowledge Base Item Details"):
        st.markdown(f"### {item}")
        
        if item.startswith(('http://', 'https://')):
            st.markdown(f"**Type:** Website")
            st.markdown(f"**URL:** {item}")
            st.markdown(f"**Domain:** {urllib.parse.urlparse(item).netloc}")
        else:
            st.markdown(f"**Type:** Document")
            st.markdown(f"**Filename:** {item}")
            
            # Try to show file info if it exists
            file_path = DOCS_UPLOAD_DIR / item
            if file_path.exists():
                stat = file_path.stat()
                st.markdown(f"**Size:** {stat.st_size / 1024:.1f} KB")
                st.markdown(f"**Modified:** {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')}")
        
        if st.button("Close"):
            st.session_state.show_kb_details = False
            st.rerun()


def sync_existing_documents(session_manager: 'SessionManager'):
    """Sync existing documents from uploads/documents with the session knowledge base"""
    
    # Check if FAISS index exists and has documents
    from core.rag_manager import rag_manager
    
    if rag_manager.vector_store:
        # Get existing documents from uploads/documents
        existing_docs = []
        if DOCS_UPLOAD_DIR.exists():
            for file_path in DOCS_UPLOAD_DIR.glob("*.pdf"):
                existing_docs.append(file_path.name)
            for file_path in DOCS_UPLOAD_DIR.glob("*.txt"):
                existing_docs.append(file_path.name)
            for file_path in DOCS_UPLOAD_DIR.glob("*.docx"):
                existing_docs.append(file_path.name)
            for file_path in DOCS_UPLOAD_DIR.glob("*.md"):
                existing_docs.append(file_path.name)
        
        # Add existing documents to the session if not already present
        current_indexed = session_manager.get_indexed_items()
        new_docs_found = []
        
        for doc in existing_docs:
            if doc not in current_indexed:
                session_manager.add_indexed_item(doc)
                new_docs_found.append(doc)
        
        # Show notification if new documents were found
        if new_docs_found and len(new_docs_found) > 0:
            with st.info(f"Found {len(new_docs_found)} existing documents in knowledge base"):
                for doc in new_docs_found:
                    st.write(f"- {doc}")


def remove_document_from_rag(item: str) -> bool:
    """Remove document from the actual RAG vector store"""
    
    try:
        # This is a complex operation that would require rebuilding the vector store
        # For now, we'll just remove from session tracking
        # In a production system, you'd need to:
        # 1. Remove the document chunks from FAISS
        # 2. Delete the physical file if needed
        # 3. Rebuild the index
        
        # Delete physical file if it exists
        if not item.startswith(('http://', 'https://')):
            file_path = DOCS_UPLOAD_DIR / item
            if file_path.exists():
                file_path.unlink()
                print(f"Deleted physical file: {file_path}")
                return True
        
        return True
        
    except Exception as e:
        print(f"Error removing document from RAG: {e}")
        return False