import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# Charger les variables d'environnement
load_dotenv()

# Configuration des API keys
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '3655e03f594b0635fc8f5faa24802d2f222cec5f78d70975478fb56aca8d138c')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '4d8f8b29c4c645be84bfa5714bcc3af2')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'd6da44bc84d6493494673b5a82a45e95')
DEEZER_ACCESS_TOKEN = os.getenv('DEEZER_ACCESS_TOKEN', '')

# Configuration de l'API centrale
API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://api_server:5000')

app = Flask(__name__)

# Configuration de Spotify
spotify = None
try:
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
except Exception as e:
    print(f"Erreur lors de l'initialisation de Spotify: {e}")

def get_youtube_trends(artist_name, music_style):
    """
    Récupère les tendances YouTube via SerpApi
    """
    try:
        search_query = f"{artist_name} {music_style} music"
        params = {
            "engine": "youtube",
            "search_query": search_query,
            "api_key": SERPAPI_KEY
        }
        response = requests.get("https://serpapi.com/search", params=params)
        
        if response.status_code == 200:
            data = response.json()
            videos = []
            
            if "video_results" in data:
                for video in data["video_results"][:5]:  # Limiter à 5 vidéos
                    videos.append({
                        "title": video.get("title", ""),
                        "link": video.get("link", ""),
                        "thumbnail": video.get("thumbnail", {}).get("static", ""),
                        "views": video.get("views", ""),
                        "published_date": video.get("published_date", "")
                    })
            
            return videos
        else:
            print(f"Erreur SerpApi YouTube: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erreur lors de la récupération des tendances YouTube: {e}")
        return []

def get_google_trends(artist_name, music_style):
    """
    Récupère les tendances Google via SerpApi
    """
    try:
        search_query = f"{artist_name} {music_style}"
        params = {
            "engine": "google_trends",
            "q": search_query,
            "api_key": SERPAPI_KEY
        }
        response = requests.get("https://serpapi.com/search", params=params)
        
        if response.status_code == 200:
            data = response.json()
            trends = []
            
            if "interest_over_time" in data:
                trends = data["interest_over_time"]
            
            return trends
        else:
            print(f"Erreur SerpApi Google Trends: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erreur lors de la récupération des tendances Google: {e}")
        return []

def get_deezer_similar_artists(artist_name):
    """
    Récupère des artistes similaires via l'API Deezer
    """
    try:
        # Recherche de l'artiste
        search_url = f"https://api.deezer.com/search/artist?q={artist_name}"
        headers = {}
        
        # Ajouter le token d'accès si disponible
        if DEEZER_ACCESS_TOKEN:
            headers["Authorization"] = f"Bearer {DEEZER_ACCESS_TOKEN}"
        
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                artist_id = data["data"][0]["id"]
                
                # Récupération des artistes similaires
                similar_url = f"https://api.deezer.com/artist/{artist_id}/related"
                similar_response = requests.get(similar_url, headers=headers)
                
                if similar_response.status_code == 200:
                    similar_data = similar_response.json()
                    
                    similar_artists = []
                    if "data" in similar_data:
                        for artist in similar_data["data"][:10]:  # Limiter à 10 artistes
                            similar_artists.append({
                                "id": artist.get("id", ""),
                                "name": artist.get("name", ""),
                                "picture": artist.get("picture_medium", ""),
                                "nb_fans": artist.get("nb_fans", 0)
                            })
                    
                    return similar_artists
        
        print(f"Erreur Deezer: {response.status_code}")
        return []
    except Exception as e:
        print(f"Erreur lors de la récupération des artistes similaires Deezer: {e}")
        return []
    
    # Respecter la limite de 50 requêtes par 5 secondes
    time.sleep(0.1)
    return []

def get_spotify_similar_artists(artist_name):
    """
    Récupère des artistes similaires via l'API Spotify
    """
    if not spotify:
        return []
    
    try:
        # Recherche de l'artiste
        results = spotify.search(q=f"artist:{artist_name}", type="artist", limit=1)
        
        if results and "artists" in results and "items" in results["artists"] and len(results["artists"]["items"]) > 0:
            artist_id = results["artists"]["items"][0]["id"]
            
            # Récupération des artistes similaires
            similar_artists_data = spotify.artist_related_artists(artist_id)
            
            similar_artists = []
            if "artists" in similar_artists_data:
                for artist in similar_artists_data["artists"][:10]:  # Limiter à 10 artistes
                    similar_artists.append({
                        "id": artist.get("id", ""),
                        "name": artist.get("name", ""),
                        "popularity": artist.get("popularity", 0),
                        "genres": artist.get("genres", []),
                        "image": artist["images"][0]["url"] if artist.get("images") and len(artist["images"]) > 0 else ""
                    })
            
            return similar_artists
        
        return []
    except Exception as e:
        print(f"Erreur lors de la récupération des artistes similaires Spotify: {e}")
        return []

def get_lookalike_artists(artist_name, music_style):
    """
    Identifie les artistes Lookalike (artistes similaires en tendance)
    """
    # Récupérer les artistes similaires de différentes sources
    deezer_artists = get_deezer_similar_artists(artist_name)
    spotify_artists = get_spotify_similar_artists(artist_name)
    
    # Combiner les résultats
    all_artists = {}
    
    # Ajouter les artistes Deezer
    for artist in deezer_artists:
        name = artist.get("name", "").lower()
        if name and name != artist_name.lower():
            if name not in all_artists:
                all_artists[name] = {
                    "name": artist.get("name", ""),
                    "sources": ["deezer"],
                    "deezer_fans": artist.get("nb_fans", 0),
                    "spotify_popularity": 0,
                    "score": artist.get("nb_fans", 0)
                }
            else:
                all_artists[name]["sources"].append("deezer")
                all_artists[name]["deezer_fans"] = artist.get("nb_fans", 0)
                all_artists[name]["score"] += artist.get("nb_fans", 0)
    
    # Ajouter les artistes Spotify
    for artist in spotify_artists:
        name = artist.get("name", "").lower()
        if name and name != artist_name.lower():
            if name not in all_artists:
                all_artists[name] = {
                    "name": artist.get("name", ""),
                    "sources": ["spotify"],
                    "deezer_fans": 0,
                    "spotify_popularity": artist.get("popularity", 0),
                    "score": artist.get("popularity", 0) * 1000  # Pondération pour équilibrer avec les fans Deezer
                }
            else:
                all_artists[name]["sources"].append("spotify")
                all_artists[name]["spotify_popularity"] = artist.get("popularity", 0)
                all_artists[name]["score"] += artist.get("popularity", 0) * 1000
    
    # Trier par score et prendre les 5 meilleurs
    lookalike_artists = sorted(all_artists.values(), key=lambda x: x["score"], reverse=True)[:5]
    
    return lookalike_artists

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé"""
    return jsonify({"status": "ok", "message": "Campaign Analyst service is running"}), 200

@app.route('/analyze', methods=['POST'])
def analyze_campaign():
    """
    Analyse une campagne en fonction du nom de l'artiste et du style musical
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    artist_name = data.get("artist_name", "")
    music_style = data.get("music_style", "")
    
    if not artist_name:
        return jsonify({"error": "Artist name is required"}), 400
    
    # Récupérer les tendances YouTube
    youtube_trends = get_youtube_trends(artist_name, music_style)
    
    # Récupérer les tendances Google
    google_trends = get_google_trends(artist_name, music_style)
    
    # Récupérer les artistes similaires Deezer
    deezer_similar = get_deezer_similar_artists(artist_name)
    
    # Récupérer les artistes similaires Spotify
    spotify_similar = get_spotify_similar_artists(artist_name)
    
    # Identifier les artistes Lookalike
    lookalike_artists = get_lookalike_artists(artist_name, music_style)
    
    # Préparer les résultats
    results = {
        "artist_name": artist_name,
        "music_style": music_style,
        "youtube_trends": youtube_trends,
        "google_trends": google_trends,
        "deezer_similar": deezer_similar,
        "spotify_similar": spotify_similar,
        "lookalike_artists": lookalike_artists
    }
    
    # Stocker les résultats dans l'API centrale
    try:
        # Stocker les insights
        requests.post(
            f"{API_SERVER_URL}/store/campaign_insights",
            json=results
        )
        
        # Stocker les artistes Lookalike séparément
        requests.post(
            f"{API_SERVER_URL}/store/lookalike_artists",
            json=lookalike_artists
        )
    except Exception as e:
        print(f"Erreur lors du stockage des résultats dans l'API centrale: {e}")
    
    return jsonify({"status": "success", "data": results}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
