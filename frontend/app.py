import streamlit as st
import requests
import uuid
import os
from datetime import datetime

# --- Configuration ---
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="SafeSpace AI", layout="wide", initial_sidebar_state="expanded")

# --- UI Styling ---
st.markdown("""
    <style>
    /* Reduce top padding for the main content area */
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    /* Style for buttons in the sidebar and forms */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
    }
    /* Style for chat messages */
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    /* Style for the right-side knowledge base container */
    .knowledge-base-container {
        background-color: #f0f2f6; /* A light grey background */
        padding: 1rem;
        border-radius: 10px;
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)


# --- Session State Initialization for Multi-Chat ---
if 'all_chats' not in st.session_state:
    st.session_state.all_chats = {}
if 'active_chat_id' not in st.session_state:
    new_chat_id = str(uuid.uuid4())
    st.session_state.active_chat_id = new_chat_id
    st.session_state.all_chats[new_chat_id] = {
        "title": "New Chat",
        "history": [],
        "indexed_items": set()
    }

# --- Helper functions for chat management ---
def start_new_chat():
    new_chat_id = str(uuid.uuid4())
    st.session_state.active_chat_id = new_chat_id
    st.session_state.all_chats[new_chat_id] = {
        "title": "New Chat",
        "history": [],
        "indexed_items": set()
    }
    st.rerun()

def switch_chat(chat_id):
    st.session_state.active_chat_id = chat_id
    st.rerun()

# --- LEFT SIDEBAR for Chat History ---
with st.sidebar:
    # Signature in the sidebar
    # st.markdown("---")
    st.markdown("Crafted with ❤️ by SAURABH PANDEY")
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
    st.markdown("---")
    st.subheader("Recent")
    # Display chats in reverse chronological order
    for chat_id, chat_data in reversed(list(st.session_state.all_chats.items())):
        if st.button(chat_data['title'], key=f"chat_{chat_id}", use_container_width=True):
            switch_chat(chat_id)
    
     # --- NEW: How to Use Section ---
    st.markdown("---")
    with st.expander("ℹ️ How to Use This Agent"):
        st.markdown("""
        **1. Start a Conversation**
        - Use the text box at the bottom of the chat to ask anything. Your first message will become the title of the chat.

        **2. Manage Chats**
        - Click **"+ New Chat"** to start a fresh conversation.
        - Your past conversations are saved under **"Recent"**. Click any of them to continue where you left off.

        **3. Use the Knowledge Base (Right Panel)**
        - **Upload PDFs**: Add your own medical books or documents. The AI will use these to answer questions.
        - **Add Websites**: Provide a URL, and the AI will scrape its content to use as context.
        - *Note: The knowledge base is specific to each chat.*

        **4. Interact with Responses**
        - **Search Web**: If an answer isn't detailed enough, click this to get more information from the internet.
        - **Regenerate**: Not satisfied with a response? Click this to get an alternative answer.
        """)

# --- MAIN PAGE LAYOUT ---
col1, col2 = st.columns([3, 1],gap="medium") # Main chat area is twice as wide as the knowledge base area

# --- CENTER COLUMN: Main Chat Interface ---
with col1:
    st.title("🧠 SafeSpace AI")
    st.markdown(f"**Conversation:** {st.session_state.all_chats[st.session_state.active_chat_id]['title']}")

    # Create a container that will hold the chat history
    # This allows the chat input to be placed outside and stick to the bottom
    chat_container = st.container()

    with chat_container:
        active_chat_history = st.session_state.all_chats[st.session_state.active_chat_id]["history"]
        for i, msg in enumerate(active_chat_history):
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if i == len(active_chat_history) - 1 and msg["role"] == "assistant":
                    last_user_message = next((m["content"] for m in reversed(active_chat_history) if m["role"] == "user"), None)
                    if last_user_message:
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("🌐 Search Web", key=f"web_search_{i}_{st.session_state.active_chat_id}"):
                                active_chat_history.append({"role": "user", "content": f"Please search the web for more information about: {last_user_message}"})
                                st.rerun()
                        with btn_col2:
                            if st.button("🔄 Regenerate", key=f"regen_{i}_{st.session_state.active_chat_id}"):
                                active_chat_history.pop()
                                active_chat_history.append({"role": "user", "content": f"Please provide an alternative response for: {last_user_message}"})
                                st.rerun()

    # Place the chat_input outside the container to pin it to the bottom
    user_input = st.chat_input("What's on your mind today?")
    if user_input:
        active_chat_history.append({"role": "user", "content": user_input})
        if st.session_state.all_chats[st.session_state.active_chat_id]["title"] == "New Chat":
            st.session_state.all_chats[st.session_state.active_chat_id]["title"] = user_input[:30] + "..."
        st.rerun()

    # Generate AI response
    if active_chat_history and active_chat_history[-1]["role"] == "user":
        last_user_message = active_chat_history[-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(f"{BACKEND_URL}/ask", json={"message": last_user_message, "session_id": st.session_state.active_chat_id})
                if response.status_code == 200:
                    ai_response = response.json()
                    response_text = f'{ai_response.get("response", "Sorry, I encountered an error.")} \n\n*Tool Called: `{ai_response.get("tool_called", "None")}`*'
                    active_chat_history.append({"role": "assistant", "content": response_text})
                    st.rerun()
                else:
                    st.error("Error connecting to the backend. Please ensure it's running.")

# --- RIGHT COLUMN: Knowledge Base Management ---
with col2:
    st.markdown('<div class="knowledge-base-container">', unsafe_allow_html=True)
    st.header("📚 Knowledge Base")
    st.info("Add context for your active chat.")

    # PDF UPLOAD FORM
    with st.form("pdf_upload_form", clear_on_submit=True):
        st.subheader("Upload Medical PDFs")
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
        pdf_submitted = st.form_submit_button("Add PDFs to Knowledge Base")
        if pdf_submitted and uploaded_files:
            active_chat = st.session_state.all_chats[st.session_state.active_chat_id]
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in active_chat['indexed_items']:
                    file_path = os.path.join("data", uploaded_file.name)
                    with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    with st.spinner(f"Indexing {uploaded_file.name}..."):
                        response = requests.post(f"{BACKEND_URL}/upload", json={"file_path": file_path})
                        if response.status_code == 200:
                            st.success(f"✅ {uploaded_file.name} added.")
                            active_chat['indexed_items'].add(uploaded_file.name)
                        else: st.error(f"❌ Failed to add {uploaded_file.name}.")
                else: st.toast(f"'{uploaded_file.name}' is already indexed.")

    # WEBSITE URL UPLOAD FORM
    with st.form("website_upload_form", clear_on_submit=True):
        st.subheader("Add a Website URL")
        website_url = st.text_input("Enter a website URL", label_visibility="collapsed")
        website_submitted = st.form_submit_button("Add Website to Knowledge Base")
        if website_submitted and website_url:
            active_chat = st.session_state.all_chats[st.session_state.active_chat_id]
            if website_url not in active_chat['indexed_items']:
                with st.spinner("Indexing website..."):
                    response = requests.post(f"{BACKEND_URL}/upload", json={"file_path": website_url})
                    if response.status_code == 200:
                        st.success("✅ Website added.")
                        active_chat['indexed_items'].add(website_url)
                    else: st.error("❌ Failed to add website.")
            else: st.toast("This website is already indexed.")

    # Display Indexed Items
    active_chat_data = st.session_state.all_chats.get(st.session_state.active_chat_id, {})
    if active_chat_data.get("indexed_items"):
        st.subheader("Indexed Knowledge for this Chat")
        for item in active_chat_data["indexed_items"]:
            st.markdown(f"📄 {item}" if item.endswith('.pdf') else f"🔗 {item}")

    st.markdown('</div>', unsafe_allow_html=True)