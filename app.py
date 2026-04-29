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
                        "Tu dois répondre UNIQUEMENT en JSON valide, sans texte autour. "
                        "Tu es extrêmement précis et complet."
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
Transformer ce cours en support de révision COMPLET, STRUCTURÉ et EXHAUSTIF.

=========================
FORMAT OBLIGATOIRE
=========================

{{
  "resume": [
    {{
      "titre": "Nom de la partie du cours",
      "resume": "Explication claire, détaillée mais simple",
      "points_cles": [
        "Tous les points importants de cette partie",
        "Aucune limite de nombre",
        "Chaque point = une idée distincte"
      ]
    }}
  ],

  "flashcards": [
    {{
      "importance": "essentiel | important | secondaire",
      "question": "Question basée sur UNE idée du cours",
      "reponse": "Réponse claire et complète"
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
- Toutes les notions doivent apparaître

FLASHCARDS :
- UNE flashcard par idée du cours (aucune limite)
- Couvrir 100% du cours
- Trier par importance :
  - essentiel = notions indispensables
  - important = notions utiles
  - secondaire = détails / exemples

GLOBAL :
- Aucun texte hors JSON
- Réponse structurée et pédagogique
- Ne pas résumer trop fortement
- Être exhaustif
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
