import pandas as pd
import re
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("Loading dataset...")

# Load dataset
data = pd.read_csv("data/sentiment_data.csv", encoding="latin-1")

# Rename columns
data.columns = ["sentiment", "id", "date", "query", "user", "comment"]

# Convert labels
data['sentiment'] = data['sentiment'].replace(4, "positive")
data['sentiment'] = data['sentiment'].replace(0, "negative")

print("Cleaning text...")

# Clean text
def clean_text(text):
    text = re.sub(r"[^A-Za-z]", " ", str(text))
    text = text.lower()
    return text

data['comment'] = data['comment'].apply(clean_text)

# Features and labels
X = data['comment']
y = data['sentiment']

print("Converting text to vectors...")

# Convert text to numbers
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(X)

print("Splitting dataset...")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2
)

print("Training model...")

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

print("Testing model...")

# Test model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)

print("Saving model...")

# Save model
joblib.dump(model, "model/sentiment_model.pkl")
joblib.dump(vectorizer, "model/vectorizer.pkl")

print("Model saved successfully!")