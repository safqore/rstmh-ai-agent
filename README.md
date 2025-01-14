# rsmth-test-bot
![MIT License](https://img.shields.io/badge/license-MIT-green)

rsmth-test-bot is a document-processing bot that accepts documents from various clients and provides answers to questions based on the content of those documents. It utilizes natural language processing (NLP) to extract, analyze, and respond to user queries accurately.

## Prerequisites

- **Backend**: Deployed on Render.
- **Frontend**: Deployed on Netlify.
- **Databases**:
  - **Vector Database**: Qdrant.
  - **Logging Database**: PostgreSQL via Supabase.
- **APIs**:
  - **OpenAI**: For NLP capabilities.

## Environment Variables

### Backend

Create a `.env` file in the backend directory with the following variables:

```plaintext
QDRANT_HOST=<your-qdrant-host>
QDRANT_API_KEY=<your-qdrant-api-key>
SUPABASE_URL=<your-supabase-url>
SUPABASE_API_KEY=<your-supabase-api-key>
OPENAI_API_KEY=<your-openai-api-key>
