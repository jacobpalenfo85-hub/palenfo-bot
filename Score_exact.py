import os, datetime, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("ODDS_API_KEY")
def get_scores():
    today = datetime.date.today().isoformat()
    url = f"https://v3.football.api-sports.io/fixtures?date={today}"
    headers = {"x-apisports-key": API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=20).json()
        matchs = r.get("response", [])
        if not matchs:
            return "Aucun match aujourd'hui."
        txt = "🎯 *SCORES EXACTS DU JOUR* 🎯\n\n"
        for m in matchs[:15]:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            league = m["league"]["name"]
            # Prédiction simple
            txt += f"🏆 {league}\n{home} vs {away}\n➡️ Score probable : 1-1 / 2-1\n\n"
        txt += "Bonne chance 🍀"
        return txt
    except Exception as e:
        return f"Erreur : {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Envoie /score pour les scores exacts du jour 🎯")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_scores(), parse_mode="Markdown")

def auto_loop(app):
    # Envoie tout seul à 9h00
    sent_today = None
    while True:
        now = datetime.datetime.now()
        if now.hour == 9 and now.minute == 0 and sent_today != now.date():
            try:
                asyncio.run_coroutine_threadsafe(
                    app.bot.send_message(chat_id=CHAT_ID, text=get_scores(), parse_mode="Markdown"),
                    app.loop if hasattr(app, 'loop') else asyncio.get_event_loop()
                )
                sent_today = now.date()
            except Exception as e:
                print("Erreur auto:", e)
        time.sleep(50)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("score", score))
    # Lance la boucle auto en arrière-plan
    threading.Thread(target=auto_loop, args=(app,), daemon=True).start()
    print("Bot Score Exact démarré...")
    app.run_polling()
