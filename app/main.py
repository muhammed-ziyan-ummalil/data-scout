from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
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
logger = logging.getLogger(__name__)

# Define the path for NLTK data
nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# Download necessary NLTK data at startup
def download_nltk_data():
    try:
        # Download specific NLTK data files
        for resource in ['punkt', 'stopwords']:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                nltk.download(resource, download_dir=nltk_data_path, quiet=True)
        return True
    except Exception as e:
        logger.error(f"Failed to download NLTK data: {e}")
        return False

# Initialize Flask app
app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# Enable CORS
CORS(app)

# Load environment variables
load_dotenv()

# Create MongoDB client
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
client = MongoClient(mongo_uri)
db_name = os.getenv('MONGODB_DB', 'data_scout')
db = client[db_name]

# Initialize thread pool executor
executor = ThreadPoolExecutor(max_workers=4)

# Global variable to track if NLTK data is available
nltk_data_available = download_nltk_data()

# Fallback tokenization function
def simple_tokenize(text):
    """Simple tokenization when NLTK is not available"""
    return [word.lower() for word in text.split() if len(word) > 2]

@lru_cache(maxsize=1000)
def process_natural_language(query):
    """Process and cache the user query."""
    try:
        if nltk_data_available:
            # Use NLTK if available
            tokens = word_tokenize(query.lower())
            stop_words = set(stopwords.words('english'))
            keywords = [word for word in tokens if word not in stop_words and word.isalnum()]
        else:
            # Fallback to simple tokenization
            keywords = simple_tokenize(query)
        
        return keywords if keywords else simple_tokenize(query)
    except Exception as e:
        logger.error(f"Error in query processing: {e}")
        return simple_tokenize(query)

def query_products_mongo(keywords):
    """Query MongoDB with error handling."""
    try:
        products_collection = db['products']
        query = {"$text": {"$search": " ".join(keywords)}}
        projection = {
            'TITLE': 1,
            'PRODUCT_TYPE_ID': 1,
            'prices.asins': 1,
            'overall_rating': 1,
            'score': {'$meta': 'textScore'}
        }
        
        results = list(products_collection.find(
            query,
            projection
        ).sort([('score', {'$meta': 'textScore'})]).limit(20))
        
        return results
    except Exception as e:
        logger.error(f"MongoDB query error: {e}")
        return []

def format_product(product):
    """Format product details with error handling."""
    try:
        return {
            "name": product.get('TITLE', 'N/A'),
            "categories": product.get('PRODUCT_TYPE_ID', 'N/A'),
            "price": product.get('prices', {}).get('asins', 'N/A'),
            "overall_rating": product.get('overall_rating', 'N/A')
        }
    except Exception as e:
        logger.error(f"Error formatting product: {e}")
        return {"name": "Error formatting product", "categories": "N/A", "price": "N/A", "overall_rating": "N/A"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        user_query = request.form.get('query', '').strip()
        
        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        # Process query
        query_info = process_natural_language(user_query)
        
        if not query_info:
            return jsonify({"results": [], "message": "Invalid query"}), 400
        
        # Query MongoDB asynchronously
        future = executor.submit(query_products_mongo, query_info)
        products = future.result()
        
        # Format products
        formatted_products = [format_product(p) for p in products]
        
        response = {
            "results": formatted_products,
            "debug_info": {
                "query": user_query,
                "processed_query": query_info,
                "result_count": len(formatted_products)
            }
        }
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route('/db-check')
def db_check():
    try:
        client.server_info()
        return jsonify({"status": "success", "message": "DB connection successful"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"DB connection failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)