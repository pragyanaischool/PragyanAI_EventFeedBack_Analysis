import pandas as pd
from textblob import TextBlob
import collections
import re

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

def extract_keywords(text_series, top_n=10):
    """Extracts the most frequent words from a series of text data."""
    words = []
    for text in text_series:
        if pd.notna(text):
            # Clean and tokenize
            clean_text = re.sub(r'[^\w\s]', '', str(text).lower())
            words.extend(clean_text.split())
    
    # Filter common stop words (simplified)
    stop_words = {'the', 'and', 'was', 'were', 'for', 'with', 'this', 'that', 'session', 'workshop', 'event'}
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    return collections.Counter(filtered_words).most_common(top_n)

def generate_dynamic_summary(df):
    """Generates a text summary of the current dataset insights."""
    if df.empty:
        return "System is ready. Awaiting student input."
    
    total = len(df)
    avg_rating = df['Rating_Overall'].mean()
    sentiment_counts = df['Sentiment'].value_counts().to_dict()
    pos_percent = (sentiment_counts.get('Positive', 0) / total) * 100
    
    summary = f"**Project Intelligence Summary:**\n\n"
    summary += f"- **Engagement:** Total of {total} feedback records processed.\n"
    summary += f"- **Satisfaction:** The average overall rating is **{avg_rating:.2f}/5**.\n"
    summary += f"- **Sentiment:** {pos_percent:.1f}% of students reported a positive experience.\n"
    
    if 'Trainer' in df.columns:
        top_trainer = df.groupby('Trainer')['Rating_Overall'].mean().idxmax()
        summary += f"- **Top Performer:** {top_trainer} is currently the highest-rated trainer.\n"
        
    return summary
