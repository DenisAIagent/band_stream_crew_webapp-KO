import os
import json
import requests
import re
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API centrale
API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://api_server:5000')

app = Flask(__name__)

# Mots-clés interdits pour les annonces Google Ads
FORBIDDEN_KEYWORDS = [
    "gratuit", "téléchargement", "streaming illégal", "offert", 
    "free", "download", "illegal streaming", "offered"
]

# Expressions FOMO (Fear Of Missing Out)
FOMO_EXPRESSIONS = [
    "Ne manquez pas", "Offre limitée", "Événement unique", 
    "Dernière chance", "Exclusivité", "Places limitées",
    "Seulement aujourd'hui", "Bientôt épuisé", "Réservez maintenant"
]

def validate_ad_text(text):
    """
    Vérifie si le texte de l'annonce respecte les règles Google Ads
    """
    # Vérifier les mots-clés interdits
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword.lower() in text.lower():
            return False, f"Contient le mot-clé interdit: {keyword}"
    
    # Vérifier les caractères spéciaux (emojis, symboles comme %, $)
    if re.search(r'[^\w\s.,!?\'"-]', text):
        return False, "Contient des caractères spéciaux interdits"
    
    return True, "Texte valide"

def contains_fomo(text):
    """
    Vérifie si le texte contient une expression FOMO
    """
    for expression in FOMO_EXPRESSIONS:
        if expression.lower() in text.lower():
            return True
    return False

def truncate_text(text, max_length):
    """
    Tronque le texte à la longueur maximale spécifiée
    """
    if len(text) <= max_length:
        return text
    
    # Tronquer au dernier espace avant la limite pour éviter de couper un mot
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        return truncated[:last_space]
    
    return truncated

def generate_ad_drafts(artist_name, music_style, lyrics, bio, lookalike_artists):
    """
    Génère des drafts d'annonces respectant les règles Google Ads et FOMO
    """
    ad_drafts = []
    
    # Préparer les noms des artistes Lookalike pour les annonces
    lookalike_names = [artist.get("name", "") for artist in lookalike_artists if artist.get("name")]
    lookalike_string = ", ".join(lookalike_names[:3])  # Limiter à 3 artistes pour la longueur
    
    # Générer différents types d'annonces
    
    # Type 1: Annonce standard avec FOMO
    title = f"Ne manquez pas {artist_name}"
    title = truncate_text(title, 30)
    
    long_title = f"Fans de {lookalike_string} Ne manquez pas {artist_name}"
    long_title = truncate_text(long_title, 90)
    
    description = f"Evenement unique Decouvrez {artist_name} en concert 2025"
    description = truncate_text(description, 90)
    
    valid_title, title_message = validate_ad_text(title)
    valid_long_title, long_title_message = validate_ad_text(long_title)
    valid_description, description_message = validate_ad_text(description)
    
    if valid_title and valid_long_title and valid_description and contains_fomo(title + long_title + description):
        ad_drafts.append({
            "type": "standard_fomo",
            "title": title,
            "long_title": long_title,
            "description": description,
            "character_counts": {
                "title": len(title),
                "long_title": len(long_title),
                "description": len(description)
            }
        })
    
    # Type 2: Annonce basée sur le style musical avec FOMO
    title = f"{music_style} Offre limitée"
    title = truncate_text(title, 30)
    
    long_title = f"{artist_name} {music_style} Dernière chance"
    long_title = truncate_text(long_title, 90)
    
    description = f"Rejoignez les fans de {lookalike_string} et découvrez {artist_name}"
    description = truncate_text(description, 90)
    
    valid_title, title_message = validate_ad_text(title)
    valid_long_title, long_title_message = validate_ad_text(long_title)
    valid_description, description_message = validate_ad_text(description)
    
    if valid_title and valid_long_title and valid_description and contains_fomo(title + long_title + description):
        ad_drafts.append({
            "type": "music_style_fomo",
            "title": title,
            "long_title": long_title,
            "description": description,
            "character_counts": {
                "title": len(title),
                "long_title": len(long_title),
                "description": len(description)
            }
        })
    
    # Type 3: Annonce basée sur les artistes Lookalike avec FOMO
    title = f"Fans de {lookalike_names[0] if lookalike_names else music_style}"
    title = truncate_text(title, 30)
    
    long_title = f"Vous aimez {lookalike_string} Découvrez {artist_name} maintenant"
    long_title = truncate_text(long_title, 90)
    
    description = f"Événement unique {artist_name} le nouveau phénomène {music_style}"
    description = truncate_text(description, 90)
    
    valid_title, title_message = validate_ad_text(title)
    valid_long_title, long_title_message = validate_ad_text(long_title)
    valid_description, description_message = validate_ad_text(description)
    
    if valid_title and valid_long_title and valid_description and contains_fomo(title + long_title + description):
        ad_drafts.append({
            "type": "lookalike_fomo",
            "title": title,
            "long_title": long_title,
            "description": description,
            "character_counts": {
                "title": len(title),
                "long_title": len(long_title),
                "description": len(description)
            }
        })
    
    # Type 4: Annonce basée sur les paroles avec FOMO
    # Extraire quelques mots des paroles (si disponibles)
    lyrics_excerpt = ""
    if lyrics:
        words = lyrics.split()
        if words:
            lyrics_excerpt = " ".join(words[:3])  # Prendre les 3 premiers mots
    
    title = f"Places limitées {artist_name}"
    title = truncate_text(title, 30)
    
    long_title = f"{lyrics_excerpt} - {artist_name} Réservez maintenant"
    long_title = truncate_text(long_title, 90)
    
    description = f"Comme {lookalike_string} {artist_name} va vous surprendre"
    description = truncate_text(description, 90)
    
    valid_title, title_message = validate_ad_text(title)
    valid_long_title, long_title_message = validate_ad_text(long_title)
    valid_description, description_message = validate_ad_text(description)
    
    if valid_title and valid_long_title and valid_description and contains_fomo(title + long_title + description):
        ad_drafts.append({
            "type": "lyrics_fomo",
            "title": title,
            "long_title": long_title,
            "description": description,
            "character_counts": {
                "title": len(title),
                "long_title": len(long_title),
                "description": len(description)
            }
        })
    
    return ad_drafts

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé"""
    return jsonify({"status": "ok", "message": "Marketing Agents service is running"}), 200

@app.route('/generate_ads', methods=['POST'])
def generate_ads():
    """
    Génère des drafts d'annonces en fonction des informations fournies
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    artist_name = data.get("artist_name", "")
    music_style = data.get("music_style", "")
    lyrics = data.get("lyrics", "")
    bio = data.get("bio", "")
    
    if not artist_name:
        return jsonify({"error": "Artist name is required"}), 400
    
    # Récupérer les artistes Lookalike depuis l'API centrale
    lookalike_artists = []
    try:
        response = requests.get(f"{API_SERVER_URL}/retrieve/lookalike_artists")
        if response.status_code == 200:
            response_data = response.json()
            if "data" in response_data:
                lookalike_artists = response_data["data"]
    except Exception as e:
        print(f"Erreur lors de la récupération des artistes Lookalike: {e}")
    
    # Générer les drafts d'annonces
    ad_drafts = generate_ad_drafts(artist_name, music_style, lyrics, bio, lookalike_artists)
    
    # Stocker les drafts d'annonces dans l'API centrale
    try:
        requests.post(
            f"{API_SERVER_URL}/store/ad_drafts",
            json=ad_drafts
        )
    except Exception as e:
        print(f"Erreur lors du stockage des drafts d'annonces: {e}")
    
    return jsonify({"status": "success", "data": ad_drafts}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
