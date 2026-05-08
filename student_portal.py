import streamlit as st
import datetime
import base64
from data_utils import load_events, save_feedback_entry
from analysis_engine import perform_sentiment_analysis, run_deep_ai_analysis, analyze_image_with_feedback

def render_student_flow():
    """Main UI for the Student Portal including account handling and multi-stage feedback."""
    
    # 1. AUTHENTICATION / PROFILE GATE
    if not st.session_state.authenticated:
        st.markdown('<p class="main-header">Student Access Portal</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Login to Dashboard"):
                if u and p:
                    # Logic for demo; in production verify against a user DB
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "name": u, 
                        "role": "student", 
                        "usn": "1GN21CS001",
                        "college": "GNDEC, Bidar"
                    }
                    st.rerun()
                else:
                    st.error("Credentials required.")
        with col2:
            st.info("Log in to view your scheduled workshops and submit deep intelligence feedback.")
        return

    # 2. STUDENT DASHBOARD
    st.markdown(f'<p class="main-header">Welcome, {st.session_state.user["name"]}</p>', unsafe_allow_html=True)
    
    events = load_events()
    if not events:
        st.warning("No active workshops are currently scheduled by the administration.")
        return

    selected_event_name = st.selectbox("Select Workshop to Review", list(events.keys()))
    evt = events[selected_event_name]

    # Display Rich Event Context
    st.markdown(f"""
    <div class="metric-card">
        <h4>📍 {selected_event_name}</h4>
        <p><b>Venue:</b> {evt.get('location', 'Main Campus')}</p>
        <p><b>Date Range:</b> {evt.get('start_date')} to {evt.get('end_date')}</p>
        <p><b>Trainer:</b> {evt.get('trainer')} | <b>Key Topics:</b> {evt.get('topics')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. TWO-PHASE FEEDBACK SYSTEM
    
    # PHASE 1: Quantitative & Topics
    if st.session_state.step == 1:
        with st.form("phase_1_feedback"):
            st.subheader("Phase 1: Performance & Learning Evaluation")
            c1, c2, c3 = st.columns(3)
            r_ovr = c1.feedback("stars", key="rate_ovr")
            st.caption("Overall Experience")
            r_tch = c2.feedback("stars", key="rate_tch")
            st.caption("Teaching Quality")
            r_hnd = c3.feedback("stars", key="rate_hnd")
            st.caption("Hands-on / Practical")
            
            topics_mastered = st.text_area("What specific concepts or skills did you master today?")
            liked_most = st.text_input("What was the absolute highlight of this session?")
            
            if st.form_submit_button("Proceed to Deep Analysis"):
                if r_ovr is None or not topics_mastered:
                    st.error("Please provide an overall rating and describe the topics mastered.")
                else:
                    st.session_state.temp_feedback = {
                        "ovr": r_ovr + 1, 
                        "tch": (r_tch or 0) + 1, 
                        "hnd": (r_hnd or 0) + 1,
                        "topics": topics_mastered, 
                        "liked": liked_most, 
                        "event": selected_event_name, 
                        "trainer": evt.get('trainer')
                    }
                    st.session_state.step = 2
                    st.rerun()
    
    # PHASE 2: Vision, Voice, and Llama Narrative
    else:
        st.subheader("Phase 2: Deep Feedback & Proof of Learning")
        if st.button("← Modify Ratings"):
            st.session_state.step = 1
            st.rerun()
            
        img = st.camera_input("Capture Evidence (Selfie or Work Output)")
        audio = st.audio_input("Record Voice Reflection (Your feedback in your own words)")
        narrative_txt = st.text_area("Deep Narrative: Describe your learning journey and trainer impact.")
        
        if st.button("Finalize and Sync Intelligence Report"):
            with st.spinner("Llama Engine Analyzing Feedback..."):
                # 1. Sentiment & Polarity
                sentiment_label, polarity_score = perform_sentiment_analysis(narrative_txt)
                
                # 2. Deep AI Narrative Summary
                ai_report = run_deep_ai_analysis(narrative_txt, metadata=f"Event: {selected_event_name}")
                
                # 3. Vision Analysis
                vision_status = "N/A"
                if img:
                    try:
                        img_b64 = base64.b64encode(img.getvalue()).decode('utf-8')
                        vision_status = analyze_image_with_feedback(img_b64, narrative_txt)
                    except Exception:
                        vision_status = "Vision engine processing error."

                # 4. Package Record
                record = {
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Student": st.session_state.user['name'],
                    "USN": st.session_state.user['usn'],
                    "College": st.session_state.user['college'],
                    "Event": selected_event_name,
                    "Trainer": evt.get('trainer'),
                    "Rating_Overall": st.session_state.temp_feedback['ovr'],
                    "Rating_Content": st.session_state.temp_feedback['tch'],
                    "Rating_HandsOn": st.session_state.temp_feedback['hnd'],
                    "Topics": st.session_state.temp_feedback['topics'],
                    "Liked": st.session_state.temp_feedback['liked'],
                    "Sentiment": sentiment_label,
                    "Detailed_Transcript": narrative_txt,
                    "AI_Summary": ai_report,
                    "Vision_Verification": vision_status,
                    "Media_Captured": "Yes" if img else "No"
                }
                
                # 5. Save to Knowledge Base
                save_feedback_entry(record)
                
                st.success("✅ Deep Intelligence Report successfully synced to Admin Suite!")
                
                # Viral Loop & Good Rating Redirect
                if record['Rating_Overall'] >= 4:
                    st.balloons()
                    st.markdown("### 🌟 Exceptional Learning Detected!")
                    st.info("Your feedback is helping us grow. Would you mind sharing this on our Google Business page?")
                    st.link_button("Write Review on Google", "https://g.page/r/your-google-business-id/review")
                
                # Reset
                st.session_state.step = 1
                if st.button("Submit Another"):
                    st.rerun()

if __name__ == "__main__":
    # Ensure session state for standalone testing
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False
    if 'step' not in st.session_state: st.session_state.step = 1
    render_student_flow()
    
