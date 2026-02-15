import joblib
import re

# Load trained model
model = joblib.load("model/sentiment_model.pkl")

# Load vectorizer
vectorizer = joblib.load("model/vectorizer.pkl")


def clean_text(text):

    text = re.sub(r"[^A-Za-z]", " ", str(text))
    text = text.lower()

    return text


def predict_sentiment(comment):

    clean = clean_text(comment)

    vector = vectorizer.transform([clean])

    prediction = model.predict(vector)

    return prediction[0]