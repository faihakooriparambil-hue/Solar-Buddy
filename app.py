from flask import Flask, render_template, request
from transformers import pipeline
import requests
import random
import re

app = Flask(__name__)

# ===== AI MODEL =====
qa = pipeline("text2text-generation", model="google/flan-t5-large")

# ===== CHAT HISTORY =====
chat_history = []

# ===== WEATHER API KEY =====
OPENWEATHER_API_KEY = "9ed9b6938cc15732cc89f8e8bbcb3a65"  

# ===== CITY LIST =====
UAE_CITIES = [
    "Abu Dhabi,AE", "Dubai,AE", "Sharjah,AE", "Ajman,AE",
    "Ras Al Khaimah,AE", "Fujairah,AE", "Umm Al Quwain,AE"
]

INTERNATIONAL_CITIES = [
    "New York,US", "London,GB", "Paris,FR", "Tokyo,JP", "Sydney,AU", 
    "Mumbai,IN", "Singapore,SG", "Seoul,KR", "Shanghai,CN", "Beijing,CN", 
    "Berlin,DE", "Budapest,HU", "Milan,IT", "Moscow,RU"
]

ALL_CITIES = UAE_CITIES + INTERNATIONAL_CITIES

# ===== WEATHER FUNCTION =====
def get_weather(city="Dubai,AE"):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        if data.get("cod") != 200:
            return f"Sorry, I couldn't find weather info for '{city.split(',')[0]}'."  # show only city name

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()

        if "rain" in desc.lower():
            air_status = "It looks rainy 🌧️ — stay cozy!"
        elif "clear" in desc.lower():
            air_status = "The sky’s clear ☀️ — perfect for solar panels!"
        elif "cloud" in desc.lower():
            air_status = "A bit cloudy ☁️ but still good for solar energy."
        else:
            air_status = "Moderate conditions outside 🌤️."

        return f"{desc}. Temp: {temp}°C (feels like {feels_like}°C). Humidity: {humidity}%. {air_status}"

    except Exception as e:
        print("Weather fetch error:", e)
        return "Weather info couldn’t be fetched right now 🌥️"

# ===== CITY DETECTION =====
def extract_city(user_input):
    user_input = user_input.lower()
    for city in ALL_CITIES:
        if city.split(',')[0].lower() in user_input:
            return city
    return "Dubai,AE"  # default

# ===== MAIN ROUTE =====
@app.route("/", methods=["GET", "POST"])
def home():
    global chat_history
    if request.method == "POST":
        user_input = request.form.get("prompt", "").strip()

        # ❌ Reject empty input
        if not user_input:
            chat_history.append(("Solar Buddy", "Please type something ☀️"))
            return render_template("index.html", chat_history=chat_history)

        # ❌ Enforce ONE MESSAGE at a time
        sentences = [s for s in re.split(r'[.!?;\n]+', user_input) if s.strip()]
        if len(sentences) > 1:
            chat_history.append(("Solar Buddy", "Please ask **only one question at a time** ☀️"))
            return render_template("index.html", chat_history=chat_history)

        chat_history.append(("You", user_input))
        lower_input = user_input.lower()

        # ===== WEATHER =====
        if any(word in lower_input for word in ["weather", "temperature", "humidity"]):
            city = extract_city(user_input)
            weather_report = get_weather(city)
            chat_history.append(("Solar Buddy", f"Here’s the weather in {city.split(',')[0]}: {weather_report}"))

        # ===== GREETINGS =====
        elif any(g in lower_input for g in ["hi", "hello", "hey"]):
            chat_history.append(("Solar Buddy", random.choice([
                "Hello! ☀️ How can I brighten your solar knowledge today?",
                "Hey! Ready to learn something about solar energy?",
                "Hi there! 🌞 Ask me anything about solar power."
            ])))

        # ===== SOLAR QUESTIONS =====
        elif any(word in lower_input for word in ["solar", "energy", "sun", "panel"]):
            prompt = (
                f"You are Solar Buddy, a friendly AI assistant. "
                f"Answer the user's question clearly, politely, and only about solar energy. "
                f"Do NOT talk about yourself. Keep it simple and concise under 120 words. "
                f"Question: {user_input}"
            )
            result = qa(prompt, max_length=200, temperature=0.8, top_p=0.9, do_sample=True)
            response = result[0]["generated_text"].strip()
            response = response.replace("Solar Buddy:", "").replace("solar buddy", "").strip()
            chat_history.append(("Solar Buddy", response))

        # ===== OFF-TOPIC =====
        else:
            chat_history.append(("Solar Buddy", "I mainly talk about solar energy or weather ☀️ Please ask about those topics."))

    return render_template("index.html", chat_history=chat_history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
