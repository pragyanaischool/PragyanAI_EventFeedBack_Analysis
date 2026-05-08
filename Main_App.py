import streamlit as st
import os
from data_utils import init_folders

# Initialize the data environment
init_folders()

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="PragyanAI Student Feedback",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# Global Constants
ADMIN_KEY = "PRAGYANAI"

# Initialize Session States
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'backend_running' not in st.session_state:
    st.session_state.backend_running = False

# Custom CSS for Premium Branding
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #000000; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; height: 3em; background-color: black !important; color: white !important; }
    .main-header { font-size: 2.5rem; font-weight: 800; color: #1a1a1a; margin-bottom: 0; }
    .metric-card { background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid black; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MODULAR ROUTING
# ============================================================
def main():
    st.sidebar.title("PragyanAI 🚀")
    
    if not st.session_state.authenticated:
        page = st.sidebar.radio("Navigation", ["Student Access", "Admin Gateway"])
    else:
        role = st.session_state.user.get('role', 'student')
        if role == 'admin':
            page = st.sidebar.radio("Workspace", ["Intelligence Suite", "Event Manager", "Logout"])
        else:
            page = st.sidebar.radio("Workspace", ["Dashboard", "Feedback Center", "Logout"])

    if page == "Logout":
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.step = 1
        st.rerun()

    # Import modules (Using relative imports for local modularity)
    from student_portal import render_student_flow
    from admin_intelligence import render_admin_suite

    if page in ["Student Access", "Dashboard", "Feedback Center"]:
        render_student_flow()
    elif page in ["Admin Gateway", "Intelligence Suite", "Event Manager"]:
        render_admin_suite()

if __name__ == "__main__":
    main()
    
