import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os
import json
import datetime

# Configuration Paths
DB_FILE = "data/unified_knowledge_base.xlsx"
EVENTS_FILE = "data/events.json"

def load_events():
    """Loads event data from a JSON file or returns defaults."""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    return {
        "Multi-Agent AI Systems": {"trainer": "Sateesh A.", "topics": "RAG, AutoGen, CrewAI"},
        "Edge Intelligence": {"trainer": "Priya K.", "topics": "ESP32, MicroPython, MQTT"}
    }

def save_events(events_dict):
    """Saves updated event/trainer profiles to the JSON file."""
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(EVENTS_FILE, "w") as f:
        json.dump(events_dict, f, indent=4)

def generate_summary(df):
    """AI-driven summary of current student feedback."""
    if df.empty: return "Waiting for data streams..."
    pos_rate = round((len(df[df['Sentiment'] == 'Positive']) / len(df)) * 100)
    avg_r = round(df['Rating_Overall'].mean(), 1)
    top_trainer = df.groupby('Trainer')['Rating_Overall'].mean().idxmax()
    
    summary = f"Program Health: **{avg_r}/5 Stars**. "
    summary += f"Sentiment Analysis shows **{pos_rate}% Positive** engagement. "
    summary += f"Top performing module is currently led by **{top_trainer}**."
    return summary

def render_admin_suite():
    st.markdown('<p class="main-header">Intelligence Suite</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Live Engine Monitor & Strategic Analytics</p>', unsafe_allow_html=True)
    
    # 1. LIVE SYNC & PROCESS CONTROL
    st_autorefresh(interval=60000, key="admin_refresh_timer")
    
    with st.expander("⚙️ System Control & Backend Engine", expanded=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            if not st.session_state.get('backend_running', False):
                if st.button("▶️ Start Backend Engine"):
                    st.session_state.backend_running = True
                    st.rerun()
            else:
                if st.button("⏹️ Stop Backend Engine", type="secondary"):
                    st.session_state.backend_running = False
                    st.rerun()
        with c2:
            status = "ACTIVE" if st.session_state.get('backend_running', False) else "IDLE"
            color = "green" if status == "ACTIVE" else "red"
            st.markdown(f"**Engine Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
            st.caption(f"Last Intelligence Sync: {datetime.datetime.now().strftime('%H:%M:%S')}")

    # 2. EVENT & TRAINER MANAGEMENT
    with st.expander("➕ Event Manager (Add Workshops & Trainers)"):
        st.subheader("Configure New Workshop")
        with st.form("add_event_form"):
            e_name = st.text_input("Event Name", placeholder="e.g., Quantum Computing Basics")
            t_name = st.text_input("Trainer Profile Name")
            t_topics = st.text_area("Curriculum / Topics Covered (Comma separated)")
            if st.form_submit_button("Deploy Event to Portal"):
                if e_name and t_name:
                    current_events = load_events()
                    current_events[e_name] = {"trainer": t_name, "topics": t_topics}
                    save_events(current_events)
                    st.success(f"Event '{e_name}' is now live on the Student Portal!")
                else:
                    st.error("Event Name and Trainer are required.")

    if not os.path.exists(DB_FILE):
        st.info("Awaiting initial feedback submissions to populate Analytics...")
        return

    # 3. CORE ANALYTICS
    df = pd.read_excel(DB_FILE)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Reviews", len(df))
    m2.metric("Satisfaction", f"{round(df['Rating_Overall'].mean(), 1)}/5")
    m3.metric("Positive Sentiment", f"{len(df[df['Sentiment'] == 'Positive'])}")
    m4.metric("Media Proofs", len(df[df['Media_Captured'] == 'Yes']))

    # Intelligence Summary
    st.markdown("### 🤖 Automated Intelligence Report")
    st.success(generate_summary(df))

    # TABS
    tab1, tab2, tab3 = st.tabs(["📈 Sentiment Tracker", "👨‍🏫 Trainer Rankings", "📂 Data Forge (JSON)"])
    
    with tab1:
        st.subheader("Live Sentiment Distribution")
        fig_pie = px.pie(df, names='Sentiment', color='Sentiment', 
                       color_discrete_map={'Positive':'#000000', 'Neutral':'#cccccc', 'Negative':'#ff4b4b'},
                       hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("Rating Timeline")
        fig_line = px.line(df, x='Timestamp', y='Rating_Overall', color='Event', title="Quality Consistency per Event")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("Trainer Performance Benchmarks")
        trainer_stats = df.groupby('Trainer').agg({
            'Rating_Overall': 'mean',
            'Rating_Content': 'mean',
            'Rating_HandsOn': 'mean'
        }).reset_index()
        st.dataframe(trainer_stats.style.highlight_max(axis=0, color='lightgrey'))
        
        fig_bar = px.bar(trainer_stats, x='Trainer', y=['Rating_Overall', 'Rating_Content'], 
                        barmode='group', title="Trainer Rating Comparison")
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("Individual Record Processing (One-by-One)")
        st.info("Select a specific student record to analyze deep metadata or download as an individual JSON forge.")
        
        record_id = st.selectbox("Select Student Record", df.index, 
                                format_func=lambda x: f"Record {x}: {df.loc[x, 'Student']} ({df.loc[x, 'Event']})")
        
        selected_data = df.loc[record_id].to_dict()
        st.json(selected_data)
        
        st.download_button(
            label=f"📥 Download Record {record_id} (JSON)",
            data=json.dumps(selected_data, indent=4),
            file_name=f"student_analysis_{record_id}.json",
            mime="application/json"
        )
        
        st.divider()
        if st.button("Generate Master Knowledge Dump"):
            full_dump = df.to_json(orient="records", indent=4)
            st.download_button("📥 Download Full Master JSON", full_dump, "master_intelligence_dump.json")

if __name__ == "__main__":
    # This block allows the file to be tested independently if needed
    render_admin_suite()
  
