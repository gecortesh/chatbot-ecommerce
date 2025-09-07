import streamlit as st
import requests
import re
import uuid

# Configure Streamlit page
st.set_page_config(
    page_title="E-commerce Customer Service",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def initialize_session():
    """Initialize session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_available" not in st.session_state:
        st.session_state.api_available = check_api_health()
    
    if "api_info" not in st.session_state:
        st.session_state.api_info = get_api_info()

def check_api_health():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_api_info():
    """Get API information"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def send_message(message):
    """Send message to chatbot API"""
    try:
        with st.spinner("🤖 AI is thinking..."):
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={
                    "message": message,
                    "session_id": st.session_state.session_id
                },
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Request timed out. The AI is taking longer than expected."}
    except Exception as e:
        return {"error": f"🔌 Connection error: {str(e)}"}

def reset_conversation():
    """Reset the conversation"""
    try:
        response = requests.post(f"{API_BASE_URL}/reset/{st.session_state.session_id}")
        if response.status_code == 200:
            st.session_state.messages = []
            st.success("Conversation reset!")
            st.rerun()
        else:
            st.error("Failed to reset conversation")
    except Exception as e:
        st.error(f"Reset failed: {str(e)}")

def get_session_stats():
    """Get session statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/session/{st.session_state.session_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def format_bot_response(response: str) -> str:
    """Format bot response for better Streamlit display"""
    
    # Replace bullet points with proper markdown
    response = response.replace("•", "-")
    
    # Ensure proper spacing around bullet points
    response = re.sub(r'([a-z])\s*-\s*([A-Z])', r'\1\n\n- \2', response)
    
    lines = response.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # If line starts with bullet point info, format it properly
            if 'Order' in line and ('cancelled' in line or 'shipped' in line or 'delivered' in line):
                # Extract order info
                line = line.replace('- ', '').strip()
                formatted_lines.append(f"- **{line}**")
            elif line.startswith('-'):
                formatted_lines.append(f"{line}")
            else:
                formatted_lines.append(line)
    
    return '\n\n'.join(formatted_lines)

def main():
    """Main Streamlit app"""
    initialize_session()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .sidebar-metric {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🛒 E-commerce Customer Service</h1>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Order Management & Support**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # API Status
        if st.session_state.api_available:
            st.success("API Connected")
            if st.session_state.api_info:
                model_info = st.session_state.api_info.get("model", "Unknown")
                st.info(f"Model: {model_info}")
        else:
            st.error("API Disconnected")
            st.warning("Start the backend server:")
            st.code("python src/interfaces/web_api.py", language="bash")
        
        # Actions
        st.markdown("### Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset", use_container_width=True):
                reset_conversation()
        
        with col2:
            if st.button("Refresh", use_container_width=True):
                st.session_state.api_available = check_api_health()
                st.session_state.api_info = get_api_info()
                st.rerun()
        
        # Session Statistics
        st.markdown("### Session Info")
        st.markdown(f'<div class="sidebar-metric"><strong>Session ID:</strong><br/>{st.session_state.session_id[:8]}...</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-metric"><strong>Messages:</strong> {len(st.session_state.messages)}</div>', unsafe_allow_html=True)
        
        # Get additional stats if API is available
        if st.session_state.api_available:
            session_stats = get_session_stats()
            if session_stats:
                st.markdown(f'<div class="sidebar-metric"><strong>Created:</strong><br/>{session_stats.get("created_at", "N/A")}</div>', unsafe_allow_html=True)
        
        # Help Section
        st.markdown("---")
        st.markdown("### 💡 How to Use")
        
        # Expandable help sections
        with st.expander("📦 Order Tracking"):
            st.markdown("""
            • "Track my orders for john@example.com"
            • "What's the status of order ORD001?"
            • "Check my order ORD002 for jane@example.com"
            """)
        
        with st.expander("❌ Order Cancellation"):
            st.markdown("""
            • "Cancel order ORD001 for john@example.com"
            • "I want to cancel my order ORD003"
            • "Please cancel order ORD002"
            """)
        
        with st.expander("📧 Test Data"):
            st.markdown("""
            **john@example.com:**
            • ORD001: Cancelled ($999.99)
            • ORD002: Shipped ($59.98)
            • ORD004: Delivered ($159.99)
            
            **jane@example.com:**
            • ORD003: Cancelled ($79.99)
            """)
        
        # Policies
        st.markdown("---")
        st.markdown("### 📋 Policies")
        st.caption("✅ Orders cancellable within 10 days")
        st.caption("❌ No cancellation if shipped/delivered")
        st.caption("⚠️ Processing orders can be cancelled")
    
    # Main chat interface
    if not st.session_state.api_available:
        st.error("**Chatbot API is not available**")
        st.info("Please start the backend server to use the chatbot:")
        st.code("python src/interfaces/web_api.py", language="bash")
        
        # Show connection troubleshooting
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            1. **Start the API server:**
               ```bash
               python src/interfaces/web_api.py
               ```
            
            2. **Check if the server is running:**
               - Open http://localhost:8000 in your browser
               - You should see the API information
            
            3. **Common issues:**
               - Port 8000 might be in use
               - Python dependencies not installed
               - Virtual environment not activated
            """)
        return
    
    # Quick start suggestions
    if not st.session_state.messages:
        st.info("👋 **Welcome!** Try these example queries to get started:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📦 Track Orders", use_container_width=True):
                st.session_state.quick_message = "Track my orders for john@example.com"
        
        with col2:
            if st.button("❓ Check Status", use_container_width=True):
                st.session_state.quick_message = "What's the status of order ORD001 for john@example.com?"
        
        with col3:
            if st.button("❌ Cancel Order", use_container_width=True):
                st.session_state.quick_message = "Cancel order ORD002 for john@example.com"
    
    # Handle quick message
    if hasattr(st.session_state, 'quick_message'):
        prompt = st.session_state.quick_message
        del st.session_state.quick_message
        
        # Add to message history and process
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get bot response
        result = send_message(prompt)
        
        if result and "error" not in result:
            bot_response = result["response"]
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
        else:
            error_msg = result.get("error", "Unknown error") if result else "Failed to get response"
            st.session_state.messages.append({"role": "assistant", "content": f"❌ {error_msg}"})
        
        st.rerun()
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💬 Type your message here... (e.g., 'Track my orders for john@example.com')"):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)
        
        # Get bot response
        with st.chat_message("assistant", avatar="🤖"):
            result = send_message(prompt)
            
            if result and "error" not in result:
                bot_response = result["response"]
                formatted_response = format_bot_response(bot_response)
                st.markdown(formatted_response)  # Use markdown instead of write
                
                # Show response time if available
                if "response_time" in result:
                    st.caption(f"⚡ Response time: {result['response_time']:.2f}s")
                
                # Add to session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": bot_response
                })
                
            else:
                error_msg = result.get("error", "Unknown error") if result else "Failed to get response"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"{error_msg}"
                })

    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.8rem;">'
        '🤖 Powered by llama-cpp + Phi-3.5 | Built with Streamlit & FastAPI'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()