# Application web du Club BDManga

## Installation en local

 - `git clone https://github.com/Lysquid/ClubBDManga`
 - `python -m venv env`
 - `source env/bin/activate`
 - `pip install -r requirements.txt`
 - installer `mariadb` ou `mysql` (les deux sont interchangeables)
 - `mariadb -u root -p -e "create database BDMANGA"`
 - définir les variables d'environnement suivantes :
   - `DB_USER` l'utilisateur de la base de données, `root` ici
   - `DB_PASSWORD`
   - `DB_NAME` le nom de la base de données, `BDMANGA` ici
   - `DEBUG=1` pour faciliter le développement
 - `python manage.py migrate`
 - `python manage.py createsuperuser` (optionnel, pour avoir le site admin)
 - `python manage.py runserver`

Le docker-compose peut également être utilisé en local, en définissant les variables d'environnement dans un fichier `.env`. Cette méthode reste moins pratique pour le développement car elle a été prévue pour le déploiement.

## Base de données

Des backups journalières sont réalisées sur le VPS avec une action.

### Faire une backup

`mariadb-dump -u root -p -D BDMANGA > dump.sql`

Avec docker :

`docker exec -i clubbdmanga-db-1 mariadb-dump -u $DB_USER $DB_NAME > dump.sql`

### Réstaurer une backup

`mariadb -u root -p -D BDMANGA < dump.sql`

Avec docker :

`cat dump.sql | docker exec -i clubbdmanga-db-1 mariadb -u $DB_USER --password=$DB_PASSWORD $DB_NAME`

## Déploiement

Le déploiement se fait automatiquement sur le VPS hébergeant le runner à chaque push sur `main`, ou en lançant manuellement l'action. Il y a une autre action pour arrêter l'application.
