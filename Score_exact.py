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
 
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("score", score))
    print("Bot Score Exact démarré...")
    app.run_polling()
