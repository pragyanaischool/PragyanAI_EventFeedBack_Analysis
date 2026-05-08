import streamlit as st
import os

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
DB_FILE = "data/unified_knowledge_base.xlsx"
ADMIN_KEY = "PRAGYANAI"

# Initialize Session State
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
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; height: 3em; }
    .main-header { font-size: 2.5rem; font-weight: 800; color: #1a1a1a; margin-bottom: 0; }
    .sub-header { color: #666; margin-top: -10px; margin-bottom: 30px; }
    .metric-card { background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid black; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MODULAR ROUTING
# ============================================================
def main():
    st.sidebar.title("PragyanAI Student")
    
    if not st.session_state.authenticated:
        page = st.sidebar.radio("Navigation", ["Student Access", "Admin Gateway"])
    else:
        page = st.sidebar.radio("Workspace", ["Dashboard", "Feedback Center", "Intelligence Suite", "Logout"])

    if page == "Logout":
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    # Import modules (Using relative imports for local modularity)
    try:
        from student_portal import render_student_flow
        from admin_intelligence import render_admin_suite
    except ImportError:
        st.error("Module files (student_portal.py or admin_intelligence.py) missing!")
        return

    if "Student" in page or "Feedback" in page or "Dashboard" in page:
        render_student_flow()
    elif "Admin" in page or "Intelligence" in page:
        render_admin_suite()

if __name__ == "__main__":
    main()
