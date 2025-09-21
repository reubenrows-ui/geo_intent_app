import streamlit as st
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import Vertex AI and authentication
import vertexai
from google.oauth2 import service_account
from vertexai import agent_engines

# Load environment variables from .env file
load_dotenv()

RESOURCE_ID = os.getenv("RESOURCE_ID", "projects/593281338192/locations/us-central1/reasoningEngines/3028974214615924736")

def initialize_vertex_ai():
    """Initialize Vertex AI with service account credentials from secrets."""
    try:
        # Get credentials from Streamlit secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )

        # Initialize Vertex AI
        vertexai.init(
            project=st.secrets["gcp_service_account"]["project_id"],
            location="us-central1",
            credentials=credentials,
            staging_bucket=f"gs://{st.secrets['gcp_service_account']['project_id']}-staging"
        )

        return True
    except KeyError as e:
        st.error(f"Missing secret key: {e}. Please configure .streamlit/secrets.toml.")
        return False
    except Exception as e:
        st.error(f"Error initializing Vertex AI: {e}")
        return False

# Direct functions using agent_engines (same as remote.py)
async def create_new_session(resource_id: str, user_id: str) -> Optional[str]:
    """Create a new session and return session ID."""
    try:
        remote_app = agent_engines.get(resource_id)
        remote_session = await remote_app.async_create_session(user_id=user_id)

        if isinstance(remote_session, str):
            return remote_session
        elif isinstance(remote_session, dict):
            return remote_session.get('id')
        else:
            return None
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return None

async def get_sessions_list(resource_id: str, user_id: str) -> List[Dict[str, Any]]:
    """Get list of sessions for the user."""
    try:
        remote_app = agent_engines.get(resource_id)
        sessions = await remote_app.async_list_sessions(user_id=user_id)

        if isinstance(sessions, dict) and 'sessions' in sessions:
            return sessions['sessions']
        elif isinstance(sessions, list):
            return sessions
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")
        return []

async def get_session_details(resource_id: str, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Get session details including conversation history."""
    try:
        remote_app = agent_engines.get(resource_id)
        session = await remote_app.async_get_session(user_id=user_id, session_id=session_id)
        
        if isinstance(session, dict):
            return session
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching session details: {e}")
        return None

async def delete_session_by_id(resource_id: str, user_id: str, session_id: str) -> bool:
    """Delete a session by ID."""
    try:
        remote_app = agent_engines.get(resource_id)
        await remote_app.async_delete_session(user_id=user_id, session_id=session_id)
        return True
    except Exception as e:
        st.error(f"Error deleting session: {e}")
        return False

async def send_message_to_agent(resource_id: str, user_id: str, session_id: str, message: str) -> List[str]:
    """Send message to agent and return responses."""
    try:
        remote_app = agent_engines.get(resource_id)
        responses = []

        async for event in remote_app.async_stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            # Extract text content from the event
            if isinstance(event, dict):
                content = event.get('content', {})
                if isinstance(content, dict):
                    parts = content.get('parts', [])
                    for part in parts:
                        if isinstance(part, dict) and 'text' in part:
                            text = part['text']
                            if text and text.strip():
                                responses.append(text)

        return responses
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return []

def display_conversation_history(session_details: Dict[str, Any]):
    """Display conversation history from session events."""
    events = session_details.get('events', [])

    if not events:
        st.info("No conversation history yet. Start by sending a message!")
        return

    # Display events as conversation
    for event in events:
        if isinstance(event, dict):
            # Extract message content
            content = event.get('content', {})
            author = event.get('author', 'unknown')

            if isinstance(content, dict):
                parts = content.get('parts', [])
                role = content.get('role', author)

                # Extract text from parts
                text_content = ""
                for part in parts:
                    if isinstance(part, dict) and 'text' in part and part['text'] is not None:
                        text_content += part['text']

                if text_content.strip():
                    # Determine if it's user or assistant message
                    if role == 'user' or author == 'user':
                        with st.chat_message("user"):
                            st.write(text_content)
                    else:
                        with st.chat_message("assistant"):
                            st.write(text_content)

def main():
    st.set_page_config(
        page_title="Vertex AI Agent Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Vertex AI Agent Chat")
    st.markdown("Chat with your deployed Vertex AI Agent Engine")
    
    # Initialize Vertex AI
    if not initialize_vertex_ai():
        st.stop()
    
    # Check if resource ID is configured
    if RESOURCE_ID == "your-resource-id-here":
        st.error("⚠️ Please update RESOURCE_ID in app.py with your actual resource ID from remote.py --create")
        st.info("Run `python remote.py --create` to deploy your agent and get the resource ID.")
        st.stop()
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "sessions" not in st.session_state:
        st.session_state.sessions = []
    if "refresh_sessions" not in st.session_state:
        st.session_state.refresh_sessions = True
    if "user_name" not in st.session_state:
        st.session_state.user_name = "test_user"
    
    # Sidebar for session management
    with st.sidebar:
        user_id = st.text_input("User Name", value=st.session_state.user_name)
        st.session_state.user_name = user_id
        st.header("Session Management")
        
        # Refresh sessions button
        if st.button("🔄 Refresh Sessions"):
            st.session_state.refresh_sessions = True
        
        # Load sessions
        if st.session_state.refresh_sessions:
            st.session_state.sessions = asyncio.run(get_sessions_list(RESOURCE_ID, user_id))
            st.session_state.refresh_sessions = False
        
        # Create new session
        if st.button("➕ Create New Session"):
            new_session_id = asyncio.run(create_new_session(RESOURCE_ID, user_id))
            if new_session_id:
                st.success(f"Created new session: {new_session_id}")
                st.session_state.session_id = new_session_id
                st.session_state.refresh_sessions = True
                st.rerun()
        
        # Display sessions
        if st.session_state.sessions:
            st.subheader("Available Sessions")
            
            for i, session in enumerate(st.session_state.sessions):
                session_id = session.get('id', f'session_{i}')
                last_update = session.get('lastUpdateTime', 0)
                
                if last_update:
                    last_update_str = datetime.fromtimestamp(last_update).strftime('%m/%d %H:%M')
                else:
                    last_update_str = "Unknown"
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(f"📝 {session_id[:8]}... ({last_update_str})", key=f"select_{session_id}"):
                        st.session_state.session_id = session_id
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{session_id}", help="Delete session"):
                        if asyncio.run(delete_session_by_id(RESOURCE_ID, user_id, session_id)):
                            st.success("Session deleted!")
                            if st.session_state.session_id == session_id:
                                st.session_state.session_id = None
                            st.session_state.refresh_sessions = True
                            st.rerun()
        else:
            st.info("No sessions found. Create a new session to start chatting!")
    
    # Main chat interface
    if st.session_state.session_id:
        st.subheader(f"Chat Session: {st.session_state.session_id}")
        
        # Get and display session details
        session_details = asyncio.run(get_session_details(RESOURCE_ID, user_id, st.session_state.session_id))
        
        if session_details:
            # Display conversation history
            display_conversation_history(session_details)
            
            # Chat input
            st.markdown("---")
            user_message = st.chat_input("Type your message here...")
            
            if user_message:
                # Display user message
                with st.chat_message("user"):
                    st.write(user_message)
                
                # Send message and get response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        responses = asyncio.run(send_message_to_agent(RESOURCE_ID, user_id, st.session_state.session_id, user_message))
                    
                    if responses:
                        for response in responses:
                            st.write(response)
                    else:
                        st.error("No response received from the agent.")
                
                # Refresh to show updated conversation
                st.rerun()
        else:
            st.error("Could not load session details. Please try refreshing or creating a new session.")
    else:
        st.info("👈 Please select or create a session from the sidebar to start chatting.")
        
        # Display some helpful information
        st.markdown("""
        ### Getting Started
        
        1. **Create a Session**: Click "Create New Session" in the sidebar
        2. **Start Chatting**: Select a session and type your message
        3. **Manage Sessions**: View, select, or delete sessions from the sidebar
        
        ### Configuration
        
        - **User ID**: `{}`
        - **Resource ID**: `{}`
        
        Make sure your Vertex AI Agent Engine is deployed and the Resource ID is correct.
        """.format(user_id, RESOURCE_ID))

if __name__ == "__main__":
    main()
