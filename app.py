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
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=4500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un professeur expert en pédagogie. "
                        "Tu réponds UNIQUEMENT en JSON valide sans texte autour."
                    )
                },
                {
                    "role": "user",
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
            response_format={"type": "json_object"}
        )

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
