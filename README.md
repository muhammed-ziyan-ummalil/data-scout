# Data Scout

Data Scout is a Natural Language to SQL chatbot designed to convert user queries into SQL, execute them on a database, and return relevant search results. It can be easily integrated into any website and offers a conversational interface for users to interact with databases using plain language.

## Features

- **Natural Language Processing**: Understands user queries in plain language.
- **SQL Query Generation**: Converts natural language queries into accurate SQL commands.
- **Database Integration**: Executes SQL queries on a connected database.
- **Conversational Interface**: Chatbot-style interaction that can be embedded into websites.
- **Customizable**: Adaptable to various types of databases and website platforms.

## Getting Started

### Prerequisites

Before you start, ensure you have the following installed:

- Python (version 3.8 or higher)
- Flask for backend development
- spaCy or another NLP library
- A SQL database (e.g., MySQL, PostgreSQL)

### Installation

1. Clone the repository:


   git clone https://github.com/muhammed-ziyan-ummalil/data-scout
   cd data-scout


2. Install the necessary dependencies:


   pip install -r requirements.txt


3. Set up your database and update the connection details in the configuration file (`main/config.py`).

### Usage

1. Start the Flask server:


   python main/data_scout.py


2. Open your browser and navigate to `http://localhost:5000`.

3. Interact with the chatbot by entering natural language queries (e.g., "Find a phone with a 5000mAh battery and red color").

### Example Queries

- "Show me laptops with 16GB RAM."
- "I need a phone with a 64MP camera."
- "Find me a blue shirt in size medium."

## Project Structure

- **`main/data_scout.py`** - Main script to run the application.
- **`main/config.py`** - Configuration settings for the application.
- **`main/database.py`** - Database connection and query handling.
- **`main/nlp.py`** - NLP processing and query understanding.
- **`requirements.txt`** - List of dependencies required to run Data Scout.

## Future Enhancements

- **Support for complex queries**: Improve the NLP model to handle more sophisticated natural language queries.
- **Contextual understanding**: Enable the chatbot to maintain conversation context for follow-up questions.
- **Support for multiple databases**: Extend compatibility with different types of databases.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repo.
2. Create a new branch: `git checkout -b feature-name`.
3. Make and commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any inquiries, feel free to reach out:

- **Email**: mziyan777.mz@gmail.com
- **GitHub**: [github.com/muhammed-ziyan-ummalil](https://github.com/muhammed-ziyan-ummalil)
