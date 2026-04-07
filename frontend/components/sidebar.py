"""
Sidebar Component - Modern Sleek Dark Mode

Provides settings panel and status information in the sidebar with glassmorphism design.
"""

import streamlit as st
from frontend.api_client import BackendClient


def render_custom_expander(title: str, content: str, key: str = None):
    """Render a custom HTML expander using details/summary elements."""
    expander_html = f"""
    <details style="border: 1px solid #30363D; border-radius: 8px; overflow: hidden; margin-bottom: 8px; background: #1E252E;">
        <summary style="background: #1E252E; color: #E0E0E0; padding: 10px 14px; cursor: pointer; font-weight: 500; font-size: 14px; list-style: none; display: flex; align-items: center; gap: 8px;">
            <span style="transition: transform 0.2s ease;">▶</span>
            <span>{title}</span>
        </summary>
        <div style="background: #0D1117; padding: 12px 14px; border-top: 1px solid #30363D; color: #A0A0A0; font-size: 13px; line-height: 1.6;">
            {content}
        </div>
    </details>
    """
    st.markdown(expander_html, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings and status - Modern Sleek Design."""
    with st.sidebar:
        # App branding with modern layout
        st.markdown("""
            <div style='text-align: center; margin-bottom: 24px; padding: 16px 0;'>
                <div style='display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 14px; background: linear-gradient(135deg, #007AFF 0%, #BB86FC 100%); margin-bottom: 12px;'>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="11" width="18" height="10" rx="2"></rect>
                        <circle cx="12" cy="5" r="2"></circle>
                        <path d="M12 7v4"></path>
                    </svg>
                </div>
                <div style='font-size: 17px; font-weight: 600; color: #E0E0E0; letter-spacing: -0.3px;'>MCP Data Assistant</div>
                <span class="version-badge">v0.1.0</span>
            </div>
        """, unsafe_allow_html=True)

        # Connection Settings Card
        st.markdown('<div class="sidebar-section-title">Connection</div>', unsafe_allow_html=True)
        
        with st.container():
            backend_url = st.text_input(
                "Backend URL",
                value=st.session_state.get("backend_url", "http://localhost:8000"),
                key="backend_url_input",
                label_visibility="collapsed",
                placeholder="http://localhost:8000"
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Check Connection", use_container_width=True, type="primary"):
                    with st.spinner("Checking connection..."):
                        client = BackendClient(base_url=backend_url)
                        try:
                            import asyncio
                            status = asyncio.run(client.health_check())
                            st.session_state["backend_status"] = "connected"
                            st.success(f"Connected: {status.get('service', 'Unknown')}")
                        except Exception as e:
                            st.session_state["backend_status"] = "disconnected"
                            st.error(f"Connection failed: {str(e)[:80]}")

                        st.session_state["backend_url"] = backend_url

            # Connection status indicator with glowing dot
            status = st.session_state.get("backend_status", "unknown")
            with col2:
                if status == "connected":
                    st.markdown('<div class="status-chip connected"><span class="status-dot connected"></span>Online</div>', unsafe_allow_html=True)
                elif status == "disconnected":
                    st.markdown('<div class="status-chip disconnected"><span class="status-dot disconnected"></span>Offline</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-chip idle"><span class="status-dot idle"></span>Idle</div>', unsafe_allow_html=True)

        st.divider()

        # Quick Actions Card
        st.markdown('<div class="sidebar-section-title">Quick Actions</div>', unsafe_allow_html=True)
        
        with st.container():
            if st.button("📂  List Files", use_container_width=True):
                st.session_state["quick_action"] = "list_files"
                st.rerun()

            if st.button("🗃️  List Tables", use_container_width=True):
                st.session_state["quick_action"] = "list_tables"
                st.rerun()

            if st.button("🧹  Clear Chat", use_container_width=True, type="secondary"):
                st.session_state["chat_history"] = []
                st.session_state["quick_action"] = None
                st.rerun()

        st.divider()

        # Tips Section - Using custom HTML expanders to avoid overlay issues
        st.markdown('<div class="sidebar-section-title">Help & Tips</div>', unsafe_allow_html=True)
        
        # Example Questions expander
        render_custom_expander(
            "💬 Example Questions",
            """
            <ul style="margin: 0; padding-left: 16px; color: #A0A0A0;">
                <li style="margin-bottom: 6px;"><em>What files are available?</em></li>
                <li style="margin-bottom: 6px;"><em>Show me the first 5 rows of sales.csv</em></li>
                <li style="margin-bottom: 6px;"><em>What tables are in the database?</em></li>
                <li><em>What are the columns in products.xlsx?</em></li>
            </ul>
            """
        )

        # Setup Requirements expander
        render_custom_expander(
            "⚙️ Setup Requirements",
            """
            <ul style="margin: 0; padding-left: 16px; color: #A0A0A0;">
                <li style="margin-bottom: 6px;">✅ LM Studio running on port 1234</li>
                <li style="margin-bottom: 6px;">✅ Backend running on port 8000</li>
                <li style="margin-bottom: 6px;">✅ Data files in /data folder</li>
                <li>✅ Database configured in .env</li>
            </ul>
            """
        )

        # Footer
        st.divider()
        st.markdown("""
            <div class="sidebar-footer">
                Built with Streamlit & FastMCP
            </div>
        """, unsafe_allow_html=True)