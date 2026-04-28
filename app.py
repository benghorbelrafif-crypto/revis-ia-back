import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

# Configuration du client Groq via la variable d'environnement
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "🚀 Le serveur Révis'IA est en ligne et prêt !"

@app.route('/generer', methods=['POST'])
def generer():
    data = request.json
    cours = data.get('cours')

    if not cours:
        return jsonify({"error": "Aucun texte fourni"}), 400

    try:
        # Appel à l'IA Llama 3
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=6000,
            messages=[
                {
                    "role": "system", 
                    "content": "Tu es un assistant pédagogique expert. Ton format de réponse est TOUJOURS un JSON pur."
                },
                {
                    "role": "user", 
                    "content": f"""
                    Analyse ce cours : {cours}
                    Génère un objet JSON avec :
                    1. 'resume' : Un résumé détaillé et structuré.
                    2. 'flashcards' : Liste d'objets (question/reponse).
                    3. 'quiz' : QCM avec 'question', 'options' (4 choix), et 'reponse_correcte'.
                    """
                }
            ],
            response_format={"type": "json_object"}
        )
        
        reponse_brute = completion.choices[0].message.content
        reponse_ia = json.loads(reponse_brute)
        
        return jsonify(reponse_ia)
        
    except Exception as e:
        print(f"Erreur détectée : {e}")
        return jsonify({
            "error": str(e),
            "resume": "Désolé, une erreur est survenue.",
            "flashcards": [],
            "quiz": []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)