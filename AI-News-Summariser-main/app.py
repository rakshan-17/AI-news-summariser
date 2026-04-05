
from flask import Flask, request, render_template, flash, redirect, url_for
import nltk
from textblob import TextBlob
from newspaper import Article
from urllib.parse import urlparse
import requests

nltk.download('punkt')

app = Flask(__name__)
app.secret_key = "secret123"


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme and parsed.netloc


def get_website_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        if not is_valid_url(url):
            flash("Please enter a valid URL.")
            return redirect(url_for("index"))

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            requests.get(url, headers=headers, timeout=10)
        except:
            flash("Failed to access the URL.")
            return redirect(url_for("index"))

        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
        except:
            flash("Unable to extract article from this website.")
            return redirect(url_for("index"))

        title = article.title if article.title else "No Title Found"

        authors = ", ".join(article.authors)
        if not authors:
            authors = get_website_name(url)

        publish_date = (
            article.publish_date.strftime("%B %d, %Y")
            if article.publish_date
            else "N/A"
        )

        article_text = article.text.strip()

        if not article_text:
            flash("Article text could not be extracted.")
            return redirect(url_for("index"))

        sentences = article_text.split(". ")
        max_sentences = min(5, len(sentences))
        summary = ". ".join(sentences[:max_sentences]) + "."

        top_image = article.top_image if article.top_image else ""

        analysis = TextBlob(article_text)
        polarity = analysis.sentiment.polarity

        if polarity > 0.2:
            sentiment = "positive 🙂"
        elif polarity < -0.2:
            sentiment = "negative ☹️"
        else:
            sentiment = "neutral 😐"

        return render_template(
            "index.html",
            title=title,
            authors=authors,
            publish_date=publish_date,
            summary=summary,
            top_image=top_image,
            sentiment=sentiment,
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

