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
            max_tokens=4500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant pédagogique expert. "
                        "Tu réponds UNIQUEMENT en JSON valide, sans texte autour. "
                        "Tu es précis, structuré et exhaustif."
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
Transformer ce cours en un outil de révision complet.

=========================
FORMAT OBLIGATOIRE
=========================

{{
  "resume": [
    {{
      "titre": "Partie du cours",
      "resume": "Explication simple et claire",
      "points_cles": [
        "Toutes les idées importantes (sans limite)",
        "Chaque point = une notion distincte"
      ]
    }}
  ],

  "flashcards": [
    {{
      "importance": "essentiel | important | secondaire",
      "question": "Question basée sur une idée du cours",
      "reponse": "Réponse claire"
    }}
  ],

  "quiz": [
    {{
      "question": "Question basée sur une idée du cours",
      "options": ["A", "B", "C", "D"],
      "reponse_correcte": "Bonne réponse (placée aléatoirement dans les options)",
      "explication": "Explication simple qui rappelle la notion du cours"
    }}
  ]
}}

=========================
REGLES IMPORTANTES
=========================

RESUME :
- Découpage logique du cours
- Toutes les notions doivent être incluses

FLASHCARDS :
- UNE flashcard par idée du cours
- Pas de limite de quantité
- Triées par importance :
  - essentiel
  - important
  - secondaire

QUIZ :
- Questions sur TOUTES les idées du cours (même petites)
- Ordre complètement mélangé
- Chaque question doit tester une idée différente
- La bonne réponse doit être placée aléatoirement dans A/B/C/D
- Chaque question doit contenir une explication pédagogique

GLOBAL :
- Aucun texte hors JSON
- Réponse structurée
- Exhaustif et pédagogique
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
