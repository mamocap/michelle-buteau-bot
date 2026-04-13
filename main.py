import os
import logging
import asyncio
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """את המאמנת העסקית של המשתמשת — סטייליסטית ומספרת סיפורים ויזואליים בתחום האופנה.

האישיות שלך היא בסגנון מישל ביוטו: ישירה, מצחיקה, חמה, קצת דרמטית, עם הרבה אנרגיה וחוש הומור. 
את מדברת עברית, את לא מסבירה יותר מדי — את אומרת את האמת בצורה מצחיקה ואוהבת.
את עוזרת למשתמשת לבנות את העסק שלה סביב סיפורים ויזואליים באופנה — תוכן, שיווק, מציאת לקוחות, תמחור, ומיתוג אישי.
כשהיא מתלבטת — את שואלת שאלה אחת חדה שתעזור לה להתבהר.
כשהיא צריכה עידוד — את נותנת אותו בסגנון שלך: ישיר, חם ומצחיק.
תמיד תשמרי על תגובות קצרות וקולעות — לא יותר מ-3-4 משפטים."""

conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "היי! אני המאמנת העסקית שלך 👗✨\n"
        "אני כאן כדי לעזור לך לבנות עסק מסיפורים ויזואליים באופנה.\n"
        "אז תגידי לי — מה קורה? מה מעכב אותך היום? 😄"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })

    if len(conversation_history[user_id]) > 10:
        conversation_history[user_id] = conversation_history[user_id][-10:]

    client = Groq(api_key=GROQ_API_KEY)

    messages_with_system = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[user_id]

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        max_tokens=500,
        messages=messages_with_system
    )

    assistant_message = response.choices[0].message.content

    conversation_history[user_id].append({
        "role": "assistant",
        "content": assistant_message
    })

    await update.message.reply_text(assistant_message)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("הבוט רץ! 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
