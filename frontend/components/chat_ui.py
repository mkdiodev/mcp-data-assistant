"""
Chat UI Component - Modern Sleek Dark Mode

Provides a modern chat interface with sleek dark theme design.
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime


# ============================================
# CSS Styles - Modern Sleek Dark Mode
# ============================================

SLEEK_DARK_CSS = """
<style>
    /* === IMPORT GOOGLE FONT: INTER === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* === MAIN THEME COLORS === */
    :root {
        --bg-primary: #0E1117;
        --bg-secondary: #161B22;
        --bg-card: #1E252E;
        --bg-input: #0D1117;
        --text-primary: #E0E0E0;
        --text-secondary: #A0A0A0;
        --text-muted: #6B7280;
        --accent-blue: #007AFF;
        --accent-purple: #BB86FC;
        --accent-gradient: linear-gradient(135deg, #007AFF 0%, #BB86FC 100%);
        --border-color: #30363D;
        --border-hover: #58A6FF;
        --success: #10b981;
        --error: #ef4444;
        --warning: #f59e0b;
        --idle: #F59E0B;
    }

    /* === GLOBAL TYPOGRAPHY === */
    * {
        font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* === MAIN CONTAINER === */
    .main {
        background-color: var(--bg-primary) !important;
    }

    .stApp {
        background: var(--bg-primary) !important;
    }

    /* === GLASSMORPHISM SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: rgba(22, 27, 34, 0.85) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid var(--border-color) !important;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    /* === CARD-LIKE CONTAINERS IN SIDEBAR === */
    .sidebar-card {
        background: var(--bg-card) !important;
        padding: 16px !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        margin-bottom: 12px !important;
        transition: all 0.3s ease;
    }

    .sidebar-card:hover {
        border-color: var(--border-hover) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }

    /* === PROFESSIONAL BUTTONS === */
    .stButton > button {
        width: 100% !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        background-color: #21262D !important;
        color: #C9D1D9 !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
    }

    .stButton > button:hover {
        border-color: var(--border-hover) !important;
        color: var(--border-hover) !important;
        background-color: #1C2128 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Primary button variant */
    .stButton > button[kind="primary"] {
        background: var(--accent-gradient) !important;
        border: none !important;
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover {
        opacity: 0.9 !important;
        box-shadow: 0 6px 20px rgba(0, 122, 255, 0.3) !important;
    }

    /* === INPUT FIELD STYLING === */
    .stTextInput input,
    .stTextInput textarea {
        background-color: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }

    .stTextInput input:focus,
    .stTextInput textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15) !important;
    }

    /* === CHAT INPUT FIXED AT BOTTOM === */
    div[data-testid="stChatInput"] {
        border-radius: 15px !important;
        border: 1px solid var(--border-color) !important;
        background-color: var(--bg-secondary) !important;
        padding: 10px !important;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.2);
    }

    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--text-primary) !important;
        border: none !important;
        font-size: 15px !important;
    }

    div[data-testid="stChatInput"] textarea:focus {
        box-shadow: none !important;
    }

    div[data-testid="stChatInput"] button {
        background: var(--accent-gradient) !important;
        border: none !important;
        border-radius: 10px !important;
        transition: all 0.2s ease;
    }

    div[data-testid="stChatInput"] button:hover {
        opacity: 0.85 !important;
        transform: scale(1.05);
    }

    /* === CHAT MESSAGE STYLES === */
    .message-block {
        display: flex;
        margin-bottom: 16px;
        padding: 12px 0;
        animation: fadeIn 0.3s ease;
    }

    .message-user {
        justify-content: flex-end;
    }

    .message-assistant {
        justify-content: flex-start;
    }

    .message-bubble {
        max-width: 80%;
        padding: 14px 20px;
        border-radius: 20px;
        font-size: 15px;
        line-height: 1.6;
        word-wrap: break-word;
    }

    .message-user .message-bubble {
        background: linear-gradient(135deg, #007AFF 0%, #0055D4 100%);
        color: white;
        border-bottom-right-radius: 6px;
    }

    .message-assistant .message-bubble {
        background: #1A1F26;
        color: var(--text-primary);
        border-bottom-left-radius: 6px;
        border: 1px solid var(--border-color);
    }

    /* === AVATAR STYLES (Perfectly Round) === */
    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        font-weight: 500;
        flex-shrink: 0;
        margin: 0 10px;
        overflow: hidden;
    }

    .avatar-user {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    }

    .avatar-assistant {
        background: linear-gradient(135deg, #007AFF 0%, #00C6FF 100%);
    }

    /* === GLOWING STATUS INDICATOR === */
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 8px currentColor;
        animation: pulse 2s infinite;
    }

    .status-dot.connected {
        background-color: var(--success);
        color: var(--success);
    }

    .status-dot.disconnected {
        background-color: var(--error);
        color: var(--error);
    }

    .status-dot.idle {
        background-color: var(--idle);
        color: var(--idle);
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* === STATUS CHIP === */
    .status-chip {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border-color);
    }

    .status-chip.connected {
        border-color: rgba(16, 185, 129, 0.3);
        color: var(--success);
    }

    .status-chip.disconnected {
        border-color: rgba(239, 68, 68, 0.3);
        color: var(--error);
    }

    .status-chip.idle {
        border-color: rgba(245, 158, 11, 0.3);
        color: var(--idle);
    }

    /* === HEADER === */
    .header-container {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }

    .header-title {
        font-size: 26px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }

    .header-title span {
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .header-subtitle {
        font-size: 13px;
        color: var(--text-secondary);
        font-weight: 400;
    }

    /* === LOADING ANIMATION === */
    .loading-dots {
        display: inline-flex;
        gap: 6px;
        align-items: center;
    }

    .loading-dots span {
        width: 8px;
        height: 8px;
        background: var(--accent-blue);
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out;
    }

    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
    .loading-dots span:nth-child(3) { animation-delay: 0s; }

    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.25);
    }

    /* === TABLES === */
    .stDataFrame {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid var(--border-color) !important;
    }

    .stDataFrame table {
        color: var(--text-primary) !important;
    }

    .stDataFrame th {
        background: #1A1F26 !important;
        color: var(--accent-blue) !important;
    }

    .stDataFrame td {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }

    /* === CODE BLOCKS === */
    pre {
        background: #1A1F26 !important;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 16px;
        overflow-x: auto;
    }

    code {
        background: #1A1F26 !important;
        color: #7EE787 !important;
        padding: 3px 8px;
        border-radius: 6px;
        font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace !important;
        font-size: 13px !important;
    }

    /* === MARKDOWN TABLE FIX === */
    .stMarkdown table {
        color: var(--text-primary) !important;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }

    .stMarkdown th {
        background: #1A1F26 !important;
        color: var(--accent-blue) !important;
        padding: 12px 16px !important;
        font-weight: 600;
    }

    .stMarkdown td {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: 10px 16px !important;
        border-top: 1px solid var(--border-color);
    }

    /* === EXPANDER STYLING === */
    details[data-testid="stExpander"] {
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        overflow: hidden;
        margin-bottom: 8px;
        background: var(--bg-card) !important;
    }

    details[data-testid="stExpander"] summary {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: 10px 14px !important;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500 !important;
        font-size: 14px !important;
        list-style: none !important;
    }

    details[data-testid="stExpander"] summary:hover {
        background: #252D38 !important;
    }

    /* Hide all default markers and arrows */
    details[data-testid="stExpander"] summary::-webkit-details-marker {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }

    details[data-testid="stExpander"] summary::marker {
        content: "" !important;
        display: none !important;
    }

    details[data-testid="stExpander"] summary::before {
        display: none !important;
    }

    details[data-testid="stExpander"] summary::after {
        display: none !important;
    }

    /* Hide any span that contains arrow text */
    details[data-testid="stExpander"] summary span {
        display: none !important;
    }

    /* Ensure paragraph text is visible */
    details[data-testid="stExpander"] summary p {
        color: var(--text-primary) !important;
        margin: 0 !important;
        display: block !important;
        font-weight: 500 !important;
    }

    /* Expander content area */
    details[data-testid="stExpander"] > div {
        background: var(--bg-input) !important;
        padding: 12px 14px !important;
        border-top: 1px solid var(--border-color) !important;
    }

    details[data-testid="stExpander"] > div p {
        color: var(--text-secondary) !important;
        margin: 4px 0 !important;
    }

    /* Additional fix for Streamlit expander label */
    div[data-testid="stExpander"] p {
        color: var(--text-primary) !important;
    }

    /* Hide arrow icon container */
    div[data-testid="stExpander"] svg {
        display: none !important;
    }

    /* === METRICS === */
    [data-testid="stMetricValue"] {
        color: var(--accent-blue) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }

    /* === DIVIDER === */
    hr {
        border-color: var(--border-color) !important;
    }

    /* === SIDEBAR SECTION HEADERS === */
    .sidebar-section-title {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--text-muted);
        margin-bottom: 10px;
        padding-left: 4px;
    }

    /* === VERSION BADGE === */
    .version-badge {
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 10px;
        color: var(--text-muted);
        opacity: 0.5;
        background: rgba(255, 255, 255, 0.05);
        padding: 2px 6px;
        border-radius: 4px;
    }

    /* === FOOTER === */
    .sidebar-footer {
        text-align: center;
        font-size: 11px;
        color: var(--text-muted);
        padding-top: 8px;
        border-top: 1px solid var(--border-color);
        margin-top: 12px;
    }
</style>
"""


def inject_styles():
    """Inject Modern Sleek Dark Mode styles into the app."""
    st.markdown(SLEEK_DARK_CSS, unsafe_allow_html=True)


def render_header():
    """Render the app header with branding."""
    st.markdown("""
        <div class="header-container">
            <div class="header-title"><span>MCP Data Assistant</span></div>
            <div class="header-subtitle">Ask questions about your files and databases</div>
        </div>
    """, unsafe_allow_html=True)


def render_message(role: str, content: str, timestamp: str = None):
    """
    Render a chat message with proper styling.

    Args:
        role: 'user' or 'assistant'
        content: Message content
        timestamp: Optional timestamp string
    """
    # Avatar icons (using simple SVG for cleaner look)
    if role == "user":
        avatar_icon = """
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
        """
    else:
        avatar_icon = """
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="10" rx="2"></rect>
                <circle cx="12" cy="5" r="2"></circle>
                <path d="M12 7v4"></path>
                <line x1="8" y1="16" x2="8" y2="16"></line>
                <line x1="16" y1="16" x2="16" y2="16"></line>
            </svg>
        """
    
    avatar_class = "avatar-user" if role == "user" else "avatar-assistant"
    message_class = "message-user" if role == "user" else "message-assistant"

    # Format timestamp
    time_html = ""
    if timestamp:
        time_html = f"<div style='font-size: 11px; color: var(--text-muted); margin-top: 6px;'>{timestamp}</div>"

    # Parse markdown tables and convert to HTML
    if "```" in content or "|" in content:
        # Try to extract and render tables
        content_html = parse_and_show_table(content)
    else:
        content_html = content.replace("\n", "<br>")

    st.markdown(f"""
        <div class="message-block {message_class}">
            <div class="avatar {avatar_class}">{avatar_icon}</div>
            <div class="message-bubble">
                {content_html}
                {time_html}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_loading():
    """Render loading animation."""
    st.markdown("""
        <div class="message-block message-assistant">
            <div class="avatar avatar-assistant">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="10" rx="2"></rect>
                    <circle cx="12" cy="5" r="2"></circle>
                    <path d="M12 7v4"></path>
                </svg>
            </div>
            <div class="message-bubble">
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def parse_and_show_table(content: str) -> str:
    """
    Parse markdown table in content and render as HTML table.

    Returns the content with properly rendered tables.
    """
    # Check if content contains a markdown table
    lines = content.strip().split("\n")

    # Simple detection: look for | character and separator row
    has_table = False
    table_start = -1

    for i, line in enumerate(lines):
        if "|" in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if "---" in next_line and "|" in next_line:
                has_table = True
                table_start = i
                break

    if not has_table:
        return content.replace("\n", "<br>")

    # Convert markdown table to HTML table
    result = []
    i = 0
    in_table = False

    while i < len(lines):
        line = lines[i].strip()

        if i == table_start or in_table:
            in_table = True

            # Check if this is the ending of the table
            if i > table_start + 1:
                result.append("</table>")
                in_table = False
                result.append(line.replace("\n", "<br>"))
                i += 1
                continue

            # Parse table rows
            if "|" in line and "---" not in line:
                # Extract cells
                cells = [c.strip() for c in line.strip("|").split("|")]

                # Header row (right after separator)
                if i == table_start:
                    result.append("<table style='width: 100%; border-collapse: collapse; margin: 8px 0;'>")
                    header_row = "<thead><tr>"
                    for cell in cells:
                        header_row += f"<th style='padding: 10px 12px; text-align: left; color: #8b5cf6; border-bottom: 2px solid #4f5258;'>{cell}</th>"
                    header_row += "</tr></thead><tbody>"
                    result.append(header_row)
                else:
                    # Data row
                    body_row = "<tr>"
                    for cell in cells:
                        body_row += f"<td style='padding: 8px 12px; border-top: 1px solid #4f5258;'>{cell}</td>"
                    body_row += "</tr>"
                    result.append(body_row)
            elif "---" in line:
                # Skip separator row
                pass

        else:
            result.append(line.replace("\n", "<br>"))

        i += 1

    # Close table if still open
    if in_table:
        result.append("</tbody></table>")

    return "".join(result)


def show_data_preview(data: str):
    """
    Show a data preview panel with extracted table data.

    Args:
        data: Raw data string (usually markdown table)
    """
    try:
        # Try to parse as DataFrame if it looks like table data
        if "rows" in data.lower() and "|" in data:
            st.markdown("""
                <div style='background: #1f2937; padding: 12px; border-radius: 8px; margin: 8px 0;'>
                    <strong style='color: #8b5cf6;'>📊 Data Preview</strong>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(data)
    except Exception:
        pass