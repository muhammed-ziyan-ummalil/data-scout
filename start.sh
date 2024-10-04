#!/bin/bash

echo "Starting application setup..."

# Create directory for NLTK data
NLTK_DATA_DIR="./nltk_data"
echo "Creating NLTK data directory at $NLTK_DATA_DIR"
mkdir -p $NLTK_DATA_DIR

# Download NLTK data
echo "Downloading NLTK data..."
python -c "
import nltk
import os
nltk.data.path.append('$NLTK_DATA_DIR')
for package in ['punkt', 'stopwords']:
    try:
        nltk.data.find(f'tokenizers/{package}')
        print(f'{package} already downloaded')
    except LookupError:
        print(f'Downloading {package}...')
        nltk.download(package, download_dir='$NLTK_DATA_DIR')
"

# Verify MongoDB connection
echo "Verifying MongoDB connection..."
python -c "
from pymongo import MongoClient
import os
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
client = MongoClient(mongo_uri)
try:
    client.server_info()
    print('MongoDB connection successful')
    db = client[os.getenv('MONGODB_DB', 'data_scout')]
    count = db.products.count_documents({})
    print(f'Found {count} documents in products collection')
except Exception as e:
    print(f'MongoDB connection failed: {e}')
"

# Start the application
echo "Starting Gunicorn..."
gunicorn app.main:app --bind 0.0.0.0:10000 --log-level debug