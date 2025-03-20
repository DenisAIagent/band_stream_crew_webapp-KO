from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# Simuler une base de données en mémoire
DATA_STORE = {
    "trending_artists": [],
    "lookalike_artists": [],
    "campaign_insights": {},
    "ad_draft": [],
    "optimized_campaign": {}
}

# Route pour vérifier la santé du serveur
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "success",
        "message": "API Server is running"
    }), 200

# Route pour stocker des données
@app.route('/store/<key>', methods=['POST'])
def store_data(key):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Vérifier si la clé est valide
    if key not in DATA_STORE:
        return jsonify({"error": f"Invalid key: {key}"}), 400

    # Stocker les données en fonction de la clé
    if key in ["trending_artists", "lookalike_artists"]:
        DATA_STORE[key] = data.get("artists", [])
    elif key == "campaign_insights":
        DATA_STORE[key] = data.get("insights", {})
    elif key == "ad_draft":
        DATA_STORE[key] = data.get("drafts", [])
    elif key == "optimized_campaign":
        DATA_STORE[key] = data.get("campaign", {})

    return jsonify({
        "status": "success",
        "message": f"Data stored for {key}"
    }), 200

# Route pour récupérer des données
@app.route('/get/<key>', methods=['GET'])
def get_data(key):
    if key not in DATA_STORE:
        return jsonify({"error": f"Invalid key: {key}"}), 400

    return jsonify({
        "status": "success",
        "data": DATA_STORE[key]
    }), 200

# Route pour effacer toutes les données
@app.route('/clear_all_data', methods=['DELETE'])
def clear_all_data():
    DATA_STORE["trending_artists"] = []
    DATA_STORE["lookalike_artists"] = []
    DATA_STORE["campaign_insights"] = {}
    DATA_STORE["ad_draft"] = []
    DATA_STORE["optimized_campaign"] = {}

    return jsonify({
        "status": "success",
        "message": "All data cleared"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
