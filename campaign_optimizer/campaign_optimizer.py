import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API centrale
API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://api_server:5000')

app = Flask(__name__)

def optimize_campaign(insights):
    """
    Optimise les insights pour suggérer des stratégies marketing
    """
    if not insights:
        return {
            "status": "error",
            "message": "Aucun insight disponible pour optimisation"
        }
    
    # Initialiser les stratégies
    strategies = {
        "youtube_promotion": [],
        "lookalike_targeting": [],
        "trending_keywords": [],
        "platform_focus": []
    }
    
    # Optimiser les vidéos YouTube
    if "youtube_trends" in insights and insights["youtube_trends"]:
        youtube_videos = insights["youtube_trends"]
        strategies["youtube_promotion"] = [
            {
                "action": "Promouvoir cette vidéo YouTube",
                "title": video.get("title", ""),
                "link": video.get("link", ""),
                "views": video.get("views", ""),
                "reason": "Contenu populaire lié à l'artiste"
            }
            for video in youtube_videos[:3]  # Limiter aux 3 meilleures vidéos
        ]
    
    # Optimiser le ciblage Lookalike
    if "lookalike_artists" in insights and insights["lookalike_artists"]:
        lookalike_artists = insights["lookalike_artists"]
        strategies["lookalike_targeting"] = [
            {
                "action": "Cibler les fans de cet artiste similaire",
                "artist": artist.get("name", ""),
                "score": artist.get("score", 0),
                "reason": f"Artiste similaire avec une forte audience ({', '.join(artist.get('sources', []))})"
            }
            for artist in lookalike_artists
        ]
    
    # Extraire des mots-clés tendance
    keywords = []
    if "music_style" in insights:
        keywords.append(insights["music_style"])
    
    if "google_trends" in insights and insights["google_trends"]:
        # Extraire des mots-clés des tendances Google
        for trend in insights["google_trends"][:5]:
            if isinstance(trend, dict) and "query" in trend:
                keywords.append(trend["query"])
    
    strategies["trending_keywords"] = [
        {
            "action": "Utiliser ce mot-clé dans les campagnes",
            "keyword": keyword,
            "reason": "Mot-clé pertinent et en tendance"
        }
        for keyword in keywords if keyword
    ]
    
    # Recommandations de plateformes
    platform_scores = {
        "spotify": 0,
        "deezer": 0,
        "youtube": 0
    }
    
    # Évaluer l'importance de chaque plateforme
    if "spotify_similar" in insights and insights["spotify_similar"]:
        platform_scores["spotify"] = len(insights["spotify_similar"]) * 10
    
    if "deezer_similar" in insights and insights["deezer_similar"]:
        platform_scores["deezer"] = len(insights["deezer_similar"]) * 10
    
    if "youtube_trends" in insights and insights["youtube_trends"]:
        platform_scores["youtube"] = len(insights["youtube_trends"]) * 15
    
    # Trier les plateformes par score
    sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
    
    strategies["platform_focus"] = [
        {
            "action": f"Concentrer les efforts sur {platform.upper()}",
            "platform": platform,
            "score": score,
            "reason": f"Plateforme avec la plus grande visibilité pour cet artiste"
        }
        for platform, score in sorted_platforms if score > 0
    ]
    
    # Créer la campagne optimisée
    optimized_campaign = {
        "artist_name": insights.get("artist_name", ""),
        "music_style": insights.get("music_style", ""),
        "strategies": strategies,
        "summary": f"Campagne optimisée pour {insights.get('artist_name', '')} ({insights.get('music_style', '')})"
    }
    
    return optimized_campaign

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé"""
    return jsonify({"status": "ok", "message": "Campaign Optimizer service is running"}), 200

@app.route('/optimize', methods=['POST'])
def optimize():
    """
    Optimise une campagne en fonction des insights fournis
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Si les insights sont fournis directement
    if "artist_name" in data:
        insights = data
    else:
        # Sinon, récupérer les insights depuis l'API centrale
        try:
            response = requests.get(f"{API_SERVER_URL}/retrieve/campaign_insights")
            if response.status_code == 200:
                response_data = response.json()
                if "data" in response_data:
                    insights = response_data["data"]
                else:
                    return jsonify({"error": "No insights found in API server"}), 404
            else:
                return jsonify({"error": f"Failed to retrieve insights: {response.status_code}"}), 500
        except Exception as e:
            return jsonify({"error": f"Error retrieving insights: {str(e)}"}), 500
    
    # Optimiser la campagne
    optimized_campaign = optimize_campaign(insights)
    
    # Stocker la campagne optimisée dans l'API centrale
    try:
        requests.post(
            f"{API_SERVER_URL}/store/optimized_campaign",
            json=optimized_campaign
        )
    except Exception as e:
        print(f"Erreur lors du stockage de la campagne optimisée: {e}")
    
    return jsonify({"status": "success", "data": optimized_campaign}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
