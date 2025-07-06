# train_category_model.py
import os
import django
import joblib
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "civic_saathi.settings")
django.setup()

# Import your models
from core.models import Complaint

# Load data from DB
complaints = Complaint.objects.all().values('description', 'category__name')
data = pd.DataFrame(list(complaints)).dropna()

# Check data
if data.empty:
    print("No data found in DB to train on!")
    exit()

X = data['description']
y = data['category__name']

# Create pipeline & train
model = make_pipeline(
    TfidfVectorizer(),
    MultinomialNB()
)
model.fit(X, y)

# Save model
joblib.dump(model, "category_model.pkl")
print("✅ Model trained and saved as 'category_model.pkl'")
