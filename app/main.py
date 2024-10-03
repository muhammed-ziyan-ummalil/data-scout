from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from app.extractor import extract_keywords
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load environment variables
load_dotenv()

app = Flask(__name__)

def connect_to_mongodb():
    """Connect to MongoDB using the environment variables."""
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    db_name = os.getenv('MONGODB_DB', 'data_scout')
    return client[db_name]

def process_natural_language(query):
    """Process the user query dynamically."""
    tokens = word_tokenize(query.lower())
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word not in stop_words and word.isalnum()]
    
    logging.debug(f"Processed keywords: {keywords}")
    return keywords

def query_products_mongo(db, query_info):
    """Query MongoDB for products based on the dynamically processed query information."""
    products_collection = db['products']
    
    query = {"$text": {"$search": " ".join(query_info)}}
    
    logging.debug(f"MongoDB query: {query}")
    
    try:
        results = list(products_collection.find(query, {'score': {'$meta': 'textScore'}})
                       .sort([('score', {'$meta': 'textScore'})])
                       .limit(20))
        logging.debug(f"Query results count: {len(results)}")
        return results
    except Exception as e:
        logging.error(f"Error querying MongoDB: {e}")
        return []

def format_product(product):
    """Format product details for display."""
    formatted = {
        "name": product.get('TITLE', 'N/A'),
        "categories": product.get('PRODUCT_TYPE_ID', 'N/A'),
        "brand": product.get('brand', 'N/A'),
        "prices": product.get('prices', {}).get('asins', 'N/A'),
        "overall_rating": product.get('overall_rating', 'N/A'),
        "score": product.get('score', 0),
        "image_url": product.get('image', '/static/placeholder.png')
    }
    logging.debug(f"Formatted product: {formatted}")
    return formatted

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle natural language search queries and return product results."""
    user_query = request.form.get('query', '')
    logging.info(f"Received search query: {user_query}")
    
    if not user_query:
        logging.warning("No query received.")
        return jsonify({"error": "No query provided"}), 400

    db = connect_to_mongodb()
    
    # Process the natural language query
    query_info = process_natural_language(user_query)
    logging.info(f"Processed query info: {query_info}")
    
    # Query the MongoDB to get relevant products
    products = query_products_mongo(db, query_info)
    formatted_products = [format_product(product) for product in products]
    
    if not formatted_products:
        logging.info("No products found.")
        return jsonify({"results": [], "message": "No products found"}), 404
    
    response = {
        "results": formatted_products,
        "debug_info": {
            "query": user_query,
            "processed_query": query_info,
            "result_count": len(formatted_products)
        }
    }
    
    logging.info(f"Sending response: {response}")
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
