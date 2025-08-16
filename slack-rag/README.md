# Slack RAG Chatbot

This project is a Slack chatbot designed to assist users with inquiries related to various medical braces, specifically focusing on products such as Adonis, Ascender, Hermes, and Zeus. The chatbot utilizes a structured knowledge base to provide accurate and relevant answers to user questions.

## Project Structure

- **src/**: Contains the main application code.
  - **app.py**: The entry point for the Slack chatbot, responsible for initializing the bot and handling incoming messages.
  - **types/**: Contains type definitions and classes for type safety and clarity.

- **data/**: The knowledge base for the chatbot, organized by product.
  - **adonis/**: Information specific to the Adonis product, including intents, synonyms, and triggers.
  - **ascender/**: Information specific to the Ascender product, including intents, synonyms, and triggers.
  - **hermes/**: Information specific to the Hermes product, including intents, synonyms, and triggers.
  - **zeus/**: Information specific to the Zeus product, including intents, synonyms, and triggers.
  - **shared/**: Contains shared resources such as product and intent aliases.
  - **patterns/**: Contains files for pattern matching and normalization of user input.
  - **paraphrases/**: Contains paraphrase files for each product to improve question recognition.
  - **schemas/**: Contains JSON schema files for validating intents and products.

- **requirements.txt**: Lists the Python dependencies required for the project.

## Improving Question Matching

To enhance the chatbot's ability to match questions to the corresponding product and handle various question formats, consider the following strategies:

1. **Expand Synonyms and Triggers**: Ensure that each product has a comprehensive list of synonyms and trigger phrases to cover diverse user inquiries.

2. **Utilize Patterns**: Enhance the pattern detection files to recognize product names and intents in various formats, improving the bot's understanding of user queries.

3. **Add Contextual Information**: Include additional contextual information in the intent markdown files to help the chatbot grasp the nuances of each question.

4. **Incorporate Paraphrases**: Utilize the paraphrases directory to include a wide range of paraphrased questions for each intent, enhancing the bot's ability to recognize similar queries.

5. **Regular Updates**: Continuously update the knowledge base with new questions and answers based on user interactions to maintain the chatbot's relevance and effectiveness.

## Setup and Usage

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the application using `python src/app.py`.
4. Configure your Slack app to connect with the chatbot.

This README provides an overview of the project and serves as a guide for developers and users to understand the structure and functionality of the Slack RAG chatbot.