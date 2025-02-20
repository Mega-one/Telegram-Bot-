from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, JobQueue
import sqlite3
import os
from datetime import datetime

# Initialisation de la base de données
def init_db():
    if not os.path.exists('config.db'):
        conn = sqlite3.connect('config.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                image_path TEXT,
                reaction TEXT,
                start_date TEXT,
                frequency INTEGER,
                published BOOLEAN DEFAULT 0
            )
        ''')
        # Insérer une ligne vide si la table est vide
        cursor.execute('INSERT OR IGNORE INTO config (id) VALUES (1)')
        conn.commit()
        conn.close()

# Fonction pour sauvegarder une configuration
def save_config(key, value):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE config SET {key} = ? WHERE id = 1', (value,))
    conn.commit()
    conn.close()

# Fonction pour récupérer toutes les configurations
def get_all_config():
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('SELECT message, image_path, reaction, start_date, frequency, published FROM config WHERE id = 1')
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'message': result[0],
            'image_path': result[1],
            'reaction': result[2],
            'start_date': result[3],
            'frequency': result[4],
            'published': result[5]
        }
    return None

# Fonction pour démarrer le bot et afficher le menu
def start(update: Application, context: CallbackContext) -> None:
    menu_options = [
        ['📌 Configurer message'],
        ['📌 Configurer Image'],
        ['📌 Configurer réaction'],
        ['📌 Configurer Date'],
        ['📌 Configurer Fréquence'],
        ['📌 Configurer Publié'],
        ['📌 Voir toutes les configurations']
    ]
    reply_markup = ReplyKeyboardMarkup(menu_options, one_time_keyboard=True)
    application.message.reply_text('Choisissez une option:', reply_markup=reply_markup)

# Fonction pour gérer les messages textuels
def handle_message(application: Application, context: CallbackContext) -> None:
    text = application.message.text
    if text == '📌 Configurer message':
        application.message.reply_text('Veuillez entrer votre message')
        context.user_data['awaiting_input'] = 'message'
    elif text == '📌 Configurer Image':
        application.message.reply_text('Veuillez indiquer le chemin de l\'image')
        context.user_data['awaiting_input'] = 'image_path'
    elif text == '📌 Configurer réaction':
        application.message.reply_text('Ajoutez des boutons emojis')
        context.user_data['awaiting_input'] = 'reaction'
    elif text == '📌 Configurer Date':
        application.message.reply_text('Entrez la date et l\'heure de début des publications (format: YYYY-MM-DD HH:MM)')
        context.user_data['awaiting_input'] = 'start_date'
    elif text == '📌 Configurer Fréquence':
        application.message.reply_text('Choisissez combien de publications par jour seront envoyées')
        context.user_data['awaiting_input'] = 'frequency'
    elif text == '📌 Configurer Publié':
        application.message.reply_text('Publication immédiate')
        save_config('published', 1)
        application.message.reply_text('Publication validée.')
    elif text == '📌 Voir toutes les configurations':
        config = get_all_config()
        if config:
            response = (
                f"📝 Message : {config['message']}\n"
                f"🖼️ Image : {config['image_path']}\n"
                f"🎉 Réaction : {config['reaction']}\n"
                f"📅 Date de début : {config['start_date']}\n"
                f"⏱️ Fréquence : {config['frequency']} publications/jour\n"
                f"🚀 Publié : {'Oui' if config['published'] else 'Non'}"
            )
            application.message.reply_text(response)
        else:
            application.message.reply_text('Aucune configuration trouvée.')
    else:
        key = context.user_data.get('awaiting_input')
        if key:
            save_config(key, text)
            application.message.reply_text(f'Configuration "{key}" validée: {text}')
            context.user_data['awaiting_input'] = None

# Fonction pour maintenir l'activité du bot
def keep_alive(context: CallbackContext):
    print("Bot actif à", datetime.now())

def main() -> None:
    # Initialiser la base de données
    init_db()

    # Remplacez 'YOUR_TOKEN' par votre token de bot Telegram
    application = Application.builder().token("BOT_TOKEN").build()

    # Ajouter les gestionnaires de commandes et de messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Ajouter une tâche périodique pour maintenir l'activité
    job_queue = application.job_queue
    job_queue.run_repeating(keep_alive, interval=600, first=0)  # Toutes les 10 minutes

    # Démarrage du bot
    await application.run_polling()

if __name__ == '__main__':
       import asyncio
       asyncio.run(main())
