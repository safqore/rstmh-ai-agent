from openai import OpenAI
import os
from dotenv import load_dotenv
import os

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
env_path = os.path.join(current_dir, '../..', '.env')
# Load the environment variables
load_dotenv(dotenv_path=env_path)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm_response(query, context, chat_history):
    print(f"[DEBUG] Context for LLM: {context[:200]}...")
    
    prompt = (
        f"You are a knowledgeable and helpful assistant focused on the RSTMH Early Career Grants Programme. "
        f"Use the provided context and chat history to answer questions as accurately as possible. "
        f"If a question is slightly outside the context but related to grants, research, or funding, do your best to provide helpful information based on your expertise. "
        f"If a question is completely unrelated to the RSTMH Early Career Grants Programme or grants in general, respond with: "
        f"'I'm sorry, but I can only provide information related to the RSTMH Early Career Grants Programme or grants in general. If you have any questions about funding opportunities or research, feel free to ask!'\n"
        f"If the user asks a question that contains non-English words, respond with: "
        f"'I'm sorry, but I can only understand and respond in English. Please ask your question in English.'\n"
        f"Chat History:\n{chat_history}\n"
        f"Context:\n{context}\n"
        f"Question: {query}\n"
        f"Answer:"
    )

    print("[DEBUG] Sending prompt to OpenAI GPT-4o-mini.")
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    llm_reply = response.choices[0].message.content.strip()
    print(f"[DEBUG] LLM Reply: {llm_reply}")

    return llm_reply