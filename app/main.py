from pymongo import MongoClient
from app.extractor import extract_keywords
import os
from dotenv import load_dotenv
import re
from collections import Counter

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    db_name = os.getenv('MONGODB_DB', 'data_scout')
    return client[db_name]

def calculate_relevance_score(product, keywords):
    score = 0
    product_text = ' '.join(str(value) for value in product.values() if isinstance(value, (str, list)))
    
    # Count occurrences of each keyword
    keyword_counts = Counter(keyword.lower() for keyword in keywords)
    
    for keyword, count in keyword_counts.items():
        matches = len(re.findall(re.escape(keyword), product_text, re.IGNORECASE))
        score += matches * count  # Weight by keyword frequency
    
    # Boost score for matches in important fields
    important_fields = ['name', 'brand', 'categories']
    for field in important_fields:
        if field in product:
            for keyword in keywords:
                if re.search(re.escape(keyword), str(product[field]), re.IGNORECASE):
                    score += 2  # Additional points for matching important fields
    
    return score

def query_products_mongo(db, keywords):
    products_collection = db['products']
    
    # Simplified query using regex for keywords
    query = {
        "$or": [
            {field: {"$regex": "|".join(keywords), "$options": "i"}} 
            for field in ['name', 'brand', 'categories', 'keys']
        ]
    }
    
    try:
        results = list(products_collection.find(query).limit(50))  # Increase initial result set
        
        # Calculate relevance score for each product
        for product in results:
            product['relevance_score'] = calculate_relevance_score(product, keywords)
        
        # Sort results by relevance score, descending
        sorted_results = sorted(results, key=lambda x: x['relevance_score'], reverse=True)
        
        return sorted_results[:10]  # Return top 10 results
    except Exception as e:
        print(f"Error querying MongoDB: {e}")
        return []

def format_product(product):
    return (
        f"Product Name: {product.get('name', 'N/A')}\n"
        f"Primary Categories: {product.get('primaryCategories', 'N/A')}\n"
        f"Brand: {product.get('brand', 'N/A')}\n"
        f"Price: {product.get('prices', {}).get('asins', 'N/A')}\n"
        f"Rating: {product.get('overall_rating', 'N/A')}\n"
        f"Relevance Score: {product.get('relevance_score', 0)}\n"
        "========================================="
    )

def main():
    db = connect_to_mongodb()
    print("Welcome to Data Scout - Your Natural Language Product Search Assistant!")
    print("Type 'quit' at any time to exit.")

    while True:
        user_input = input("\nWhat product are you looking for? ").strip()
        if user_input.lower() == 'quit':
            print("Thank you for using Data Scout. Goodbye!")
            break

        keywords = extract_keywords(user_input)
        if not keywords:
            print("I couldn't extract any meaningful keywords. Could you please rephrase your query?")
            continue

        print("Extracted keywords:", keywords)

        products = query_products_mongo(db, keywords)

        if products:
            print(f"\nFound {len(products)} matching products:")
            for product in products:
                print(format_product(product))
        else:
            print("No matching products found. Try different search terms.")

if __name__ == "__main__":
    main()
