import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Download necessary NLTK data (only if not already downloaded)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def extract_keywords(text):
    """Extract keywords from the given text using TF-IDF."""
    try:
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        filtered_words = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and word.isalnum()]
        
        if not filtered_words:
            logging.warning("No words remained after filtering. Returning original tokens.")
            return tokens  # Return original tokens if no words remain after filtering
        
        # Use TF-IDF to identify important words
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5)
        tfidf_matrix = vectorizer.fit_transform([" ".join(filtered_words)])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top TF-IDF scores
        tfidf_scores = zip(feature_names, tfidf_matrix.toarray()[0])
        sorted_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
        
        keywords = [word for word, score in sorted_scores if score > 0]
        
        logging.info(f"Extracted keywords: {keywords}")
        return keywords
    except Exception as e:
        logging.error(f"Error in keyword extraction: {str(e)}")
        return []

if __name__ == "__main__":
    user_input = input("Enter your product search query: ")
    keywords = extract_keywords(user_input)
    print("Extracted keywords:", keywords)