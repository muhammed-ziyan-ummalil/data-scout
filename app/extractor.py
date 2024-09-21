import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from transformers import pipeline
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer

# Load environment variables
load_dotenv()

# Hugging Face keyword extraction model
model_name = os.getenv('NER_MODEL', 'dslim/bert-base-NER')
keyword_extractor = pipeline('ner', model=model_name)

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

stop_words = set(stopwords.words('english'))
additional_stop_words = {'need', 'want', 'looking', 'for', 'with', 'has', 'have', 'a', 'an', 'the', 'and', 'or', 'but'}
stop_words.update(additional_stop_words)

def extract_keywords(text):
    # Tokenize and clean text
    tokens = word_tokenize(text.lower())
    filtered_words = [word for word in tokens if word not in stop_words and word.isalnum()]
    
    if not filtered_words:
        return tokens  # Return original tokens if no words remain after filtering
    
    # Use TF-IDF to identify important words
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5)
    tfidf_matrix = vectorizer.fit_transform([" ".join(filtered_words)])
    feature_names = vectorizer.get_feature_names_out()
    
    # Get top TF-IDF scores
    tfidf_scores = zip(feature_names, tfidf_matrix.toarray()[0])
    sorted_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
    
    # Combine TF-IDF keywords with NER results
    ner_keywords = [kw['word'] for kw in keyword_extractor(" ".join(filtered_words))]
    tfidf_keywords = [word for word, score in sorted_scores[:3]]  # Top 3 TF-IDF keywords
    
    combined_keywords = list(set(ner_keywords + tfidf_keywords))
    
    return combined_keywords if combined_keywords else filtered_words

if __name__ == "__main__":
    user_input = input("Enter your product search query: ")
    keywords = extract_keywords(user_input)
    print("Extracted keywords:", keywords)