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
            temperature=0.4,
            max_tokens=4000,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant pédagogique expert. "
                        "Tu dois répondre UNIQUEMENT en JSON valide, sans texte autour."
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

Transforme ce cours en un JSON structuré pour révision.

=========================
FORMAT OBLIGATOIRE
=========================

{{
  "resume": [
    {{
      "titre": "Titre de la partie",
      "resume": "Explication claire et simple de la partie",
      "points_cles": [
        "Point important 1",
        "Point important 2",
        "Point important 3"
      ]
    }}
  ],
  "flashcards": [
    {{
      "question": "Question",
      "reponse": "Réponse"
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
- Découpe le cours en VRAIES parties logiques
- "resume" DOIT être une liste
- Pas de texte hors JSON
- Réponses simples et pédagogiques
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
