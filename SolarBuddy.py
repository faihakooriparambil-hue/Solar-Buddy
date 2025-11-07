from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ⚡ Grab your OpenAI API key safely from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"reply": "Please send a message!"})

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Solar Buddy, a friendly AI assistant for families in the UAE. "
                    "Answer questions about solar energy, energy savings, and eco-friendly habits "
                    "in 1-5 sentences. Be polite, helpful, and fun."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()  # catches HTTP errors
        reply = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error:", e)
        reply = "Oops, something went wrong! Please try again."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000, debug=True)


