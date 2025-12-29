# 🏎️ Race Query

Race Query est une petite app web permettant de suivre les saisons de Formule 1 de 2022 jusqu'à aujourd'hui. Que vous soyez un passionné, un néophyte ou tout simplement curieux, Race Query transforme la complexité des données de course en analyses visuelles intuitives et accessibles à tous.

## ⚙️ Fonctionnalités
- **Classement championnat Pilote et Constructeur** : Suivez l'évolution des points et des positions de la saison.
- **Calendrier et résultat** : Accès aux résultats des séances ou aux programmes des week-end (Essais libres, Qualification, Sprint et Grand-Prix).
- **Statistiques** : Fiches détaillées de la saison des pilotes et des écuries (résultats des courses des pilotes, nombre de pole position, de victoire etc..).

## 🔜 Fonctionnalités à venir
- **Face à Face Pilotes 🆚** : Comparaison des statistiques de la saison entre deux pilotes (Qui est meilleur en course, en qualif etc...).
- **Evolution au classement 📈** : Graphique permettant de visualiser l'évolution au classement course après course.
- **Stratégie de course 🔍** : Analyse et comparaison des différentes stratégies de course (visualisation des relais de course,analyse du rythme...).
- **What if 🔮** : Supprimez un pilote ou une écurie et voyez si l'issue du championnat reste la même.

## 🛠️ Stack Technique
- **Frontend** : Angular 20+, TypeScript, HTML, CSS
- **Backend** : Flask (Python), FastF1 API, Pandas

## 🚀 Installation et Démarrage
### Prérequis
- **Python 3.11+**

### Installation
1. Clôner le dépôt :

   ```bash
   https://github.com/bsy44/RaceQuery.git
   ```
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer les scripts dans l'ordre suivant pour charger les données :
   ```bash
   # Récupérer les Pilotes et les écuries
   python -m scripts.preprocess_drivers_and_teams.py

   # Récupérer le calendrier et les classements
   python -m scripts.preprocess_ergast.py

   # Récupérer les résultats des sessions
   python -m scripts.preprocess_fastf1_sessions.py

   # Récupérer les stats des pilotes et écuries
   python -m scripts.preprocess_fastf1_sessions.py
   ```

4. Lancement du serveur API
   ```bash
   python app.py
   ```
 L'API sera disponible sur `http://127.0.0.1:5000`.

## Principales Routes
 **Methode**  |    **Endpoint**    |  **Description**  
 --- | --- | --- |
  `GET`      |  `/drivers/<year>` |   Retourne la liste complète des pilotes d'une saison
  `GET`      |  `/drivers/<year>/standings` |   Retourne le classement pilote d'une saison
  `GET`      |  `/teams/<year>` |   Retourne la liste complète des écuries d'une saison
  `GET`      |  `/teams/<year>/standings` |   Retourne le classement constructeur d'une saison  
  `GET`      |  `/races/<year>` |   Retourne le calendrier d'une saison
  `GET`      |  `/races/<year>/<round>` |   Retourne les détails d'un weekend de course
  `GET`      |  `/races/<year>/<round>/<session>` |   Retourne les résultats d'une session

---

## 📄 Licence & Données
Projet réalisé dans un cadre personnel et pédagogique. Les données sont issues de la librairie [FastF1](https://docs.fastf1.dev/index.html).
