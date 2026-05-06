import os # Importation du module pour interagir avec le système d'exploitation (clés d'API, ports)
import json # Importation du module pour manipuler les données au format JSON
from flask import Flask, request, jsonify # Importation des composants de Flask pour créer l'API et gérer les requêtes
from flask_cors import CORS # Importation pour autoriser les requêtes provenant d'autres domaines (ton front-end)
from groq import Groq # Importation du client officiel pour utiliser l'IA de Groq

# =========================
# CONFIG
# =========================
client = Groq(api_key=os.environ.get("GROQ_API_KEY")) # Initialisation du client Groq avec la clé d'API stockée en variable d'environnement

app = Flask(__name__) # Création de l'instance de l'application Flask
CORS(app) # Activation du CORS pour que ton interface Barbie puisse communiquer avec ce serveur

# =========================
# ROUTES
# =========================
@app.route('/') # Définition de la route racine (URL de base)
def home(): # Fonction exécutée quand on accède à la racine
    return "🚀 Révis'IA est en ligne !" # Message simple pour vérifier que le serveur tourne

@app.route('/generer', methods=['POST']) # Définition de la route /generer accessible uniquement en méthode POST
def generer(): # Fonction principale qui gère la création des révisions
    data = request.json # Récupération des données envoyées par le front-end au format JSON
    cours = data.get('cours', '').strip() # Extraction du texte du cours et suppression des espaces inutiles

    if not cours: # Vérification si le texte envoyé est vide
        return jsonify({"error": "Aucun texte fourni"}), 400 # Retourne une erreur 400 si rien n'a été envoyé

    try: # Début du bloc de test pour capturer les erreurs potentielles
        completion = client.chat.completions.create( # Appel à l'API Groq pour générer le contenu
            model="llama-3.3-70b-versatile", # Choix du modèle d'intelligence artificielle
            temperature=0.3, # Réglage de la créativité (0.3 = réponses précises et stables)
            max_tokens=4500, # Limite maximale de la taille de la réponse de l'IA
            messages=[ # Liste des messages envoyés à l'IA pour définir son rôle et sa tâche
                {
                    "role": "system", # Définition du comportement de base de l'IA
                    "content": (
                        "Tu es un professeur expert en pédagogie. "
                        "Tu réponds UNIQUEMENT en JSON valide sans texte autour."
                    )
                },
                {
                    "role": "user", # Envoi de la commande spécifique avec le texte du cours
                    "content": f"""
Analyse ce cours et transforme-le en outil de révision EXCELLENT.

=========================
OBJECTIF
=========================
Extraire les 15 notions LES PLUS IMPORTANTES du cours (du plus important au moins important).

=========================
FORMAT OBLIGATOIRE
=========================

{{
  "resume": [
    {{
      "titre": "Partie du cours",
      "resume": "Explication simple et claire",
      "points_cles": ["..."]
    }}
  ],

  "flashcards": [
    {{
      "importance": "essentiel | important | secondaire",
      "question": "Question claire basée sur une idée du cours",
      "reponse": "Réponse simple et pédagogique"
    }}
  ],

  "quiz": [
    {{
      "question": "Question de compréhension sur une notion du cours",
      "options": ["A", "B", "C", "D"],
      "reponse_correcte": "Bonne réponse",
      "contexte_cours": "Extrait ou explication du cours qui permet de comprendre la notion",
      "explication": "Explication pédagogique simple"
    }}
  ]
}}

=========================
REGLES IMPORTANTES
=========================

FLASHCARDS :
- EXACTEMENT 15 flashcards
- Du plus important au moins important
- Une seule idée par flashcard

QUIZ :
- EXACTEMENT 15 questions
- Chaque question teste une notion différente
- La bonne réponse doit être mélangée
- IMPORTANT : ajouter "contexte_cours"
  -> partie du cours qui explique la réponse
  -> doit aider à comprendre la question

RESUME :
- structuré
- simplifié
- uniquement idées importantes

=========================
COURS :
{cours}
"""
                }
            ],
            response_format={"type": "json_object"} # Force l'IA à répondre avec un objet JSON propre
        )

        reponse_brute = completion.choices[0].message.content # Extraction du texte brut de la réponse de l'IA
        reponse_ia = json.loads(reponse_brute) # Conversion de la chaîne de caractères JSON en dictionnaire Python

        return jsonify(reponse_ia) # Renvoi du résultat final au front-end au format JSON

    except Exception as e: # Bloc exécuté en cas d'erreur (problème API, JSON mal formé, etc.)
        print("Erreur détectée :", e) # Affichage de l'erreur dans la console du serveur

        return jsonify({ # Renvoi d'un objet vide avec l'erreur pour éviter que le front-end ne plante
            "error": str(e),
            "resume": [],
            "flashcards": [],
            "quiz": []
        }), 500 # Code erreur 500 pour indiquer un problème côté serveur


# =========================
# RUN SERVER
# =========================
if __name__ == '__main__': # Vérifie si le script est lancé directement
    port = int(os.environ.get("PORT", 10000)) # Récupère le port de Render (par défaut 10000)
    app.run(host='0.0.0.0', port=port) # Démarre le serveur Flask sur l'adresse IP publique et le port défini
