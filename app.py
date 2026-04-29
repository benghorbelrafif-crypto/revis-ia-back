import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

# =========================
# CONFIG
# =========================
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = Flask(__name__)
CORS(app)

# =========================
# ROUTES
# =========================
@app.route('/')
def home():
    return "🚀 Révis'IA est en ligne !"

@app.route('/generer', methods=['POST'])
def generer():
    data = request.json
    cours = data.get('cours', '').strip()

    if not cours:
        return jsonify({"error": "Aucun texte fourni"}), 400

    try:
        # =========================
        # APPEL IA
        # =========================
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=4000,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant pédagogique expert. "
                        "Tu dois répondre UNIQUEMENT en JSON valide, sans aucun texte autour. "
                        "Tu structures les cours pour aider à réviser efficacement."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Analyse ce cours :

{cours}

=========================
OBJECTIF
=========================
Transformer ce cours en support de révision clair, structuré et pédagogique.

=========================
FORMAT OBLIGATOIRE
=========================

{{
  "resume": [
    {{
      "titre": "Titre de la partie",
      "resume": "Explication simple et claire de la partie",
      "points_cles": [
  "Tous les points importants du cours sous forme de liste",
  "Chaque point doit être indépendant et clair",
  "Aucun résumé global ici"
]
    }}
  ],

  "flashcards": [
    {{
      "importance": "essentiel | important | secondaire",
      "question": "Question basée sur une idée clé du cours",
      "reponse": "Réponse claire"
    }}
  ],

  "quiz": [
    {{
      "question": "Question",
      "options": ["A", "B", "C", "D"],
      "reponse_correcte": "A"
    }}
  ]
}}

=========================
REGLES IMPORTANTES
=========================

RESUME :
- Découpe le cours en parties logiques

FLASHCARDS :
- 3 niveaux d’importance OBLIGATOIRE :
  - essentiel (les notions les plus importantes du cours)
  - important
  - secondaire
- Les flashcards doivent être triées du plus important au moins important

GLOBAL :
- Pas de texte hors JSON
- Réponses simples
- Contenu pédagogique et clair
"""
                }
            ],
            response_format={"type": "json_object"}
        )

        # =========================
        # PARSING SAFE JSON
        # =========================
        reponse_brute = completion.choices[0].message.content
        reponse_ia = json.loads(reponse_brute)

        return jsonify(reponse_ia)

    except Exception as e:
        print("Erreur détectée :", e)

        return jsonify({
            "error": str(e),
            "resume": [],
            "flashcards": [],
            "quiz": []
        }), 500


# =========================
# RUN SERVER
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
