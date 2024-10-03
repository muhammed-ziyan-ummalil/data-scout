from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS  # Import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)

# Download necessary NLTK data at startup
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load environment variables
load_dotenv()

# Initialize Flask app with the correct static and template folders
app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# Enable CORS for the app
CORS(app)

# Create a MongoDB client at the application level
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
client = MongoClient(mongo_uri)
db_name = os.getenv('MONGODB_DB', 'data_scout')
db = client[db_name]

# Cache the stopwords
STOP_WORDS = set(stopwords.words('english'))

# Create a thread pool executor
executor = ThreadPoolExecutor(max_workers=4)

@lru_cache(maxsize=1000)
def process_natural_language(query):
    """Process and cache the user query."""
    tokens = word_tokenize(query.lower())
    keywords = [word for word in tokens if word not in STOP_WORDS and word.isalnum()]
    return keywords

def query_products_mongo(keywords):
    """Optimized MongoDB query using existing text index."""
    products_collection = db['products']
    
    query = {
        "$text": {
            "$search": " ".join(keywords)
        }
    }
    
    projection = {
        'TITLE': 1,
        'PRODUCT_TYPE_ID': 1,
        'prices.asins': 1,
        'overall_rating': 1,
        'score': {'$meta': 'textScore'}
    }
    
    try:
        results = list(products_collection.find(
            query,
            projection
        ).sort([('score', {'$meta': 'textScore'})]).limit(20))
        return results
    except Exception as e:
        logging.error(f"Error querying MongoDB: {e}")
        return []

def format_product(product):
    """Format product details for display."""
    return {
        "name": product.get('TITLE', 'N/A'),
        "categories": product.get('PRODUCT_TYPE_ID', 'N/A'),
        "price": product.get('prices', {}).get('asins', 'N/A'),
        "overall_rating": product.get('overall_rating', 'N/A')
    }

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    user_query = request.form.get('query', '').strip()
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Process and cache the query
    query_info = process_natural_language(user_query)
    
    if not query_info:
        return jsonify({"results": [], "message": "Invalid query"}), 400
    
    # Query MongoDB asynchronously
    future = executor.submit(query_products_mongo, query_info)
    products = future.result()
    
    # Format products asynchronously
    formatted_products = list(executor.map(format_product, products))
    
    response = {
        "results": formatted_products,
        "debug_info": {
            "query": user_query,
            "processed_query": query_info,
            "result_count": len(formatted_products)
        }
    }
    
    return jsonify(response), 200

@app.route('/db-check')
def db_check():
    """Route to check MongoDB connection."""
    try:
        client.server_info()  # Test MongoDB connection
        return "DB connection successful", 200
    except Exception as e:
        return f"Error connecting to DB: {e}", 500

if __name__ == '__main__':
    # Ensure the static/images directory exists
    os.makedirs(os.path.join(app.static_folder, 'images'), exist_ok=True)
    
    # Check for logo file
    logo_path = os.path.join(app.static_folder, 'images', 'logo.png')
    if not os.path.exists(logo_path):
        logging.warning(f"Logo file not found at {logo_path}. Please add a logo image.")
    
    app.run(debug=True)
