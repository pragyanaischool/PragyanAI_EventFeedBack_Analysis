import streamlit as st
import os
from data_utils import init_folders

# Initialize the data environment and folder structure
init_folders()

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="PragyanAI Modular Intelligence",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# Global Constants
ADMIN_KEY = "PRAGYANAI"

# Initialize Session States for Authentication and Navigation
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'backend_running' not in st.session_state:
    st.session_state.backend_running = False

# Custom CSS for Premium Branding (Black & White Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { 
        background-color: #000000; 
        color: white; 
    }
    [data-testid="stSidebar"] * { 
        color: white !important; 
    }
    
    /* Button Styling */
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        font-weight: 700; 
        height: 3.5em; 
        background-color: black !important; 
        color: white !important; 
        border: 2px solid #333;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #222 !important;
        border: 2px solid white;
        transform: translateY(-2px);
    }

    /* Header and Text Styling */
    .main-header { 
        font-size: 2.8rem; 
        font-weight: 800; 
        color: #000000; 
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    .sub-header { 
        font-size: 1.2rem;
        color: #555; 
        margin-top: 0px; 
        margin-bottom: 35px;
        font-weight: 400;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #000;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
    }

    /* Card Styling - Optimized for Workshop Details */
    .metric-card { 
        background: #ffffff; 
        padding: 25px; 
        border-radius: 16px; 
        border: 1px solid #eaeaea;
        border-left: 8px solid black; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    
    .metric-card h4 {
        margin-top: 0;
        font-size: 1.6rem;
        font-weight: 800;
    }

    .metric-card p {
        margin: 5px 0;
        font-size: 1rem;
        color: #444;
    }

    /* Input Fields & Text Areas */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #ddd !important;
        padding: 15px !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: black !important;
        box-shadow: 0 0 0 2px rgba(0,0,0,0.1) !important;
    }

    /* Rating Labels Styling */
    .rating-label {
        font-weight: 600;
        color: #222;
        margin-bottom: 5px;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MODULAR ROUTING LOGIC
# ============================================================
def main():
    st.sidebar.title("PragyanAI 🚀")
    st.sidebar.markdown("---")
    
    # Navigation logic based on authentication status
    if not st.session_state.authenticated:
        page = st.sidebar.radio("Navigation", ["Student Access", "Admin Gateway"])
    else:
        # Determine Menu based on assigned role
        role = st.session_state.user.get('role', 'student')
        if role == 'admin':
            page = st.sidebar.radio("Workspace", ["Intelligence Suite", "Event Manager", "Logout"])
        else:
            page = st.sidebar.radio("Workspace", ["Dashboard", "Feedback Center", "Logout"])

    # Logout Procedure
    if page == "Logout":
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.step = 1
        st.rerun()

    # Import modules dynamically to ensure isolated execution
    try:
        from student_portal import render_student_flow
        from admin_intelligence import render_admin_suite
    except ImportError as e:
        st.error(f"Module Loading Error: {e}")
        st.info("Ensure all module files (student_portal.py, admin_intelligence.py, etc.) are in the same directory.")
        return

    # Page Routing
    if page in ["Student Access", "Dashboard", "Feedback Center"]:
        render_student_flow()
    elif page in ["Admin Gateway", "Intelligence Suite", "Event Manager"]:
        render_admin_suite()

    # Footer Branding
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 PragyanAI School of Intelligence")

if __name__ == "__main__":
    main()
    
