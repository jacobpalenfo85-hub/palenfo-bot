
    import os, asyncio, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ODDS_KEY = os.getenv("ODDS_API_KEY")
CHANNEL = os.getenv("CHANNEL_ID", "@palenfo_ai")
STAKE = 10000

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {"apiKey": ODDS_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params)
        return r.json()
    except Exception as e:
        print(f"Erreur API: {e}")
        return []

def build_coupon(matches):
    picks = []
    for m in matches:
        if not m.get("bookmakers"):
            continue
        odds = m["bookmakers"][0]["markets"][0]["outcomes"]
        home = next((o for o in odds if o["name"] == m["home_team"]), None)
        if home and 1.30 <= home["price"] <= 1.65:
            picks.append((m["home_team"], m["away_team"], home["price"]))
        if len(picks) >= 4:
            break
    return picks

def format_coupon(picks):
    if not picks:
        return None
    cote_totale = 1.0
    txt = "🔥 PALENFO AI - COUPON DU JOUR\n⭐ COMBINE SECURISE V3\n\n"
    for i, (h, a, cote) in enumerate(picks, 1):
        cote_totale *= cote
        txt += f"{i}. {h} vs {a}\n   Victoire {h} - Cote {cote}\n\n"
    gain = STAKE * cote_totale
    txt += f"----------------\nMise : {STAKE:,} FCFA\nCote Totale : {cote_totale:.2f}\nGain Potentiel : {gain:,.0f} FCFA\n----------------\n\nJouez responsable. 18+"
    return txt

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue sur PALENFO AI !\n\nJe t'envoie chaque jour à 9h et 16h un coupon sécurisé.\n\nTape /coupon pour recevoir le coupon du jour maintenant.")

async def coupon_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Génération du coupon en cours...")
    matches = get_matches()
    picks = build_coupon(matches)
    txt = format_coupon(picks)
    if txt:
        await update.message.reply_text(txt)
    else:
        await update.message.reply_text("Pas de matchs pour le moment, reviens plus tard.")

async def job_auto(app):
    print("Generation coupon auto...")
    matches = get_matches()
    picks = build_coupon(matches)
    txt = format_coupon(picks)
    if txt:
        await app.bot.send_message(chat_id=CHANNEL, text=txt)
        print("Envoye au canal")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coupon", coupon_now))
    sched = AsyncIOScheduler()
    sched.add_job(job_auto, 'cron', hour=9, minute=0, args=[app])
    sched.add_job(job_auto, 'cron', hour=16, minute=0, args=[app])
    sched.start()
    print("PALENFO AUTO demarre - 9h et 16h")
    app.run_polling()

if __name__ == "__main__":
    main()
