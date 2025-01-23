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
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {query}\nAnswer:"
    )
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()