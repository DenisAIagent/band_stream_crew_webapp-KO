import os
import json
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API centrale
API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://api_server:5000')

# Configuration des autres services
ANALYST_URL = os.getenv('ANALYST_URL', 'http://campaign_analyst:5001')
OPTIMIZER_URL = os.getenv('OPTIMIZER_URL', 'http://campaign_optimizer:5002')
MARKETING_URL = os.getenv('MARKETING_URL', 'http://marketing_agents:5003')

app = Flask(__name__, template_folder='templates')

def clear_all_data():
    """
    Efface toutes les données stockées dans l'API centrale
    """
    try:
        requests.delete(f"{API_SERVER_URL}/clear_all")
    except Exception as e:
        print(f"Erreur lors de l'effacement des données: {e}")

def run_campaign_workflow(artist_name, music_style, song, lyrics, bio):
    """
    Exécute le workflow complet de la campagne
    """
    results = {
        "status": "success",
        "artist_name": artist_name,
        "music_style": music_style,
        "campaign_insights": {},
        "optimized_campaign": {},
        "ad_drafts": [],
        "errors": []
    }
    
    # Étape 1: Analyser les tendances et trouver des artistes similaires
    try:
        analyst_data = {
            "artist_name": artist_name,
            "music_style": music_style
        }
        
        analyst_response = requests.post(
            f"{ANALYST_URL}/analyze",
            json=analyst_data
        )
        
        if analyst_response.status_code == 200:
            analyst_result = analyst_response.json()
            if "data" in analyst_result:
                results["campaign_insights"] = analyst_result["data"]
        else:
            results["errors"].append(f"Erreur lors de l'analyse des tendances: {analyst_response.status_code}")
    except Exception as e:
        results["errors"].append(f"Erreur lors de l'analyse des tendances: {str(e)}")
    
    # Étape 2: Optimiser la campagne
    try:
        optimizer_response = requests.post(
            f"{OPTIMIZER_URL}/optimize",
            json={}  # Les données sont récupérées depuis l'API centrale
        )
        
        if optimizer_response.status_code == 200:
            optimizer_result = optimizer_response.json()
            if "data" in optimizer_result:
                results["optimized_campaign"] = optimizer_result["data"]
        else:
            results["errors"].append(f"Erreur lors de l'optimisation de la campagne: {optimizer_response.status_code}")
    except Exception as e:
        results["errors"].append(f"Erreur lors de l'optimisation de la campagne: {str(e)}")
    
    # Étape 3: Générer des drafts d'annonces
    try:
        marketing_data = {
            "artist_name": artist_name,
            "music_style": music_style,
            "song": song,
            "lyrics": lyrics,
            "bio": bio
        }
        
        marketing_response = requests.post(
            f"{MARKETING_URL}/generate_ads",
            json=marketing_data
        )
        
        if marketing_response.status_code == 200:
            marketing_result = marketing_response.json()
            if "data" in marketing_result:
                results["ad_drafts"] = marketing_result["data"]
        else:
            results["errors"].append(f"Erreur lors de la génération des annonces: {marketing_response.status_code}")
    except Exception as e:
        results["errors"].append(f"Erreur lors de la génération des annonces: {str(e)}")
    
    return results

@app.route('/')
def index():
    """
    Page d'accueil avec formulaire
    """
    return render_template('index.html')

@app.route('/campaign', methods=['POST'])
def create_campaign():
    """
    Traite le formulaire et lance le workflow de la campagne
    """
    # Récupérer les données du formulaire
    artist_name = request.form.get('artist_name', '')
    music_style = request.form.get('music_style', '')
    song = request.form.get('song', '')
    lyrics = request.form.get('lyrics', '')
    bio = request.form.get('bio', '')
    
    if not artist_name:
        return render_template('index.html', error="Le nom de l'artiste est requis")
    
    # Effacer les données précédentes
    clear_all_data()
    
    # Exécuter le workflow
    results = run_campaign_workflow(artist_name, music_style, song, lyrics, bio)
    
    # Afficher les résultats
    return render_template(
        'results.html',
        artist_name=artist_name,
        music_style=music_style,
        campaign_insights=results.get("campaign_insights", {}),
        optimized_campaign=results.get("optimized_campaign", {}),
        ad_drafts=results.get("ad_drafts", []),
        errors=results.get("errors", [])
    )

@app.route('/health')
def health_check():
    """
    Endpoint de vérification de santé
    """
    return jsonify({"status": "ok", "message": "Campaign Supervisor service is running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=True)
