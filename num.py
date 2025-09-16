import os
import requests
from flask import Flask, request

# -----------------------------
# Environment Variables
# -----------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Render এ এড করতে হবে
NUMLOOKUP_API = os.environ.get("NUMLOOKUP_API")  # Render এ এড করতে হবে

WEBHOOK_URL = f"https://num-info-bot-shadow.onrender.com/{BOT_TOKEN}"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

app = Flask(__name__)

# -----------------------------
# Number Lookup Function
# -----------------------------
def get_num_info(phone: str) -> str:
    try:
        url = f"https://api.numlookupapi.com/v1/validate/{phone}?country_code=BD"
        headers = {"apikey": NUMLOOKUP_API}
        res = requests.get(url, headers=headers, timeout=5).json()

        if "valid" in res and res["valid"]:
            msg = (
                f"🔎 *Number Info (BD)* 🔎\n\n"
                f"📱 Number: `{res.get('international_format', phone)}`\n"
                f"🏠 Local: `{res.get('local_format', '')}`\n"
                f"🏳 Country: *{res.get('country_name', 'Bangladesh')}*\n"
                f"📡 Carrier: *{res.get('carrier', 'Unknown')}*\n"
                f"☎ Line Type: *{res.get('line_type', 'Unknown')}*\n"
            )

            if res.get("name"):
                msg += f"👤 Name: *{res['name']}*\n"
            if res.get("email"):
                msg += f"📧 Email: `{res['email']}`\n"

            msg += f"\n━━━━━━━━━━━━━━━\n👤 Credit: *SHADOW JOKER*"

        else:
            msg = f"❌ Invalid Number: `{phone}`"
        return msg
    except Exception as e:
        return f"⚠ Error: {e}"

# -----------------------------
# Send Message with optional buttons
# -----------------------------
def send_message(chat_id, text, buttons=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}

    requests.post(API_URL + "sendMessage", json=payload)

# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def home():
    return "🤖 Number Info Bot Running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/num"):
            args = text.split(" ")
            if len(args) == 2:
                number = args[1]
                info = get_num_info(number)
                send_message(chat_id, info)
            else:
                send_message(chat_id, "⚠ Usage: `/num <MOBILE_NUMBER>` (BD only)")

        elif text == "/start":
            # Inline button example
            buttons = [
                [{"text": "Send Number 📱", "switch_inline_query_current_chat": ""}]
            ]
            send_message(
                chat_id,
                "👋 Welcome to *Number Info Bot* 🇧🇩\n\n"
                "Click the button below to send a BD number and get info 📱\n\n"
                "━━━━━━━━━━━━━━━\n👤 Credit: *SHADOW JOKER*",
                buttons
            )

    elif "callback_query" in update:
        # যদি future এ callback button যুক্ত করা হয়
        pass

    return "ok"

# -----------------------------
# Set Webhook Automatically
# -----------------------------
def set_webhook():
    res = requests.get(API_URL + "setWebhook", params={"url": WEBHOOK_URL})
    print("Webhook setup response:", res.json())

# -----------------------------
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)