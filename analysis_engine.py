import pandas as pd
from textblob import TextBlob
import collections
import re
import time
import json
import base64
import requests
import streamlit as st

# API Configuration
# Retrieving the key securely from Streamlit Secrets
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "") 
MODEL_TEXT = "llama-3.3-70b-versatile"
MODEL_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"

def call_groq_llama_api(prompt, system_instruction="You are an AI analyst.", is_vision=False, image_base64=None):
    """
    Calls the Groq API using Llama 3 models with exponential backoff.
    Handles both standard text completion and multimodal vision tasks.
    """
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in Streamlit secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Construct messages based on whether it's a vision or text task
    if is_vision and image_base64:
        messages = [
            {"role": "system", "content": system_instruction},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                    }
                ]
            }
        ]
        model = MODEL_VISION
    else:
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
        model = MODEL_TEXT

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1024
    }

    # Exponential backoff: 1s, 2s, 4s, 8s, 16s
    for i in range(5):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            elif response.status_code == 429: # Rate limit
                pass
        except Exception:
            pass
        time.sleep(2**i)
    
    return "Deep Analysis Error: Connection timeout or API limit reached."

def perform_sentiment_analysis(text):
    """Analyzes text and returns a label and polarity score using local TextBlob."""
    if not text or pd.isna(text):
        return "Neutral", 0.0
    
    analysis = TextBlob(str(text))
    polarity = analysis.sentiment.polarity
    
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity

def extract_keywords(text_series, top_n=15):
    """Extracts frequent words for Bar Charts and Word Cloud data."""
    words = []
    stop_words = {
        'the', 'and', 'was', 'were', 'for', 'with', 'this', 'that', 'session', 
        'workshop', 'event', 'very', 'good', 'great', 'really', 'also', 'from',
        'teaching', 'content', 'topic', 'topics', 'learned', 'learning'
    }
    
    for text in text_series:
        if pd.notna(text):
            clean_text = re.sub(r'[^\w\s]', '', str(text).lower())
            words.extend([w for w in clean_text.split() if w not in stop_words and len(w) > 3])
    
    return collections.Counter(words).most_common(top_n)

def analyze_narrative_feedback(transcript):
    """Uses Llama 3 via Groq to extract specific Pros and Cons."""
    prompt = (
        "Analyze this student feedback. "
        "Extract specific things they LIKED and things they DID NOT LIKE/CHALLENGES. "
        "Format your response as:\n"
        "LIKES: [bullet points]\n"
        "DISLIKES: [bullet points]\n\n"
        f"Feedback: {transcript}"
    )
    return call_groq_llama_api(prompt, "You are a specialized feedback analyst.")

def get_rating_intelligence(df):
    """Calculates detailed breakdown of all rating categories."""
    metrics = {
        "Overall": df['Rating_Overall'].mean() if 'Rating_Overall' in df.columns else 0,
        "Teaching": df['Rating_Content'].mean() if 'Rating_Content' in df.columns else 0,
        "Hands-on": df['Rating_HandsOn'].mean() if 'Rating_HandsOn' in df.columns else 0
    }
    return metrics

def run_deep_ai_analysis(transcript, metadata=None):
    """Provides Llama-driven high-level summary and intent analysis."""
    prompt = f"Summarize the following feedback in 2 sentences, identifying the student's primary outcome: \n\n {transcript}"
    if metadata:
        prompt += f"\nContext: {metadata}"
        
    return call_groq_llama_api(prompt, "You are a professional educational consultant.")

def generate_dynamic_summary(df):
    """Generates a text summary with granular rating and sentiment insights."""
    if df.empty:
        return "System is ready. Awaiting data streams..."
    
    total = len(df)
    ratings = get_rating_intelligence(df)
    sentiment_counts = df['Sentiment'].value_counts().to_dict()
    pos_percent = (sentiment_counts.get('Positive', 0) / total) * 100 if total > 0 else 0
    
    top_liked = ""
    if 'Liked' in df.columns:
        keywords = extract_keywords(df['Liked'], top_n=1)
        if keywords:
            top_liked = f"Key highlight identified: **'{keywords[0][0]}'**."

    summary = f"**Llama-Powered Intelligence Summary:**\n\n"
    summary += f"- **Database Health:** {total} records analyzed.\n"
    summary += f"- **Ratings Scorecard:** Overall: **{ratings['Overall']:.1f}/5** | Teaching: **{ratings['Teaching']:.1f}/5** | Hands-on: **{ratings['Hands-on']:.1f}/5**.\n"
    summary += f"- **Sentiment Engine:** {pos_percent:.1f}% positive feedback loop. {top_liked}\n"
    
    if 'Trainer' in df.columns and not df['Trainer'].empty:
        top_trainer = df.groupby('Trainer')['Rating_Overall'].mean().idxmax()
        summary += f"- **Top Performer:** {top_trainer} leads in satisfaction."
        
    return summary

def analyze_image_with_feedback(base64_image, transcript):
    """Multimodal analysis using Llama 3.2 Vision via Groq."""
    prompt = f"Verify if this image provides evidence for the following claim: '{transcript}'"
    return call_groq_llama_api(prompt, "You are a vision analysis agent.", is_vision=True, image_base64=base64_image)
