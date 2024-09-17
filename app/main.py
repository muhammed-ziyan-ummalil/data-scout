from app.extractor import extract_keywords

def main():
    user_input = input("Enter your product search query: ")
    keywords = extract_keywords(user_input)
    print("Extracted keywords:", keywords)

if __name__ == "__main__":
    main()