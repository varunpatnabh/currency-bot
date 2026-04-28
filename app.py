@app.route("/api/messages", methods=["POST"])
def messages():
    data = request.json

    user_text = data.get("text", "").lower()

    try:
        if "convert" in user_text:
            parts = user_text.split()

            amount = float(parts[1])
            from_currency = parts[2].upper()
            to_currency = parts[4].upper()

            url = f"https://open.er-api.com/v6/latest/{from_currency}"
            api_data = requests.get(url).json()

            if api_data.get("result") != "success":
                reply_text = "Currency API failed"
            else:
                rate = api_data["rates"].get(to_currency)

                if not rate:
                    reply_text = "Invalid currency"
                else:
                    converted = round(amount * rate, 2)
                    reply_text = f"{amount} {from_currency} = {converted} {to_currency}"

        else:
            reply_text = "Try: convert 10 USD to INR"

    except:
        reply_text = "Format error. Try: convert 10 USD to INR"

    # 🔥 IMPORTANT: Proper Bot Framework response
    return {
        "type": "message",
        "text": reply_text,
        "from": data.get("recipient"),
        "recipient": data.get("from"),
        "replyToId": data.get("id")
    }
