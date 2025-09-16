import os
import requests
from flask import Flask, request

# -----------------------------
# Environment Variables
# -----------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
NUMLOOKUP_API = os.environ.get("NUMLOOKUP_API")
WEBHOOK_URL = f"https://number-info-bot-shadow.onrender.com/{BOT_TOKEN}"
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
# Send Message with Inline Buttons
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
# Handle Callback Query
# -----------------------------
def answer_callback(callback_id, text):
    requests.post(API_URL + "answerCallbackQuery", json={"callback_query_id": callback_id, "text": text, "show_alert": False})

# -----------------------------
# Dictionary to track users waiting for input
# -----------------------------
waiting_for_number = set()  # store chat_ids of users who clicked "Send Number"

# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def home():
    return "🤖 Number Info Bot Running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    # ----------------- Message Handling -----------------
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # /start command
        if text == "/start":
            buttons = [
                [{"text": "01950178309", "callback_data": "01950178309"}],
                [{"text": "017XXXXXXXX", "callback_data": "017XXXXXXXX"}],
                [{"text": "Send Number", "callback_data": "SEND_NUMBER"}]
            ]
            send_message(
                chat_id,
                "👋 Welcome to *Number Info Bot* 🇧🇩\nClick a number below to get info or click 'Send Number' to type your own 📱\n━━━━━━━━━━━━━━━\n👤 Credit: *SHADOW JOKER*",
                buttons
            )
        else:
            # Check if user is in waiting state
            if chat_id in waiting_for_number:
                number = text.strip()
                info = get_num_info(number)
                send_message(chat_id, info)
                waiting_for_number.remove(chat_id)
            else:
                send_message(chat_id, "⚠ Please click a number button or 'Send Number' to provide a number.")

    # ----------------- Callback Handling -----------------
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        callback_id = callback["id"]
        data = callback["data"]

        if data == "SEND_NUMBER":
            waiting_for_number.add(chat_id)
            send_message(chat_id, "✏️ Please type the number now:")
            answer_callback(callback_id, "💡 Type your number in chat to get info")
        else:
            # Number button clicked
            info = get_num_info(data)
            send_message(chat_id, info)
            answer_callback(callback_id, f"✅ Info fetched for {data}")

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
