from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "App is running 🚀", 200


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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
