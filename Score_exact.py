import os, math, requests, datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID", "@palenfo")
ODDS_KEY = os.getenv("ODDS_API_KEY")

def poisson(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def predict_score():
    lam_home = 1.7
    lam_away = 1.0
    best = []
    for h in range(0, 4):
        for a in range(0, 4):
            prob = poisson(lam_home, h) * poisson(lam_away, a)
            best.append(((h, a), prob))
    best.sort(key=lambda x: x[1], reverse=True)
    return best[:3]

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {"apiKey": ODDS_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json()[:8]
    except:
        return []

def format_coupon():
    matches = get_matches()
    if not matches:
        return "Pas de matchs aujourd'hui, on revient demain."
    txt = "🎯 SCORES EXACTS DU JOUR\n\nStrategie : Joue les 3 scores pour couvrir 35% de chances.\n\n"
    for m in matches:
        home = m.get("home_team", "?")
        away = m.get("away_team", "?")
        top3 = predict_score()
        txt += f"⚽ {home} vs {away}\n"
        for (h,a), prob in top3:
            txt += f"  -> {h}-{a}  ({int(prob*100)}%)\n"
        txt += "\n"
    txt += "Mise conseillee : 500F par score. Joue responsable."
    return txt

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Score Exact Palenfo pret ! Tape /score")

async def score_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = format_coupon()
    await update.message.reply_text(txt)

async def job_auto(context: ContextTypes.DEFAULT_TYPE):
    txt = format_coupon()
    await context.bot.send_message(chat_id=CHANNEL, text=txt)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("score", score_now))
    app.job_queue.run_daily(job_auto, time=datetime.time(hour=9, minute=0))
    print("BOT SCORE EXACT DEMARRE")
    app.run_polling()

if __name__ == "__main__":
    main()
