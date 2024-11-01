# Arcane Studio

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-3.2%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Arcane Studio est une collection d'outils de productivité construits sur le [Arcane Engine](https://arcane.engineer/engine). Le moteur exécute des instructions en langage naturel (Tâches) au nom des utilisateurs en utilisant ses capacités, qui incluent la lecture, l'écriture et l'édition de code et l'interaction avec des problèmes, des tickets, des wikis, etc. via des intégrations.

## 🛠️ Stack
- **Backend** : Python et Django
- **Frontend** : Modèles Django, BulmaCSS et jQuery

## 🐳 Démarrage rapide avec Docker
Vous pouvez utiliser Docker pour exécuter le projet localement. Assurez-vous d'avoir Docker installé sur votre machine.

```shell
git clone https://github.com/arc-eng/studio.git
cd studio
docker-compose up --build
```

## 🚀 Installation et Configuration

### Prérequis
- Python 3.8+

### Installation
1. Clonez le dépôt :
   ```sh
   git clone https://github.com/arc-eng/studio.git
   ```
2. Accédez au répertoire du projet :
   ```sh
   cd studio
   ```
3. Installez les dépendances :
   ```sh
   poetry install
   ```
4. Appliquez les migrations :
   ```sh
   python manage.py migrate
   ```
5. Exécutez le serveur de développement :
   ```sh
   python manage.py runserver
   ```

## 🤝 Contribuer
Les contributions sont les bienvenues ! Veuillez lire d'abord les [directives de contribution](CONTRIBUTING.md).

## 📄 Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📧 Contact
Pour toute demande, veuillez nous contacter à [support@arcane.engineer](mailto:support@arcane.engineer).
