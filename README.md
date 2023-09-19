# Application web du Club BDManga

## Installer en local

 - `git clone https://github.com/Lysquid/ClubBDManga`
 - `python -m venv env`
 - `source env/bin/activate`
 - `pip install -r requirements.txt`
 - installer `mariadb` ou `mysql` (les deux sont interchangeables)
 - `mariadb -u root -p -e "create database BDMANGA"`
 - définir la variable d'environnement `BDMANGA_DB_PASSWORD` avec le mot de passe de la base de donnée
 - `python manage.py migrate`
 - `python manage.py createsuperuser` (optionnel, pour avoir le site admin)
 - `python manage.py runserver`

## Base de données

### Backup

`mariadb-dump -u root -p -D BDMANGA > dump.sql`

### Réstaurer une backup

`mariadb -u root -p -D BDMANGA < dump.sql`

## Déploiement

La première fois, il faut générer un certificat ssl signé à la main pour que nginx puisse démarrer, avec la commande :

`docker run -p80:80 -v/etc/letsencrypt/:/etc/letsencrypt/ certbot/certbot certonly --email <email> --domain <domain> --standalone --non-interactive --agree-tos`