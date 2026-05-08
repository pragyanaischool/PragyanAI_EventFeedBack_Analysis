import streamlit as st
import os

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="PragyanAI Student FeedBack Portal",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# Global Constants
DB_FILE = "unified_knowledge_base.xlsx"
ADMIN_KEY = "PRAGYANAI"

# Initialize Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Custom CSS for Premium Branding
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #000000; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    .main-header { font-size: 2.5rem; font-weight: 800; color: #1a1a1a; margin-bottom: 0; }
    .sub-header { color: #666; margin-top: -10px; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MODULAR ROUTING
# ============================================================
def main():
    st.sidebar.title("PragyanAI - Student Feedback")
    
    if not st.session_state.authenticated:
        page = st.sidebar.radio("Navigation", ["Student Access", "Admin Gateway"])
    else:
        page = st.sidebar.radio("Workspace", ["Dashboard", "Feedback Center", "Intelligence Suite", "Logout"])

    if page == "Logout":
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    # Import modules dynamically to simulate file separation
    from student_portal import render_student_flow
    from admin_intelligence import render_admin_suite

    if "Student" in page or "Feedback" in page or "Dashboard" in page:
        render_student_flow()
    elif "Admin" in page or "Intelligence" in page:
        render_admin_suite()

if __name__ == "__main__":
    main()
