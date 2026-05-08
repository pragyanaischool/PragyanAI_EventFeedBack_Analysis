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
        border-radius: 20px; 
        font-weight: bold; 
        height: 3em; 
        background-color: black !important; 
        color: white !important; 
        border: 1px solid white;
    }
    .stButton>button:hover {
        background-color: #333333 !important;
        border: 1px solid #555555;
    }

    /* Header and Text Styling */
    .main-header { 
        font-size: 2.5rem; 
        font-weight: 800; 
        color: #1a1a1a; 
        margin-bottom: 0; 
    }
    .sub-header { 
        color: #666; 
        margin-top: -10px; 
        margin-bottom: 30px; 
    }
    
    /* Card Styling */
    .metric-card { 
        background: #f8f9fa; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid black; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Input Fields */
    input, textarea {
        border-radius: 10px !important;
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
    # These imports reference the files in the same directory/src
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
