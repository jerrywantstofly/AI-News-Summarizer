from flask import Flask, request, jsonify
import requests
from groq import Groq

app = Flask(__name__)

# API Keys
NEWS_API_KEY = "%%news_api_key%%"  
GROQ_API_KEY = "%%groq_api_key%%" 

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Fetch News Articles
def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200 or "articles" not in data:
        return []

    return data["articles"][:5]  # Limit to top 5 articles

# Summarize Article Using AI
def summarize_article(article_text):
    prompt = f"Summarize this news article:\n{article_text}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150  # Limit summary length
    )

    return response.choices[0].message.content.strip()

# Flask API Route
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    topic = data.get("topic", "Technology")

    articles = fetch_news(topic)
    summarized_articles = []

    for article in articles:
        content = article.get("content") or article.get("description", "")
        if content:
            summary = summarize_article(content)
            summarized_articles.append({
                "title": article["title"],
                "summary": summary,
                "url": article["url"]
            })

    return jsonify({"summaries": summarized_articles})

if __name__ == "__main__":
    app.run(debug=True)
