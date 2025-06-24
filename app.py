import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://ai-chatbot-challenge.onrender.com")
API_BASE_URL = f"{BACKEND_URL}/api/v1"

# Page configuration
st.set_page_config(
    page_title="AI Chatbot with Memory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header::before {
        content: "🧠 AI Chatbot with Memory";
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        z-index: -1;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .memory-indicator {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 0.25rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.875rem;
    }
    
    .stats-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .chat-container {
        min-height: 400px;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Improve text visibility */
    .stMarkdown {
        color: #ffffff;
    }
    
    /* Make headers more visible */
    h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
    }
    
    /* Improve sidebar text */
    .css-1d391kg {
        color: #ffffff;
    }
    
    /* Better button styling */
    .stButton > button {
        background-color: #667eea;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #764ba2;
    }
    
    /* Improve chat input visibility */
    .stChatInput {
        background-color: #ffffff;
        border: 2px solid #667eea;
        border-radius: 0.5rem;
    }
    
    /* Better info boxes */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'memory_stats' not in st.session_state:
        st.session_state.memory_stats = {}
    if 'session_created' not in st.session_state:
        st.session_state.session_created = False
    if 'message_counter' not in st.session_state:
        st.session_state.message_counter = 0

def create_session():
    """Create a new conversation session."""
    try:
        response = requests.post(f"{API_BASE_URL}/session", params={"user_id": st.session_state.user_id})
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.messages = []
            st.session_state.session_created = True
            st.session_state.message_counter = 0
            return True
        return False
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return False

def load_conversation_history():
    """Load conversation history from backend."""
    if st.session_state.session_id:
        try:
            history = get_conversation_history()
            if history:
                st.session_state.messages = history
                st.session_state.message_counter = len(history)
            return True
        except Exception as e:
            st.error(f"Error loading conversation history: {e}")
    return False

def send_message(message: str) -> Dict[str, Any]:
    """Send a message to the backend and get response."""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id,
            "user_id": st.session_state.user_id,
            "use_memory": True
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return None

def get_conversation_history():
    """Get conversation history from backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/conversation/{st.session_state.session_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("messages", [])
        return []
    except Exception as e:
        st.error(f"Error getting conversation history: {e}")
        return []

def get_memory_stats():
    """Get memory statistics."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/memory/stats",
            params={"session_id": st.session_state.session_id}
        )
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error getting memory stats: {e}")
        return {}

def clear_conversation():
    """Clear conversation and memories."""
    try:
        response = requests.delete(f"{API_BASE_URL}/conversation/{st.session_state.session_id}")
        if response.status_code == 200:
            st.session_state.messages = []
            st.session_state.memory_stats = {}
            st.session_state.message_counter = 0
            st.success("Conversation cleared successfully!")
        else:
            st.error("Error clearing conversation")
    except Exception as e:
        st.error(f"Error clearing conversation: {e}")

def display_memory_visualization():
    """Display memory statistics and visualizations."""
    if not st.session_state.memory_stats:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Memories",
            st.session_state.memory_stats.get("total_memories", 0)
        )
    
    with col2:
        avg_similarity = st.session_state.memory_stats.get("average_similarity", 0)
        st.metric(
            "Avg Similarity",
            f"{avg_similarity:.3f}"
        )
    
    with col3:
        st.metric(
            "Session ID",
            st.session_state.session_id[:8] + "..." if st.session_state.session_id else "N/A"
        )

def main():
    # Initialize session state
    init_session_state()
    
    # Header with better visibility
    st.markdown('<h1 style="text-align: center; color: #ffffff; font-size: 3rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); margin-bottom: 2rem;">🧠 AI Chatbot with Memory</h1>', unsafe_allow_html=True)
    
    # Sidebar - Simplified with only essential controls
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Session management
        if st.button("🆕 New Session", use_container_width=True):
            if create_session():
                st.success("New session created!")
                st.rerun()
            else:
                st.error("Failed to create session")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            if st.session_state.session_id:
                clear_conversation()
                st.rerun()
            else:
                st.warning("No active session")
        
        # Add refresh button
        if st.button("🔄 Refresh History", use_container_width=True):
            if st.session_state.session_id:
                if load_conversation_history():
                    st.success("Conversation history refreshed!")
                    st.rerun()
                else:
                    st.error("Failed to refresh history")
            else:
                st.warning("No active session")
        
        st.divider()
            
    # Create session if not exists
    if not st.session_state.session_id:
        st.info("Click 'Start Chat' to begin a new conversation")
        if st.button("Start Chat", type="primary"):
            if create_session():
                st.success("Session created! You can now start chatting.")
                # Force a rerun to show the chat input
                st.rerun()
            else:
                st.error("Failed to create session")
        return
    
    # Load conversation history if session exists but messages are empty
    if st.session_state.session_id and not st.session_state.messages:
        load_conversation_history()
        
    # Main content with tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📊 Analytics"])
    
    with tab1:
        # Chat interface
        st.header("💬 Conversation")
        
        # Conversation summary
        if st.session_state.messages:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Messages", len(st.session_state.messages))
            with col2:
                memory_used_count = len([m for m in st.session_state.messages if m.get("memory_used")])
                st.metric("Memory Used", memory_used_count)
            with col3:
                total_tokens = sum([m.get("tokens_used", 0) for m in st.session_state.messages if m.get("tokens_used")])
                st.metric("Tokens Used", total_tokens)
        
        # Chat container with better styling
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages with Streamlit's native chat components
            if st.session_state.messages:
                for i, message in enumerate(st.session_state.messages):
                    if message["role"] == "user":
                        with st.chat_message("user"):
                            st.write(message["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message["content"])
                            
                            # Show memory information if available
                            if message.get("memory_used"):
                                st.info("🧠 Memory was used to generate this response")
                            
                            # Show memories retrieved if available
                            if message.get("memories_retrieved"):
                                memories = message["memories_retrieved"]
                                if memories:
                                    with st.expander(f"📚 Retrieved {len(memories)} memories", expanded=False):
                                        for j, memory in enumerate(memories[:3]):
                                            st.write(f"**Memory {j+1}:** {memory.get('content', '')[:200]}...")
                                            st.caption(f"Similarity: {memory.get('similarity_score', 0):.3f}")
    
    with tab2:
        # Analytics interface
        st.header("📊 Analytics & Insights")
        
        # Memory stats section
        st.subheader("🧠 Memory Statistics")
        
        # Refresh memory stats
        if st.button("🔄 Refresh Memory Stats"):
            st.session_state.memory_stats = get_memory_stats()
            st.rerun()
        
        # Display memory stats in a nice grid
        if st.session_state.memory_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Memories",
                    st.session_state.memory_stats.get("total_memories", 0),
                    help="Number of memories stored for this session"
                )
            
            with col2:
                avg_similarity = st.session_state.memory_stats.get("average_similarity", 0)
                st.metric(
                    "Avg Similarity",
                    f"{avg_similarity:.3f}",
                    help="Average similarity score of retrieved memories"
                )
            
            with col3:
                st.metric(
                    "Session ID",
                    st.session_state.session_id[:8] + "...",
                    help="Current session identifier"
                )
            
            with col4:
                st.metric(
                    "Memory Hits",
                    st.session_state.memory_stats.get("memory_hits", 0),
                    help="Number of times memories were retrieved"
                )
            
            # Memory usage chart
            st.subheader("📈 Memory Usage Over Time")
            
            # Create a simple bar chart for memory stats
            data = {
                "Metric": ["Total Memories", "Memory Hits", "Avg Similarity"],
                "Value": [
                    st.session_state.memory_stats.get("total_memories", 0),
                    st.session_state.memory_stats.get("memory_hits", 0),
                    st.session_state.memory_stats.get("average_similarity", 0) * 100
                ]
            }
            
            df = pd.DataFrame(data)
            fig = px.bar(df, x="Metric", y="Value", title="Memory Statistics", 
                        color="Metric", color_discrete_sequence=['#667eea', '#764ba2', '#f093fb'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Conversation analytics
        st.subheader("💬 Conversation Analytics")
        
        if st.session_state.messages:
            # Message count
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            
            # Create metrics
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("User Messages", user_messages, help="Total messages sent by user")
            with col_b:
                st.metric("AI Responses", assistant_messages, help="Total responses from AI")
            with col_c:
                total_messages = user_messages + assistant_messages
                st.metric("Total Messages", total_messages, help="Total conversation length")
            
            # Message distribution chart
            if total_messages > 0:
                message_data = {
                    "Role": ["User", "Assistant"],
                    "Count": [user_messages, assistant_messages]
                }
                msg_df = pd.DataFrame(message_data)
                fig2 = px.pie(msg_df, values="Count", names="Role", title="Message Distribution",
                            color_discrete_sequence=['#667eea', '#764ba2'])
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No conversation data available yet. Start chatting to see analytics!")
        
        # Recent activity
        st.subheader("🕒 Recent Activity")
        if st.session_state.messages:
            recent_messages = st.session_state.messages[-10:]  # Show last 10 messages
            
            # Create a nice timeline view
            for i, msg in enumerate(recent_messages):
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                role_color = "#667eea" if msg["role"] == "user" else "#764ba2"
                
                # Create a styled message box
                st.markdown(f"""
                <div style="
                    background-color: {role_color}20;
                    border-left: 4px solid {role_color};
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                    font-size: 14px;
                ">
                    <strong>{role_icon} {msg['role'].title()}:</strong> {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.text("No recent activity")
        
    # Make sure chat input is always visible when session exists
    if st.session_state.session_id:
        # Use a unique key based on session and message counter to ensure proper reset
        chat_key = f"chat_input_{st.session_state.session_id}_{st.session_state.message_counter}"
        user_input = st.chat_input("Type your message here...", key=chat_key)
        
        if user_input:
            # Immediately add user message to chat for instant feedback
            user_message = {"role": "user", "content": user_input}
            st.session_state.messages.append(user_message)
            st.session_state.message_counter += 1
            
            # Send message and get response with better loading feedback
            with st.spinner("🤔 AI is thinking..."):
                response = send_message(user_input)
            
            if response:
                # Add assistant response to chat with memory information
                assistant_message = {
                    "role": "assistant", 
                    "content": response["response"],
                    "memory_used": response.get("memory_used", False),
                    "memories_retrieved": response.get("memories_retrieved", []),
                    "tokens_used": response.get("tokens_used"),
                    "model_used": response.get("model_used")
                }
                st.session_state.messages.append(assistant_message)
                st.session_state.message_counter += 1
                
                # Update memory stats
                st.session_state.memory_stats = get_memory_stats()
                
                # Force rerun to show the new messages immediately
                st.rerun()
                
            else:
                # Remove the user message if response failed
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    st.session_state.messages.pop()
                    st.session_state.message_counter -= 1
                st.error("❌ Failed to get response. Please try again.")
    else:
        st.warning("⚠️ Please start a chat session first!")

if __name__ == "__main__":
    main() 