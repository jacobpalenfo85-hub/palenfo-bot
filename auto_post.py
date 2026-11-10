import os, asyncio, requests
from telegram.ext import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ODDS_KEY = os.getenv("ODDS_API_KEY")
CHANNEL = os.getenv("CHANNEL_ID", "@palenfo_pronostic")
STAKE = 10000

def get_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {"apiKey": ODDS_KEY, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=20)
        return r.json()
    except Exception as e:
        print(f"Erreur API: {e}")
        return []

def build_coupon(matches):
    picks = []
    for m in matches:
        if not m.get("bookmakers"): continue
        odds = m["bookmakers"][0]["markets"][0]["outcomes"]
        home = next((o for o in odds if o["name"] == m["home_team"]), None)
        if home and 1.30 <= home["price"] <= 1.75:
            picks.append((m["home_team"], m["away_team"], home["price"]))
        if len(picks) >= 8: break
    return picks

def format_coupon(picks):
    if not picks:
        return None
    cote_totale = 1.0
    txt = "🔥 *PALENFO AI - COUPON DU JOUR* 🔥\n\n"
    txt += "🏆 *COMBINE SECURISE V3*\n\n"
    for i, (h, a, cote) in enumerate(picks, 1):
        cote_totale *= cote
        txt += f"{i}. {h} vs {a}\n   Victoire {h} - Cote {cote:.2f}\n\n"
    gain = STAKE * cote_totale
    txt += f"------------\n"
    txt += f"Mise : {STAKE:,} FCFA\n"
    txt += f"Cote Totale : {cote_totale:.2f}\n"
    txt += f"Gain Potentiel : {gain:,.0f} FCFA\n"
    txt += f"------------\n\n"
    txt += f"Jouez responsable. 18+"
    return txt

async def job_auto(app):
    print("Generation coupon auto...")
    matches = get_matches()
    picks = build_coupon(matches)
    txt = format_coupon(picks)
    if txt:
        await app.bot.send_message(chat_id=CHANNEL, text=txt, parse_mode="Markdown")
        print("Envoye au canal")
    else:
        print("Pas de matchs")

def main():
    app = Application.builder().token(TOKEN).build()
    sched = AsyncIOScheduler()
    sched.add_job(job_auto, 'cron', hour=9, minute=0, args=[app])
    sched.add_job(job_auto, 'cron', hour=16, minute=0, args=[app])
    sched.start()
    print("PALENFO AUTO demarre - 9h et 16h")
    asyncio.get_event_loop().create_task(job_auto(app))
    app.run_polling()

if __name__ == "__main__":
    main()
