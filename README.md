# Projet LITRevu
> IMPORTANT : Ce projet n'est pas un projet de production !
> 
> Il sert uniquement en tant que POC (Proof of Concept) sur le projet 9 du
> parcours de Développeur d'Application Python d'OpenClassrooms.
---
LITRevu est une application web Django dédié à une communauté de lecteurs.
Ses utilisateurs peuvent :
- publier des demandes de critique (tickets),
- rédiger des critiques (reviews),
- suivre d’autres utilisateurs et consulter un flux personnalisé.
---
## Installation et démarrage

### Prérequis

- [Python 3.12+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads) pour cloner le dépôt
- [Poetry 2.4+](https://python-poetry.org/docs/#installation) pour installer les dépendances 
- ou bien avec le classique `pip` pour installer les dépendances

Mémo sur la vérification versions installées sur votre machine :

```bash
python --version

poetry --version

pip --version
```

### Cloner le dépôt du projet

```bash
# en version HTTPS
git clone https://github.com/Nels-J/Projet9_LITRevu.git

# en version SSH
git clone git@github.com:Nels-J/Projet9_LITRevu.git

# Naviguer dans le répertoire du projet
cd Projet9
```

### Installation avec Poetry
Installer les dépendances du projet avec `Poetry` et créer un environnement virtuel :

```bash
poetry install
```

Lancer les commandes suivantes pour créer la base de données, un superuser, puis lancer le serveur de développement :

```bash
# Créer la base de données
poetry run python manage.py migrate

# Créer un superuser pour accéder à l'interface d'administration
poetry run python manage.py createsuperuser

# Lancer le serveur de développement
poetry run python manage.py runserver
```

### Installation avec pip
Si vous préférez utiliser `pip` procédez comme suit :

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
env\Scripts\activate  # Sur Windows
source .venv/bin/activate  # Sur macOS/Linux

# Installer les dépendances de développement du projet
pip install -r requirements_dev.txt

# Installer les dépendances pour le projet sans les dépendances de développement
pip install -r requirements.txt

# Initialiser la base de données
python manage.py migrate
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver 8000
```
---
## Utilisation de l'application sur serveur local
### Accéder au backoffice de l'application
1. Accédez à l'interface via votre navigateur à l'adresse : `http://127.0.0.1:8000/admin/`
2. Connectez-vous avec le `superuser` que vous avez créé précédemment.
3. Vous pouvez maintenant gérer les utilisateurs, les tickets et les critiques via l'interface d'administration.

### Accès à l'application via votre navigateur à l'adresse : `http://127.0.0.1:8000/`
1. Connectez-vous avec le `superuser` que vous avez créé précédemment.
2. Vous pouvez maintenant créer des tickets, rédiger des critiques et suivre d'autres utilisateurs.
3. Pour vous déconnecter, cliquez sur le bouton "Se déconnecter" dans le menu de navigation.

### Créer un compte utilisateur pour tester l'application en tant qu'utilisateur régulier :
1. Cliquez sur le bouton "S'inscrire" sur la page d'accueil.
2. Remplissez le formulaire d'inscription avec vos informations personnelles.
3. Cliquez sur le bouton "S'inscrire" pour créer votre compte.
4. Vous pouvez maintenant vous connecter avec votre nouveau compte et tester l'application en tant qu'utilisateur régulier.

### S'abonner à un utilisateur pour suivre ses critiques :
1. Rendez-vous sur la page des abonnements en cliquant sur le lien "Abonnements" du menu de navigation.
2. Dans le champ de saisie insérer le nom de l'utilisateur à suivre validé en cliquant sur le bouton "Envoyer".
- Si l'utilisateur existe, il est ajouté dans la liste des abonnements.
- Si l'utilisateur n'existe pas, un message d'erreur s'affiche.
3. Vous pouvez maintenant consulter les critiques de l'utilisateur suivi dans votre flux personnalisé.
4. Pour vous désabonner, cliquez sur le bouton "Désabonner" à côté du nom de l'utilisateur dans la liste des abonnements.

### Demander une critique pour un livre :
1. Depuis la page de Flux cliquez sur le bouton "Demander une critique" pour accéder au formulaire de demande de critique.
2. Remplissez le formulaire avec les informations du livre pour lequel vous souhaitez obtenir une critique.
- Titre du livre - Auteur du livre.
- Détail de votre demande (facultatif) : vous pouvez préciser vos attentes pour la critique.
- Image de couverture (facultatif) : vous pouvez ajouter une image de couverture du livre pour illustrer votre demande.
4. Cliquez sur le bouton "Envoyer" pour soumettre votre demande de critique.

### Créer une critique pour un livre :
1. Depuis la page de Flux cliquez sur le bouton "Créer une critique" pour accéder au formulaire de création de critique.
2. Remplissez les deux parties du formulaire, celle dédiée aux détails du livre, puis la partie dédiée à la critique.
3. Cliquez sur le bouton "Envoyer" pour soumettre votre critique.

### Répondre à une demande de critique :
1. Depuis la page de Flux cliquez sur le bouton "Créer une critique" directement dans la zone du ticket.
2. Remplissez la partie Critique du formulaire.
3. Cliquez sur le bouton "Envoyer" pour soumettre votre critique en réponse à la demande.

### Modification et suppression d'un élement :
> Important seul l'auteur d'un ticket ou d'une critique peut modifier ou supprimer son élement.
1. Depuis la page de Flux ou Posts
2. Dans la zone de l'élément souhaité, cliquez sur le bouton "Modifier" ou "Supprimer".
3. Confirmez votre action si nécessaire sur la page de confirmation.

---