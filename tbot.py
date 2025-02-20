import os
import signal
import asyncio
import logging
import sqlite3
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler,
)

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# États pour la conversation
CONFIG_MESSAGE, CONFIG_IMAGE, CONFIG_REACTION, CONFIG_DATE, CONFIG_FREQUENCY = range(5)

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
        conn.commit()
        conn.close()
        logger.info("Base de données initialisée.")

# Fonction pour sauvegarder une configuration
def save_config(key, value):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE config SET {key} = ? WHERE id = 1', (value,))
    conn.commit()
    conn.close()
    logger.info(f"Configuration '{key}' sauvegardée : {value}")

# Fonction pour récupérer une configuration
def get_config(key):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT {key} FROM config WHERE id = 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Fonction pour démarrer le bot et afficher le menu
async def start(update: Update, context: CallbackContext) -> None:
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
    await update.message.reply_text('Choisissez une option:', reply_markup=reply_markup)

# Fonction pour configurer le message
async def config_message(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Veuillez entrer votre message :')
    return CONFIG_MESSAGE

# Fonction pour configurer l'image
async def config_image(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Veuillez indiquer le chemin de l\'image :')
    return CONFIG_IMAGE

# Fonction pour configurer la réaction
async def config_reaction(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Ajoutez des boutons emojis :')
    return CONFIG_REACTION

# Fonction pour configurer la date
async def config_date(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Entrez la date et l\'heure de début des publications (format: YYYY-MM-DD HH:MM) :')
    return CONFIG_DATE

# Fonction pour configurer la fréquence
async def config_frequency(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Choisissez combien de publications par jour seront envoyées :')
    return CONFIG_FREQUENCY

# Fonction pour publier immédiatement
async def publish_now(update: Update, context: CallbackContext) -> None:
    save_config('published', 1)
    await update.message.reply_text('Publication immédiate effectuée.')

# Fonction pour afficher toutes les configurations
async def show_config(update: Update, context: CallbackContext) -> None:
    config = {
        'message': get_config('message'),
        'image_path': get_config('image_path'),
        'reaction': get_config('reaction'),
        'start_date': get_config('start_date'),
        'frequency': get_config('frequency'),
        'published': get_config('published'),
    }
    response = (
        f"📝 Message : {config['message']}\n"
        f"🖼️ Image : {config['image_path']}\n"
        f"🎉 Réaction : {config['reaction']}\n"
        f"📅 Date de début : {config['start_date']}\n"
        f"⏱️ Fréquence : {config['frequency']} publications/jour\n"
        f"🚀 Publié : {'Oui' if config['published'] else 'Non'}"
    )
    await update.message.reply_text(response)

# Fonction pour maintenir l'activité du bot
async def keep_alive(context: CallbackContext) -> None:
    logger.info("Bot actif à %s", datetime.now())

# Fonction principale asynchrone
async def main() -> None:
    # Initialiser la base de données
    init_db()

    # Récupérer le token du bot Telegram depuis les variables d'environnement
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("Le token Telegram n'est pas défini. Veuillez définir la variable d'environnement TELEGRAM_TOKEN.")
        return

    # Créer l'application Telegram
    application = Application.builder().token(token).build()

    # Ajouter les gestionnaires de commandes et de messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Configurer JobQueue pour maintenir l'activité
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(keep_alive, interval=600, first=0)  # Toutes les 10 minutes

    # Gestion des interruptions
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} reçu. Arrêt du bot...")
        stop_event.set()

    # Enregistrer les gestionnaires de signaux
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler, sig, None)

    # Démarrage du bot
    logger.info("Démarrage du bot...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Attendre un signal d'arrêt
    await stop_event.wait()

    # Arrêt propre du bot
    logger.info("Arrêt du bot...")
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du bot : {e}")
