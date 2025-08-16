# Data Folder Structure for Slack Chatbot

This folder contains all the necessary data files and directories to support the Slack chatbot's functionality. The structure is organized by product, with each product having its own directory containing intents, synonyms, triggers, and other relevant files.

## Directory Structure

- **adonis/**: Contains information specific to the Adonis product.
  - **intents/**: Holds markdown files for each intent related to Adonis, detailing questions and answers.
  - **synonyms.yaml**: Lists synonyms related to Adonis.
  - **triggers.yaml**: Contains trigger phrases for Adonis-related intents.

- **ascender/**: Contains information specific to the Ascender product.
  - **intents/**: Holds markdown files for each intent related to Ascender.
  - **synonyms.yaml**: Lists synonyms related to Ascender.
  - **triggers.yaml**: Contains trigger phrases for Ascender-related intents.

- **hermes/**: Contains information specific to the Hermes product.
  - **intents/**: Holds markdown files for each intent related to Hermes.
  - **synonyms.yaml**: Lists synonyms related to Hermes.
  - **triggers.yaml**: Contains trigger phrases for Hermes-related intents.

- **zeus/**: Contains information specific to the Zeus product.
  - **intents/**: Holds markdown files for each intent related to Zeus.
  - **synonyms.yaml**: Lists synonyms related to Zeus.
  - **triggers.yaml**: Contains trigger phrases for Zeus-related intents.

- **shared/**: Contains shared resources for all products.
  - **product_aliases.yaml**: Maps product names to their aliases.
  - **intent_aliases.yaml**: Maps intent names to their aliases.

- **patterns/**: Contains files for pattern matching and normalization.
  - **product_detection.yaml**: Defines patterns for detecting product mentions.
  - **normalization.yaml**: Contains rules for normalizing user input.

- **paraphrases/**: Contains paraphrase files for each product.
  - **adonis/**: JSONL files with paraphrases for Adonis-related intents.
  - **ascender/**: JSONL files with paraphrases for Ascender-related intents.
  - **hermes/**: JSONL files with paraphrases for Hermes-related intents.
  - **zeus/**: JSONL files with paraphrases for Zeus-related intents.

- **schemas/**: Contains JSON schema files for validating intents and products.
  - **intent.schema.json**: Defines the structure for intents.
  - **product.schema.json**: Defines the structure for products.

## Recommendations for Improvement

1. **Expand Synonyms and Triggers**: Ensure comprehensive coverage of synonyms and trigger phrases for each product to enhance understanding of user queries.

2. **Utilize Patterns**: Develop sophisticated detection patterns to recognize product names and intents in various formats.

3. **Add Contextual Information**: Include contextual details in intent markdown files to clarify the nuances of questions.

4. **Incorporate Paraphrases**: Use the paraphrases directory to include diverse paraphrased questions for each intent.

5. **Regular Updates**: Continuously update the knowledge base with new questions and answers based on user interactions to maintain relevance and effectiveness.