from flask import Flask, request, jsonify, Response
import asyncio
import requests
import os

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

app = Flask(__name__)

# =========================
# 🔐 BOT AUTH (HARDCODED FOR NOW)
# =========================
APP_ID = "b32f363d-cd10-473c-8728-4674e58399d8"

# 👇 PASTE YOUR SECRET VALUE HERE (NOT SECRET ID)
APP_PASSWORD = "LFg8Q~6ovLcy6WhkaenLEZ-1O4uHBdgvs1-n.cwY"

settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)


# =========================
# 🤖 BOT LOGIC
# =========================
async def on_message_activity(turn_context: TurnContext):
    user_text = turn_context.activity.text.lower()

    try:
        if "convert" in user_text:
            parts = user_text.split()
            amount = float(parts[1])
            from_currency = parts[2].upper()
            to_currency = parts[4].upper()

            url = f"https://open.er-api.com/v6/latest/{from_currency}"
            data = requests.get(url).json()

            if data.get("result") != "success":
                reply = "Currency API failed ❌"
            else:
                rate = data["rates"].get(to_currency)
                if not rate:
                    reply = "Invalid currency ❌"
                else:
                    converted = round(amount * rate, 2)
                    reply = f"{amount} {from_currency} = {converted} {to_currency} 💰"
        else:
            reply = "Try: convert 10 USD to INR"

    except Exception:
        reply = "Invalid format. Try: convert 10 USD to INR"

    await turn_context.send_activity(reply)


# =========================
# 📩 BOT ENDPOINT
# =========================
@app.route("/api/messages", methods=["POST"])
def messages():
    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def call_bot_logic(turn_context):
        await on_message_activity(turn_context)

    task = adapter.process_activity(activity, auth_header, call_bot_logic)
    asyncio.run(task)

    return Response(status=201)


# =========================
# 🌐 REST API
# =========================
@app.route("/convert", methods=["GET"])
def convert_currency():
    from_currency = request.args.get("from")
    to_currency = request.args.get("to")
    amount = request.args.get("amount")

    if not from_currency or not to_currency or not amount:
        return jsonify({"error": "Missing parameters"}), 400

    url = f"https://open.er-api.com/v6/latest/{from_currency}"
    data = requests.get(url).json()

    if data.get("result") != "success":
        return jsonify({"error": "API failed"}), 500

    rate = data["rates"].get(to_currency)

    if not rate:
        return jsonify({"error": "Invalid currency"}), 400

    converted = float(amount) * rate

    return jsonify({
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "converted_amount": round(converted, 2)
    })


# =========================
# 🏠 HEALTH CHECK
# =========================
@app.route("/")
def home():
    return "Bot is running 🚀"


# =========================
# ▶ RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
