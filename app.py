from flask import Flask, request, Response
import asyncio

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

import os

app = Flask(__name__)

# 🔐 Azure Bot credentials (auto picked from env)
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)


# -------------------------
# BOT LOGIC
# -------------------------
async def on_message_activity(turn_context: TurnContext):
    user_text = turn_context.activity.text

    reply = f"You said: {user_text}"

    await turn_context.send_activity(reply)


# -------------------------
# MAIN ENDPOINT
# -------------------------
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


# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/")
def home():
    return "Bot is running 🚀"


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
