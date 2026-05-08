import pandas as pd
from textblob import TextBlob
import collections
import re
import time
import json
import base64
import requests
import streamlit as st

# Secure API Configuration from Streamlit Secrets
# Ensure you have "GROQ_API_KEY" set in your .streamlit/secrets.toml
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "") 
MODEL_TEXT = "llama-3.3-70b-versatile"
MODEL_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"

def call_groq_llama_api(prompt, system_instruction="You are an AI analyst.", is_vision=False, image_base64=None):
    """
    Calls the Groq API using Llama 3 models with exponential backoff.
    Handles both standard text completion and multimodal vision tasks.
    """
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY missing in Streamlit secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

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

    # Exponential backoff (1s, 2s, 4s, 8s, 16s)
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
    
    return "Analysis Error: API Connection timeout or limit reached."

def perform_sentiment_analysis(text):
    """Analyzes text and returns a label and polarity score."""
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
    # Stop words to filter out common educational/filler terms
    stop_words = {
        'the', 'and', 'was', 'were', 'for', 'with', 'this', 'that', 'session', 
        'workshop', 'event', 'very', 'good', 'great', 'really', 'also', 'from',
        'teaching', 'content', 'topic', 'topics', 'learned', 'learning'
    }
    
    for text in text_series:
        if pd.notna(text):
            # Clean and tokenize
            clean_text = re.sub(r'[^\w\s]', '', str(text).lower())
            words.extend([w for w in clean_text.split() if w not in stop_words and len(w) > 3])
    
    return collections.Counter(words).most_common(top_n)

def analyze_narrative_feedback(transcript):
    """Uses Llama 3 via Groq to extract specific Pros and Cons from a transcript."""
    prompt = (
        "Analyze this student feedback. "
        "Extract specific things they LIKED and things they DID NOT LIKE or found CHALLENGING. "
        "Format your response as:\n"
        "LIKES: [bullet points]\n"
        "DISLIKES: [bullet points]\n\n"
        f"Feedback: {transcript}"
    )
    return call_groq_llama_api(prompt, "You are a specialized feedback analyst.")

def generate_dynamic_summary(df):
    """Generates a text summary with granular rating and sentiment insights."""
    if df.empty:
        return "System is ready. Awaiting data streams..."
    
    total = len(df)
    avg_rating = df['Rating_Overall'].mean() if 'Rating_Overall' in df.columns else 0
    sentiment_counts = df['Sentiment'].value_counts().to_dict()
    pos_percent = (sentiment_counts.get('Positive', 0) / total) * 100 if total > 0 else 0
    
    summary = f"**Llama-Powered Intelligence Summary:**\n\n"
    summary += f"- **Processed:** {total} feedback records.\n"
    summary += f"- **Satisfaction Score:** **{avg_rating:.1f}/5 Stars**.\n"
    summary += f"- **Sentiment Engine:** {pos_percent:.1f}% positive feedback loop detected.\n"
    
    if 'Trainer' in df.columns and not df['Trainer'].empty:
        top_trainer = df.groupby('Trainer')['Rating_Overall'].mean().idxmax()
        summary += f"- **Star Performer:** {top_trainer} is leading in student satisfaction."
        
    return summary

def analyze_image_with_feedback(base64_image, transcript):
    """Multimodal analysis using Llama 3.2 Vision via Groq."""
    prompt = f"Verify if this image provides evidence for the following claim: '{transcript}'"
    return call_groq_llama_api(prompt, "You are a vision analysis agent.", is_vision=True, image_base64=base64_image)
    
