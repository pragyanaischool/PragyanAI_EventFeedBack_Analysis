import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os
import json

DB_FILE = "unified_knowledge_base.xlsx"

def render_admin_suite():
    st.markdown('<p class="main-header">Intelligence Suite</p>', unsafe_allow_html=True)
    
    # Live Monitoring Refresh
    st_autorefresh(interval=60000, key="admin_sync")

    if not os.path.exists(DB_FILE):
        st.warning("Data stream is currently offline. Awaiting student submissions...")
        return

    df = pd.read_excel(DB_FILE)

    # 1. High Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Live Feedbacks", len(df))
    m2.metric("Satisfaction Score", f"{round(df['Rating_Overall'].mean(), 1)}/5")
    m3.metric("Positive Voice", len(df[df['Sentiment'] == 'Positive']))
    m4.metric("Media Proofs", len(df[df['Media_Captured'] == 'Yes']))

    # 2. Deeper Analysis Tabs
    tab1, tab2, tab3 = st.tabs(["Real-time Analytics", "Sentiment Heatmap", "Data Forge (JSON Export)"])
    
    with tab1:
        st.subheader("Trainer Performance Benchmarking")
        trainer_perf = df.groupby('Trainer')['Rating_Overall'].mean().reset_index()
        fig = px.bar(trainer_perf, x='Trainer', y='Rating_Overall', color='Rating_Overall', 
                     color_continuous_scale='Greys', title="Avg Rating per Trainer")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Topic Extraction & Emotion Analysis")
        # Simulate Keyword extraction from 'Topics' column
        all_topics = " ".join(df['Topics'].astype(str)).split()
        if all_topics:
            topic_counts = pd.Series(all_topics).value_counts().head(10)
            st.write("Top Mastered Keywords:")
            st.bar_chart(topic_counts)
        
        fig2 = px.scatter(df, x='Timestamp', y='Rating_Overall', color='Sentiment', 
                         size='Rating_Content', title="Sentiment Over Time (Bubble Chart)")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("System Data Dump")
        st.info("This module packages all student responses, transcripts, and metadata into a local JSON archive.")
        
        json_dump = df.to_json(orient="records", indent=4)
        
        st.download_button(
            label="Download Complete Intelligence Dump (JSON)",
            data=json_dump,
            file_name="pragyan_intelligence_forge.json",
            mime="application/json"
        )
        st.code(json_dump[:500] + "...", language="json")
