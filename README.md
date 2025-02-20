# Telegram Bot pour la gestion de publications

Ce projet est un bot Telegram qui permet de configurer et de gérer des publications automatisées. Il offre une interface simple pour définir un message, une image, des réactions, une date de début, une fréquence de publication, et bien plus encore. Les configurations sont stockées dans une base de données SQLite, ce qui permet aux utilisateurs de récupérer et de modifier leurs paramètres à tout moment.

## Fonctionnalités

- **📌 Configurer un message** : Définissez le texte de votre publication.
- **🖼️ Configurer une image** : Ajoutez une image à votre publication.
- **🎉 Configurer des réactions** : Ajoutez des boutons emojis pour interagir avec vos publications.
- **📅 Configurer une date de début** : Planifiez la date et l'heure de début des publications.
- **⏱️ Configurer la fréquence** : Choisissez combien de publications seront envoyées par jour.
- **🚀 Publier immédiatement** : Envoyez une publication immédiatement.
- **📂 Voir toutes les configurations** : Récupérez l'ensemble des configurations enregistrées.
- **💾 Base de données SQLite** : Toutes les configurations sont sauvegardées dans une base de données pour une récupération et une modification faciles.

## Prérequis

- Python 3.7 ou supérieur
- Bibliothèque `python-telegram-bot`
- Un token de bot Telegram (obtenu via [BotFather](https://core.telegram.org/bots#botfather))

## Installation

1. Clonez ce dépôt :
   ```bash
   https://github.com/Mega-one/Telegram-Bot-.git
   cd telegram-bot-publications
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez votre token Telegram :
   - Renommez le fichier `.env.example` en `.env`.
   - Ajoutez votre token Telegram dans le fichier `.env` :
     ```
     TELEGRAM_TOKEN=votre_token_ici
     ```

4. Lancez le bot :
   ```bash
   python bot.py
   ```

## Déploiement sur Render

1. Créez un nouveau service Web sur [Render](https://render.com).
2. Liez votre dépôt Git.
3. Ajoutez la variable d'environnement `TELEGRAM_TOKEN` avec votre token Telegram.
4. Définissez la commande de démarrage :
   ```bash
   python bot.py
   ```
5. Déployez !

## Utilisation

1. Démarrez le bot avec la commande `/start`.
2. Utilisez le menu pour configurer vos publications.
3. Visualisez ou modifiez vos configurations à tout moment.

## Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce projet, suivez ces étapes :

1. Forkez ce dépôt.
2. Créez une nouvelle branche (`git checkout -b feature/nouvelle-fonctionnalite`).
3. Committez vos changements (`git commit -am 'Ajouter une nouvelle fonctionnalité'`).
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`).
5. Ouvrez une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

### Exemple de fichier `.env.example`

```plaintext
# Exemple de fichier .env
TELEGRAM_TOKEN=votre_token_ici
```
