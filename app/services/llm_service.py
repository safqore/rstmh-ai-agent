from openai import OpenAI
import os
from dotenv import load_dotenv
import os

os.environ.clear()
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
env_path = os.path.join(current_dir, '../..', '.env')
# Load the environment variables
load_dotenv(dotenv_path=env_path)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm_response(query, context):
    print(f"[DEBUG] Context for LLM: {context[:200]}...")
    prompt = (
            f"You are an expert assistant. Answer the following question based on the provided context.\n"
            f"You should only answer questions related to RSTMH Early Career Grants Programme.\n"
            f"If user asks questions unrelating to RSTMH Early Career Grants Programme, Politely inform user you can only answer question relating to RSTMH Early Career Grants Programme.\n"
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
    if "Answer:" in llm_reply:
            llm_reply = llm_reply.split("Answer:")[-1].strip()
    return llm_reply