import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load stop words
stop_words = set(stopwords.words('english'))

# Add common words that aren't useful for product search
additional_stop_words = {'need', 'want', 'looking', 'for', 'with', 'has', 'have', 'a', 'an', 'the', 'and', 'or', 'but'}
stop_words.update(additional_stop_words)

def extract_keywords(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    
    # Remove stop words and non-alphanumeric tokens
    keywords = [word for word in tokens if word not in stop_words and word.isalnum()]
    
    # Combine adjacent numeric values with their units
    combined_keywords = []
    i = 0
    while i < len(keywords):
        if keywords[i].isdigit() and i + 1 < len(keywords):
            combined_keywords.append(keywords[i] + keywords[i+1])
            i += 2
        else:
            combined_keywords.append(keywords[i])
            i += 1
    
    return combined_keywords

if __name__ == "__main__":
    user_input = input("Enter your product search query: ")
    keywords = extract_keywords(user_input)
    print("Extracted keywords:", keywords)