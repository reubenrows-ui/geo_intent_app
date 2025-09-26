from unittest import result
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from google.oauth2 import service_account
from google.auth.transport import requests as google_requests
import requests
import json

def get_identity_token():
    # Load service account credentials from Streamlit secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/cloud-platform"],  # needed for Vertex AI
    )

    # Refresh to get a valid access token
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)

    return credentials.token

RESOURCE_ID = st.secrets["gcp"]['resource_id']

def create_new_session(user_id: str) -> Optional[str]:
    """Create a new session and return session ID using Vertex AI Agent Engine HTTP API."""
    try:
        url = f"https://{st.secrets['gcp']['location']}-aiplatform.googleapis.com/v1/{RESOURCE_ID}:query"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        }
        payload = {
            "class_method": "async_create_session",
            "input": {"user_id": user_id},
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        # Extract session ID from response (adjust if response structure differs)
        session_id = result.get("output", {}).get("id")
        return session_id
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return None

def get_sessions_list(user_id: str) -> List[Dict[str, Any]]:
    """Get list of sessions for the user."""
    try:
        url = f"https://{st.secrets['gcp']['location']}-aiplatform.googleapis.com/v1/{RESOURCE_ID}:query"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        }
        payload = {
            "class_method": "async_list_sessions",
            "input": {"user_id": user_id},
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        sessions = result.get("output", {}).get("sessions", [])
        return sessions
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")
        return []

def get_session_details(user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Get session details including conversation history."""
    try:
        url = f"https://{st.secrets['gcp']['location']}-aiplatform.googleapis.com/v1/{RESOURCE_ID}:query"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        }
        payload = {
            "class_method": "async_get_session",
            "input": {"user_id": user_id, "session_id": session_id},
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        session_details = result.get("output", {})

        if session_details:
            return session_details
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching session details: {e}")
        return None

def delete_session_by_id(resource_id: str, user_id: str, session_id: str) -> bool:
    """Delete a session by ID."""
    try:
        url = f"https://{st.secrets['gcp']['location']}-aiplatform.googleapis.com/v1/{resource_id}:query"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        }
        payload = {
            "class_method": "async_delete_session",
            "input": {"user_id": user_id, "session_id": session_id},
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error deleting session: {e}")
        return False

def send_message_to_agent(resource_id: str, user_id: str, session_id: str, message: str) -> List[str]:
    """Send message to agent and return responses."""
    try:
        responses = []
        url = f"https://{st.secrets['gcp']['location']}-aiplatform.googleapis.com/v1/{resource_id}:streamQuery"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        }
        payload = {
            "class_method": "async_stream_query",
            "input": {"user_id": user_id, "session_id": session_id, "message": message},
        }

        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(payload),
            stream=True
        )
        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode("utf-8"))
                    content = event.get('content', {})
                    if isinstance(content, dict):
                        parts = content.get('parts', [])
                        for part in parts:
                            if isinstance(part, dict) and 'text' in part:
                                text = part['text']
                                if text and text.strip():
                                    responses.append(text)
                except Exception:
                    continue

        return responses
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return []

def display_conversation_history(session_details: Dict[str, Any]):
    """Display conversation history from session events."""
    events = session_details.get('events', [])

    if not events:
        st.info("Let's get started! Tell me what location you're interested in. (i.e. chicago, IL)")
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
        page_title="Geo-Intent Agent",
        page_icon="🌍",
        layout="wide"
    )
    
    st.title("🌍 Geo-Intent Agent")
    st.markdown("An agent-driven framework that combines BigQuery AI and geospatial analysis to power competitive, scalable location intelligence.")
    
    
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
        st.session_state.user_name = str(uuid.uuid4())
    
    # Sidebar for session management
    with st.sidebar:
        user_id = st.session_state.user_name
        st.header("Let's get started")
        
        
        # Load sessions
        if st.session_state.refresh_sessions:
            st.session_state.sessions = get_sessions_list(user_id)
            st.session_state.refresh_sessions = False
        
        # Create new session
        if st.button("Start New Chat"):
            new_session_id = create_new_session(user_id)
            if new_session_id:
                st.success(f"Created new session: {new_session_id}")
                st.session_state.session_id = new_session_id
                st.session_state.refresh_sessions = True
                st.rerun()
        
        # Display sessions
        if st.session_state.sessions:
            st.subheader("Existing Chats")
            
            for i, session in enumerate(st.session_state.sessions):
                session_id = session.get('id', f'session_{i}')
                last_update = session.get('lastUpdateTime', 0)
                
                if last_update:
                    last_update_str = datetime.fromtimestamp(last_update).strftime('%m/%d %H:%M')
                else:
                    last_update_str = "Unknown"
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(f"📝 Chat Session - ({last_update_str})", key=f"select_{session_id}"):
                        st.session_state.session_id = session_id
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{session_id}", help="Delete session"):
                        if delete_session_by_id(RESOURCE_ID, user_id, session_id):
                            st.success("Session deleted!")
                            if st.session_state.session_id == session_id:
                                st.session_state.session_id = None
                            st.session_state.refresh_sessions = True
                            st.rerun()
        else:
            st.info("No existing conversations. Click 'Start New Chat' to create one.")
    
    # Main chat interface
    if st.session_state.session_id:
        
        # Get and display session details
        session_details = get_session_details(user_id, st.session_state.session_id)
        
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
                        responses = send_message_to_agent(RESOURCE_ID, user_id, st.session_state.session_id, user_message)
                    
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
        st.info("👈 Please select Start New Chat from the sidebar to start chatting.")
        
        # Display some helpful information
        st.markdown("""
       ### Coffee Shop Location Intelligence PoC

        This application is a Proof of Concept demonstrating an agent-driven framework for location intelligence, powered by BigQuery AI and geospatial analysis.

        **Use Case: Researching a New Coffee Shop Location**

        Imagine you are a business analyst for a coffee company looking to expand. You can use this agent to research potential new locations by asking questions about:

        *   **Demographics:** Understand the population in a specific area.
            *   *"What is the median household income in downtown San Francisco?"*
            *   *"Show me the population density for zip code 90210."*

        *   **Competition Analysis:** Identify existing competitors.
            *   *"Find all coffee shops within a 1-mile radius of the Ferry Building in San Francisco."*
            *   *"How many Starbucks are there in Austin, Texas?"*

        *   **Identifying Underserved Areas:** Discover locations with high demand and low competition.
            *   *"Which zip codes in Brooklyn have a high population density but fewer than 3 coffee shops?"*

        *   **Standardized Reporting:** Generate comprehensive reports for a region.
            *   *"Generate a full location intelligence report for Seattle, Washington."*
        
        **How to Start:**
        1.  Click "Start New Chat" in the sidebar.
        2.  Begin by specifying a location (e.g., "Let's focus on Chicago, IL").
        3.  Ask your research questions!
        """.format(user_id, RESOURCE_ID))

if __name__ == "__main__":
    main()
