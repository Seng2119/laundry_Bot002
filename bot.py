import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# --- បន្ថែម Web Server សម្រាប់ Render Web Service ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    # Render នឹងផ្តល់ PORT ឱ្យស្វ័យប្រវត្តិ
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# --------------------------------------------------

# ===================== CONFIG =====================
TOKEN = "8914891442:AAFmetURFYk9GqqOpS7aQJsECYM87WVcCkw"
SHOP_NAME = "រស្មី សន្តិភាពបោកគក់"
PHONE = "010716615"
ADDRESS = "មន្ទីពេទ្យតេជោសន្តិភាព នៅចន្លោះ អគារ H3 នឹង H4"

SERVICES = [
    "🧺 បោក + សម្ងួត (Wash & Dry)",
    "👔 អ៊ុតសម្លៀកបំពាក់ (Ironing)",
    "🧥 បោកដាច់ដោយឡែក ( VIP)",
    "🛏️ បោកកម្រាលពូក ភួយ ស្រោមខ្នើយ",
    "🚚 សេវាទទួល និងដឹកជូនដល់កន្លែង",
]

PRICES = [
    ("បោក + សម្ងួត", "៣,០០០៛ / គីឡូ"),
    ("បោក + អ៊ុត", "៤,០០០៛ / កំប្លេ"),
    ("ភួយ / កម្រាលពូក", "គិតតាមភួយតូចធំ"),
    ("បោកដាច់ឡែក (VIP)", "១២,០០០៛ / ៣គីឡូ"),
    ("សេវាដឹកជញ្ជូន", "ឥតគិតថ្លៃ"),
]

HOURS = [("ច័ន្ទ – អាទិត្យ", "០៧:៣០ ព្រឹក – ០៦:០០ ល្ងាច")]
DURATION = "ករណីបន្ទាន់ បោក VIP"
LINE = "━━━━━━━━━━━━━━━"

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧺 សេវាកម្ម", callback_data="services"),
         InlineKeyboardButton("💰 តម្លៃ", callback_data="prices")],
        [InlineKeyboardButton("🕐 ម៉ោងបើក-បិទ", callback_data="hours"),
         InlineKeyboardButton("📞 ទំនាក់ទំនង", callback_data="contact")],
    ])

def txt_services():
    body = "\n".join(f"  {s}" for s in SERVICES)
    return f"🧺 <b>សេវាកម្មរបស់ {SHOP_NAME}</b>\n{LINE}\n\n{body}\n\n⏱ <i>{DURATION}</i>"

def txt_prices():
    rows = "\n".join(f"  •  {n}  —  <b>{p}</b>" for n, p in PRICES)
    return f"💰 <b>តារាងតម្លៃ</b>\n{LINE}\n\n{rows}\n\n<i>តម្លៃអាចប្រែប្រួលតាមប្រភេទសម្លៀកបំពាក់</i>"

def txt_hours():
    rows = "\n".join(f"  🗓  {d}  —  {h}" for d, h in HOURS)
    return f"🕐 <b>ម៉ោងបើក-បិទ</b>\n{LINE}\n\n{rows}"

def txt_contact():
    return f"📞 <b>ទំនាក់ទំនង</b>\n{LINE}\n\n  ☎️  {PHONE}\n  📍  {ADDRESS}"

def welcome_text():
    return (
        f"👋 <b>សួស្តី! សូមស្វាគមន៍មកកាន់</b>\n"
        f"✨ <b>{SHOP_NAME}</b> ✨\n{LINE}\n\n"
        "សូមចុចប៊ូតុងខាងក្រោម ដើម្បីមើលព័ត៌មានលម្អិត 👇"
    )

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        welcome_text(), parse_mode="HTML", reply_markup=menu()
    )

async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    mapping = {
        "services": txt_services(),
        "prices": txt_prices(),
        "hours": txt_hours(),
        "contact": txt_contact(),
    }
    await q.edit_message_text(
        mapping[q.data], parse_mode="HTML", reply_markup=menu()
    )

KEYWORDS = {
    ("តម្លៃ", "ថ្លៃ", "ប៉ុន្មាន", "price"): txt_prices,
    ("ម៉ោង", "បើក", "បិទ", "open", "close"): txt_hours,
    ("សេវា", "បោក", "អ៊ុត", "service", "wash"): txt_services,
    ("លេខ", "ទំនាក់", "ទីតាំង", "phone", "address"): txt_contact,
}

async def auto_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (update.message.text or "").lower()
    for keys, fn in KEYWORDS.items():
        if any(k in msg for k in keys):
            await update.message.reply_text(
                fn(), parse_mode="HTML", reply_markup=menu()
            )
            return
    await update.message.reply_text(
        f"🙏 <b>សូមអភ័យទោស</b> ខ្ញុំមិនយល់សំណួរនេះទេ\n\n"
        f"សូមចុចប៊ូតុងខាងក្រោម ឬទូរស័ព្ទមកលេខ ☎️ {PHONE}",
        parse_mode="HTML", reply_markup=menu()
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # បើក Web Server ឱ្យដើរក្នុង Background
    keep_alive()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler(["start", "help", "menu"], start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    print("Bot is running...")
    app.run_polling()