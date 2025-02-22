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
   )
from aiohttp import web

   # Configuration des logs
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
   )
   logger = logging.getLogger(__name__)

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

   # Fonction pour gérer les messages
async def handle_message(update: Update, context: CallbackContext) -> None:
       text = update.message.text
       if text == '📌 Configurer message':
           await update.message.reply_text('Veuillez entrer votre message :')
           context.user_data['awaiting_input'] = 'message'
       elif text == '📌 Configurer Image':
           await update.message.reply_text('Veuillez indiquer le chemin de l\'image :')
           context.user_data['awaiting_input'] = 'image_path'
       elif text == '📌 Configurer réaction':
           await update.message.reply_text('Ajoutez des boutons emojis :')
           context.user_data['awaiting_input'] = 'reaction'
       elif text == '📌 Configurer Date':
           await update.message.reply_text('Entrez la date et l\'heure de début des publications (format: YYYY-MM-DD HH:MM) :')
           context.user_data['awaiting_input'] = 'start_date'
       elif text == '📌 Configurer Fréquence':
           await update.message.reply_text('Choisissez combien de publications par jour seront envoyées :')
           context.user_data['awaiting_input'] = 'frequency'
       elif text == '📌 Configurer Publié':
           await publish_now(update, context)
       elif text == '📌 Voir toutes les configurations':
           await show_config(update, context)
       else:
           key = context.user_data.get('awaiting_input')
           if key:
               save_config(key, text)
               await update.message.reply_text(f'Configuration "{key}" validée : {text}')
               context.user_data['awaiting_input'] = None

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
       token = os.getenv("TELEGRAM_TOKEN")
       if not token:
           logger.error("Le token Telegram n'est pas défini. Veuillez définir la variable d'environnement TELEGRAM_TOKEN.")
           return

       # Créer l'application Telegram avec drop_pending_updates=True
       application = Application.builder().token(token).build()
       await application.initialize()
       await application.start()
       await application.updater.start_polling(drop_pending_updates=True)  # Ignorer les mises à jour en attente

       # Démarrer un serveur HTTP factice pour satisfaire Render
       app = web.Application()
       runner = web.AppRunner(app)
       await runner.setup()
       site = web.TCPSite(runner, '0.0.0.0', 8080)  # Écouter sur le port 8080
       await site.start()
       logger.info("Serveur HTTP factice démarré sur le port 8080.")

       # Gestion des interruptions
       loop = asyncio.get_event_loop()
       stop_event = asyncio.Event()

       def signal_handler(signum, frame):
           logger.info(f"Signal {signum} reçu. Arrêt du bot...")
           stop_event.set()

       # Enregistrer les gestionnaires de signaux
       for sig in (signal.SIGTERM, signal.SIGINT):
           loop.add_signal_handler(sig, signal_handler, sig, None)

       # Attendre un signal d'arrêt
       await stop_event.wait()

       # Arrêt propre du bot
       logger.info("Arrêt du bot...")
       await application.updater.stop()
       await application.stop()
       await application.shutdown()
       await runner.cleanup()

if __name__ == '__main__':
       try:
           asyncio.run(main())
       except Exception as e:
           logger.error(f"Erreur lors de l'exécution du bot : {e}")
