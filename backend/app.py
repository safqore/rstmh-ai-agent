from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS
import requests
import os

app = Flask(__name__) # <--- FOR DEPLOYMENT!!!

# FOR DEPLOYMENT!!! -- Allow specific frontend origin (Netlify) 
CORS(app, resources={r"/api/*": {"origins": ["https://resilient-blancmange-19745d.netlify.app"]}})


HF_API_URL = 'https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill'
HF_API_TOKEN = os.getenv('HF_API_TOKEN')  # Key to be picked up with environment variables

# HF_API_TOKEN = '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'


@app.route('/')
def index():
    return render_template('customer.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"reply": "Message is required."}), 400

    payload = {
        "inputs": user_message,
        "options": {"wait_for_model": True}
    }

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        print("API Response: ", data)  # Debugging line
        reply = data[0].get('generated_text', 'No response.')
        return jsonify({"reply": reply.strip()})

    except requests.exceptions.RequestException as e:
        print(f"Error contacting Hugging Face API: {e}")
        return jsonify({"reply": "An error occurred while fetching the response."}), 500


if __name__ == '__main__':
    app.run(debug=True)
