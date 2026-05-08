import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import json
import datetime
from data_utils import load_events, save_events, get_feedback_df
from analysis_engine import generate_dynamic_summary, extract_keywords

def render_admin_suite():
    """Main UI for the Admin Intelligence Dashboard."""
    st.markdown('<p class="main-header">Intelligence Suite</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Strategic Monitoring & Workshop Management</p>', unsafe_allow_html=True)
    
    # 1. LIVE SYNC & REFRESH (Every 60 Seconds)
    st_autorefresh(interval=60000, key="admin_sync_timer")
    
    # 2. BACKEND PROCESS CONTROL
    with st.expander("⚙️ Backend Engine Control", expanded=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            if not st.session_state.get('backend_running', False):
                if st.button("▶️ Start Analysis Engine"):
                    st.session_state.backend_running = True
                    st.rerun()
            else:
                if st.button("⏹️ Stop Analysis Engine", type="secondary"):
                    st.session_state.backend_running = False
                    st.rerun()
        with c2:
            status = "RUNNING" if st.session_state.get('backend_running', False) else "IDLE"
            color = "#00c853" if status == "RUNNING" else "#ff1744"
            st.markdown(f"**Engine Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
            st.caption(f"Last Intel Sync: {datetime.datetime.now().strftime('%H:%M:%S')}")

    # 3. EVENT & TRAINER MANAGEMENT
    with st.expander("📅 Workshop & Trainer Manager"):
        st.subheader("Register New Event")
        with st.form("new_event_form"):
            name = st.text_input("Event Name", placeholder="e.g., Advanced Llama 3 Workflows")
            trainer = st.text_input("Trainer Profile")
            location = st.text_input("Location (College/Hub)")
            topics = st.text_area("Key Curriculum Topics (Comma separated)")
            col_d1, col_d2 = st.columns(2)
            sd = col_d1.date_input("Start Date")
            ed = col_d2.date_input("End Date")
            
            if st.form_submit_button("Publish Event to Student Portal"):
                if name and trainer and location:
                    current_events = load_events()
                    current_events[name] = {
                        "trainer": trainer,
                        "location": location,
                        "topics": topics,
                        "start_date": str(sd),
                        "end_date": str(ed),
                        "timestamp": str(datetime.datetime.now())
                    }
                    save_events(current_events)
                    st.success(f"Workshop '{name}' is now active at {location}.")
                else:
                    st.error("Please fill required fields: Name, Trainer, and Location.")

    # 4. DATA ANALYSIS
    df = get_feedback_df()
    if df.empty:
        st.info("Awaiting live feedback streams to generate Intelligence Reports...")
        return

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Feedbacks", len(df))
    m2.metric("Avg Rating", f"{round(df['Rating_Overall'].mean(), 1)}/5")
    m3.metric("Positive Sentiment", len(df[df['Sentiment'] == 'Positive']))
    m4.metric("Media Verified", len(df[df['Media_Captured'] == 'Yes']))

    # Llama-Driven Summary
    st.markdown("### 🤖 Intelligence Auto-Summary")
    st.success(generate_dynamic_summary(df))

    # Analytical Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Sentiment Tracker", "📊 Topic Heatmap", "📂 Data Forge (JSON)"])
    
    with tab1:
        st.subheader("Emotional Distribution")
        fig_pie = px.pie(df, names='Sentiment', color='Sentiment', 
                        color_discrete_map={'Positive':'#000000', 'Neutral':'#cccccc', 'Negative':'#ff4b4b'},
                        hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("Performance Benchmark (by Trainer)")
        t_stats = df.groupby('Trainer')['Rating_Overall'].mean().reset_index()
        fig_bar = px.bar(t_stats, x='Trainer', y='Rating_Overall', color='Rating_Overall', color_continuous_scale='Greys')
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("Mentioned Skills & Interests")
        # Extract keywords using the engine logic
        keywords = extract_keywords(df['Topics'].astype(str))
        if keywords:
            word_df = pd.DataFrame(keywords, columns=['Keyword', 'Frequency'])
            fig_word = px.bar(word_df, x='Keyword', y='Frequency', color='Frequency', color_continuous_scale='Blues')
            st.plotly_chart(fig_word, use_container_width=True)
        else:
            st.write("Insufficient text data for keyword mapping.")

    with tab3:
        st.subheader("Individual Feedback Forge")
        st.write("Select and download specific student records as formatted JSON files.")
        
        selected_idx = st.selectbox("Select Record to Process", df.index, 
                                   format_func=lambda x: f"Record {x}: {df.loc[x, 'Student']} - {df.loc[x, 'Event']}")
        
        record_data = df.loc[selected_idx].to_dict()
        st.json(record_data)
        
        st.download_button(
            label=f"📥 Download Record {selected_idx} (JSON)",
            data=json.dumps(record_data, indent=4),
            file_name=f"student_record_{selected_idx}.json",
            mime="application/json"
        )
        
        st.divider()
        if st.button("Generate Master Database Dump"):
            full_json = df.to_json(orient="records", indent=4)
            st.download_button("📥 Download Full Master JSON", full_json, "master_intelligence_dump.json")

if __name__ == "__main__":
    # For testing independently
    render_admin_suite()
