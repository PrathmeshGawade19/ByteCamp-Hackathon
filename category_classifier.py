import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load data
df = pd.read_csv("complaints_data.csv")

# Build pipeline
pipe = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression(max_iter=1000))
])

# Train
X_train, X_test, y_train, y_test = train_test_split(df['description'], df['category'], test_size=0.2, random_state=42)
pipe.fit(X_train, y_train)

# Evaluate
y_pred = pipe.predict(X_test)
print(classification_report(y_test, y_pred))

# Save
joblib.dump(pipe, 'category_model.joblib')
