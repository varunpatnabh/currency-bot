from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# -------------------------
# Health Check (IMPORTANT for Azure)
# -------------------------
@app.route("/")
def home():
    return "App is running 🚀", 200


# -------------------------
# REST API (your original)
# -------------------------
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


# -------------------------
# TEAMS BOT ENDPOINT (NEW)
# -------------------------
@app.route("/api/messages", methods=["POST"])
def messages():
    data = request.json

    user_text = data.get("text", "").lower()

    try:
        if "convert" in user_text:
            parts = user_text.split()

            # Expected: convert 10 usd to inr
            amount = float(parts[1])
            from_currency = parts[2].upper()
            to_currency = parts[4].upper()

            url = f"https://open.er-api.com/v6/latest/{from_currency}"
            api_data = requests.get(url).json()

            if api_data.get("result") != "success":
                reply = "Currency API failed"
            else:
                rate = api_data["rates"].get(to_currency)

                if not rate:
                    reply = "Invalid currency"
                else:
                    converted = round(amount * rate, 2)
                    reply = f"{amount} {from_currency} = {converted} {to_currency}"

        else:
            reply = "Try: convert 10 USD to INR"

    except Exception as e:
        reply = "Format error. Try: convert 10 USD to INR"

    return {
        "type": "message",
        "text": reply
    }


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
