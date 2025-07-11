import streamlit as st
import sys
import os
from datetime import datetime

# Add the path to your main.py if it's in a different directory
# sys.path.append('path/to/your/main/directory')

# Import your main workflow function
try:
    from main import execute_nodedesk
except ImportError:
    st.error("Could not import execute_nodedesk from main.py. Please ensure main.py is in the same directory or adjust the import path.")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="NodeDesk IT Support Assistant",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        color: #2E86AB;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #2E86AB;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #1976d2;
    }
    .assistant-message {
        background-color: #f1f8e9;
        border-left-color: #388e3c;
    }
    .ticket-info {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .stats-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .feedback-buttons {
        display: flex;
        gap: 10px;
        margin: 1rem 0;
        justify-content: center;
    }
    .feedback-section {
        background-color: #f8f9fa;
        border: 2px dashed #dee2e6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'ticket_counter' not in st.session_state:
    st.session_state.ticket_counter = 0
if 'resolved_tickets' not in st.session_state:
    st.session_state.resolved_tickets = 0
if 'escalated_tickets' not in st.session_state:
    st.session_state.escalated_tickets = 0
if 'pending_feedback' not in st.session_state:
    st.session_state.pending_feedback = []

# Header
st.markdown("<h1 class='main-header'>🖥️ NodeDesk IT Support Assistant</h1>", unsafe_allow_html=True)

# Sidebar with stats and information
with st.sidebar:
    st.header("📊 Session Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='stats-card'>
            <h3 style='color: #1f2937; font-weight: bold;'>{st.session_state.ticket_counter}</h3>
            <p style='color: #4b5563; margin: 0.5rem 0 0 0;'>Total Tickets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stats-card'>
            <h3 style='color: #16a34a; font-weight: bold;'>{st.session_state.resolved_tickets}</h3>
            <p style='color: #4b5563; margin: 0.5rem 0 0 0;'>Resolved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stats-card'>
            <h3 style='color: #dc2626; font-weight: bold;'>{st.session_state.escalated_tickets}</h3>
            <p style='color: #4b5563; margin: 0.5rem 0 0 0;'>Escalated</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.header("ℹ️ How it works")
    st.markdown("""
    **NodeDesk** helps with IT support by:
    
    1. **Classifying** your query (Technical vs Non-Technical)
    2. **Categorizing** IT issues (Hardware, Software, Network, etc.)
    3. **Providing** step-by-step guidance
    4. **Creating** tickets for resolution tracking
    
    **Supported Categories:**
    - 🖥️ Hardware (Computers, Printers, Servers)
    - 💾 Software (Applications, Operating Systems)
    - 🌐 Network (Internet, Connectivity, VPN)
    - 🔒 Security (Passwords, Access Control)
    - 📧 Email (Business Email Systems)
    - 🗄️ Database (Data Storage, SQL)
    """)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.ticket_counter = 0
        st.session_state.resolved_tickets = 0
        st.session_state.escalated_tickets = 0
        st.rerun()

# Main chat interface
st.header("💬 Chat Interface")

# Display chat history
if st.session_state.chat_history:
    for i, chat in enumerate(st.session_state.chat_history):
        # User message
        st.markdown(f"""
        <div class='chat-message user-message'>
            <strong style='color: #1565c0;'>👤 You:</strong><br>
            <span style='color: #1f2937;'>{chat['query']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Assistant response
        st.markdown(f"""
        <div class='chat-message assistant-message'>
            <strong style='color: #2e7d32;'>🤖 NodeDesk Assistant:</strong><br>
            <span style='color: #1f2937;'>{chat['answer']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Show feedback buttons for technical queries that haven't been rated yet
        if chat['it_category'] != 'Non-Technical' and chat.get('satisfaction_level') is None:
            st.markdown(f"""
            <div class='feedback-section'>
                <p style='color: #1f2937; margin-bottom: 1rem;'><strong>Was this solution helpful?</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ Yes, this helped!", key=f"satisfied_{i}", type="primary"):
                    st.session_state.chat_history[i]['satisfaction_level'] = 'Satisfied'
                    st.session_state.chat_history[i]['ticket_status'] = 'Resolved'
                    st.session_state.resolved_tickets += 1
                    st.success("Great! Ticket marked as resolved.")
                    st.rerun()
            
            with col2:
                if st.button("❌ No, still need help", key=f"unsatisfied_{i}", type="secondary"):
                    st.session_state.chat_history[i]['satisfaction_level'] = 'Unsatisfied'
                    st.session_state.chat_history[i]['ticket_status'] = 'Escalated'
                    st.session_state.escalated_tickets += 1
                    st.warning("Ticket escalated to human support.")
                    st.rerun()
            
            with col3:
                if st.button("❓ Need more info", key=f"neutral_{i}"):
                    st.session_state.chat_history[i]['satisfaction_level'] = 'Neutral'
                    st.session_state.chat_history[i]['ticket_status'] = 'Pending'
                    st.info("You can ask a follow-up question below.")
                    st.rerun()
        
        # Ticket information (only show if feedback has been given)
        elif chat.get('satisfaction_level') is not None:
            ticket_status_map = {
                'Satisfied': '✅ Resolved',
                'Unsatisfied': '⚠️ Escalated',
                'Neutral': '🔄 Pending'
            }
            ticket_status = ticket_status_map.get(chat['satisfaction_level'], '❓ Unknown')
            
            st.markdown(f"""
            <div class='ticket-info'>
                <strong style='color: #1f2937;'>🎫 Ticket #{i+1} - {ticket_status}</strong><br>
                <strong style='color: #374151;'>Category:</strong> <span style='color: #1f2937;'>{chat['it_category']}</span><br>
                <strong style='color: #374151;'>Status:</strong> <span style='color: #1f2937;'>{chat['satisfaction_level']}</span><br>
                <strong style='color: #374151;'>Created:</strong> <span style='color: #1f2937;'>{chat['timestamp']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # For non-technical queries, automatically mark as resolved
        elif chat['it_category'] == 'Non-Technical':
            st.markdown(f"""
            <div class='ticket-info'>
                <strong style='color: #1f2937;'>🎫 Ticket #{i+1} - ✅ Resolved (Non-Technical)</strong><br>
                <strong style='color: #374151;'>Category:</strong> <span style='color: #1f2937;'>{chat['it_category']}</span><br>
                <strong style='color: #374151;'>Status:</strong> <span style='color: #1f2937;'>Redirected</span><br>
                <strong style='color: #374151;'>Created:</strong> <span style='color: #1f2937;'>{chat['timestamp']}</span>
            </div>
            """, unsafe_allow_html=True)

# Input form
with st.form("query_form", clear_on_submit=True):
    user_query = st.text_area(
        "Enter your IT support question:",
        placeholder="Describe your technical issue here... (e.g., 'My computer won't start', 'Email not working', 'Cannot connect to network')",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submit_button = st.form_submit_button("🚀 Submit Query", type="primary")
    with col2:
        example_button = st.form_submit_button("💡 Try Example", type="secondary")

# Handle example button
if example_button:
    example_queries = [
        "My laptop won't connect to the office WiFi",
        "Outlook keeps crashing when I try to send emails",
        "I forgot my password and can't access the database",
        "The printer is showing a paper jam error but there's no paper stuck",
        "I can't install the new software on my computer"
    ]
    import random
    user_query = random.choice(example_queries)
    submit_button = True

# Process query
if submit_button and user_query.strip():
    with st.spinner("🤔 Processing your query..."):
        try:
            # Call your main workflow
            result = execute_nodedesk(user_query.strip())
            
            # Update session state
            chat_entry = {
                'query': user_query.strip(),
                'answer': result['answer'],
                'it_category': result['it_category'],
                'satisfaction_level': None,  # Will be set by user feedback
                'ticket_created': True,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.chat_history.append(chat_entry)
            st.session_state.ticket_counter += 1
            
            # For non-technical queries, auto-resolve
            if result['it_category'] == 'Non-Technical':
                st.session_state.chat_history[-1]['satisfaction_level'] = 'Redirected'
                st.session_state.resolved_tickets += 1
            
            # Show success message and rerun to display the new chat
            st.success("✅ Query processed successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ An error occurred while processing your query: {str(e)}")
            st.exception(e)

elif submit_button and not user_query.strip():
    st.warning("⚠️ Please enter a query before submitting.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>NodeDesk IT Support Assistant | Built with Streamlit and LangGraph</small>
</div>
""", unsafe_allow_html=True)