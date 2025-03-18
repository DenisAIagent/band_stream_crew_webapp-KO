import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Stockage temporaire des données (dans un environnement de production, utiliser une base de données)
data_store = {
    "trending_artists": [],
    "lookalike_artists": [],
    "campaign_insights": {},
    "ad_drafts": [],
    "optimized_campaign": {}
}

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé de l'API"""
    return jsonify({"status": "ok", "message": "API server is running"}), 200

@app.route('/store/<key>', methods=['POST'])
def store_data(key):
    """Stocke des données dans le magasin temporaire"""
    if key not in data_store:
        return jsonify({"error": f"Invalid key: {key}"}), 400
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    data_store[key] = data
    return jsonify({"status": "success", "message": f"Data stored for {key}"}), 200

@app.route('/retrieve/<key>', methods=['GET'])
def retrieve_data(key):
    """Récupère des données du magasin temporaire"""
    if key not in data_store:
        return jsonify({"error": f"Invalid key: {key}"}), 400
    
    return jsonify({"status": "success", "data": data_store[key]}), 200

@app.route('/clear/<key>', methods=['DELETE'])
def clear_data(key):
    """Efface des données du magasin temporaire"""
    if key not in data_store:
        return jsonify({"error": f"Invalid key: {key}"}), 400
    
    if key == "trending_artists":
        data_store[key] = []
    elif key == "lookalike_artists":
        data_store[key] = []
    elif key == "campaign_insights":
        data_store[key] = {}
    elif key == "ad_drafts":
        data_store[key] = []
    elif key == "optimized_campaign":
        data_store[key] = {}
    
    return jsonify({"status": "success", "message": f"Data cleared for {key}"}), 200

@app.route('/clear_all', methods=['DELETE'])
def clear_all_data():
    """Efface toutes les données du magasin temporaire"""
    data_store["trending_artists"] = []
    data_store["lookalike_artists"] = []
    data_store["campaign_insights"] = {}
    data_store["ad_drafts"] = []
    data_store["optimized_campaign"] = {}
    
    return jsonify({"status": "success", "message": "All data cleared"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
