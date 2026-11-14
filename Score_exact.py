import os
import math
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def poisson(lam, k):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def predict(xg_home, xg_away):
    results = []
    for h in range(0, 6):
        for a in range(0, 6):
            p = poisson(xg_home, h) * poisson(xg_away, a)
            results.append((p, h, a))
    results.sort(reverse=True)
    return results[:3]

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, 
        "⚽ Bot Score Exact\n\n"
        "Utilisation :\n"
        "/score 1.5 0.9\n\n"
        "1er chiffre = buts attendus équipe à domicile\n"
        "2ème chiffre = buts attendus équipe à l'extérieur\n\n"
        "Exemple : /score 1.8 1.2"
    )

@bot.message_handler(commands=['score'])
def score(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Fais comme ça : /score 1.5 0.9")
            return
        
        xg_home = float(parts[1])
        xg_away = float(parts[2])
        
        top3 = predict(xg_home, xg_away)
        
        txt = f"📊 xG Domicile {xg_home} - xG Extérieur {xg_away}\n\n"
        txt += "🏆 Score exact le plus probable :\n\n"
        for i, (p, h, a) in enumerate(top3, 1):
            txt += f"{i}. {h}-{a}  ({p*100:.1f}%)\n"
        
        txt += "\nCeci est une probabilité, pas une certitude."
        bot.reply_to(message, txt)
        
    except ValueError:
        bot.reply_to(message, "❌ Mets des chiffres : /score 1.5 0.9")

print("Bot Score Exact démarré...")
bot.infinity_polling()
