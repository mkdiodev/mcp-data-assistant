"""
MCP Data Assistant - Main Streamlit Application

Entry point for the frontend application with Modern Sleek Dark Mode UI.
"""

import streamlit as st
import asyncio
from datetime import datetime

from frontend.components.chat_ui import inject_styles, render_header, render_message, render_loading
from frontend.components.sidebar import render_sidebar
from frontend.api_client import BackendClient


# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="MCP Data Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# Initialize Session State
# ============================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "backend_status" not in st.session_state:
    st.session_state.backend_status = "unknown"

if "backend_url" not in st.session_state:
    st.session_state.backend_url = "http://localhost:8000"

if "quick_action" not in st.session_state:
    st.session_state.quick_action = None

if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

if "pending_message" not in st.session_state:
    st.session_state.pending_message = None

if "needs_rerun" not in st.session_state:
    st.session_state.needs_rerun = False


# ============================================
# Inject Styles
# ============================================

inject_styles()


# ============================================
# Async Helper Functions (Sync wrappers for Streamlit)
# ============================================

def run_async(coro):
    """
    Run an async coroutine in Streamlit's thread.
    
    This is needed because Python 3.14+ no longer provides a default
    event loop in non-main threads. We create a new event loop for
    each call to ensure compatibility.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


async def _process_quick_action(action: str) -> str:
    """Process quick actions and generate appropriate messages."""
    client = BackendClient(base_url=st.session_state.backend_url)

    if action == "list_files":
        try:
            files = await client.list_files()
            if files:
                return "Show me what files are available in the data folder."
            else:
                return "List all available data files."
        except Exception:
            return "What files are in the data folder?"

    elif action == "list_tables":
        return "What tables are available in the database?"

    return ""


def process_quick_action(action: str) -> str:
    """Sync wrapper for _process_quick_action."""
    return run_async(_process_quick_action(action))


def _add_user_message_to_history(message: str):
    """Add user message to chat history and set loading state."""
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({
        "role": "user",
        "content": message,
        "timestamp": timestamp,
    })
    st.session_state.is_loading = True


async def _fetch_ai_response(message: str):
    """Fetch AI response for a user message."""
    try:
        client = BackendClient(base_url=st.session_state.backend_url)

        # Build history for API (exclude the current user message)
        history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.chat_history[:-1]
        ]

        # Send message to backend
        response = await client.send_message(message=message, history=history)

        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["response"],
            "timestamp": datetime.now().strftime("%H:%M"),
        })

        st.session_state.backend_status = "connected"

    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"\u26a0\ufe0f **Error**: Could not connect to the backend.\n\n"
                       f"Please ensure:\n"
                       f"1. LM Studio is running on port 1234\n"
                       f"2. Backend server is running on port 8000\n\n"
                       f"Details: `{str(e)[:100]}`",
            "timestamp": datetime.now().strftime("%H:%M"),
        })
        st.session_state.backend_status = "disconnected"

    finally:
        st.session_state.is_loading = False
        st.session_state.quick_action = None
        st.session_state.pending_message = None


# ============================================
# Main Application
# ============================================

def main():
    """Main application entry point."""
    # Render sidebar
    render_sidebar()

    # Render header
    render_header()

    # Handle quick actions
    if st.session_state.quick_action and not st.session_state.pending_message:
        message = process_quick_action(st.session_state.quick_action)
        if message:
            _add_user_message_to_history(message)
            st.session_state.pending_message = message
            st.rerun()
            st.stop()

    # Check if we just added a user message and need to show it before fetching AI
    if st.session_state.needs_rerun:
        st.session_state.needs_rerun = False
        # Render messages and loading, then rerun to process AI
        for msg in st.session_state.chat_history:
            render_message(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg.get("timestamp"),
            )
        if st.session_state.is_loading:
            render_loading()
        st.divider()
        st.chat_input("Processing...", key="user_input_disabled")
        st.rerun()
        st.stop()

    # Process pending message (get AI response - this blocks)
    if st.session_state.pending_message:
        message = st.session_state.pending_message
        run_async(_fetch_ai_response(message))

    # Render chat messages
    for msg in st.session_state.chat_history:
        render_message(
            role=msg["role"],
            content=msg["content"],
            timestamp=msg.get("timestamp"),
        )

    # Show loading indicator
    if st.session_state.is_loading:
        render_loading()

    # Chat input
    st.divider()

    user_input = st.chat_input(
        "Ask about your files or data...",
        key="user_input",
    )

    # Handle user input
    if user_input:
        _add_user_message_to_history(user_input)
        st.session_state.pending_message = user_input
        st.session_state.needs_rerun = True
        st.rerun()
        st.stop()

    # Auto-scroll to bottom
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()