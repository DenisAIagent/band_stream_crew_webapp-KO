# Analyse des exigences du projet "Band Stream Crew IA Agent"

## Architecture globale
- 5 agents autonomes dans des conteneurs Docker séparés
- Communication via API Flask centrale (api_server.py sur port 5000)
- Transformation de l'interface CLI en webapp Flask

## Agents et leurs rôles
1. **Agent MAIN (Interface Utilisateur)**
   - Actuellement: Script CLI (campaign_supervisor.py)
   - À transformer en: Webapp Flask avec formulaire HTML
   - Port: 5004
   - Fonctionnalités:
     - Collecter les informations utilisateur (artiste, style musical, chanson, paroles, bio)
     - Transmettre aux autres agents via l'API centrale
     - Afficher les résultats finaux

2. **Agent SUPERVISOR (Chef de Projet)**
   - Actuellement: Intégré dans campaign_supervisor.py
   - Rôle:
     - Orchestrer les autres agents
     - Transmettre "Nom & Style Musical" à Agent ANALYST
     - Transmettre "Paroles & Bio" à Agent MARKETING
     - Coordonner les résultats via Agent OPTIMIZER
     - Retourner la campagne finale à Agent MAIN

3. **Agent ANALYST (Recherche d'Insights)**
   - Fichier: campaign_analyst.py
   - Port: 5001
   - Rôle:
     - Rechercher des insights via APIs (YouTube/SerpApi, Deezer, Spotify, Google Trends)
     - Identifier les artistes similaires et tendances
     - Retourner des "Insights Tendances"
   - Fonctionnalité à ajouter:
     - Fonction get_lookalike_artists pour identifier artistes similaires en tendance

4. **Agent MARKETING (Rédaction d'Annonces)**
   - Fichier: marketing_agents.py
   - Port: 5003
   - Rôle:
     - Rédiger des annonces respectant les règles Google Ads et FOMO
     - Intégrer les artistes Lookalike dans les annonces
   - Contraintes pour les annonces:
     - Titres: 30 caractères maximum
     - Titres longs: 90 caractères maximum
     - Description: 90 caractères maximum
     - Type FOMO obligatoire
     - Pas de mots-clés interdits
     - Pas de caractères spéciaux

5. **Agent OPTIMIZER (Optimisation)**
   - Fichier: campaign_optimizer.py
   - Port: 5002
   - Rôle:
     - Optimiser les insights pour suggérer des stratégies
     - Retourner une "Campagne Optimisée" au SUPERVISOR

## APIs et clés
1. **SerpApi** (YouTube et Google Trends)
   - Clé: SERPAPI_KEY=3655e03f594b0635fc8f5faa24802d2f222cec5f78d70975478fb56aca8d138c
   - Endpoint Google Trends: https://serpapi.com/search?engine=google_trends

2. **Deezer**
   - Documentation: https://api.deezer.com
   - Limite: 50 requêtes par 5 secondes
   - Format: JSON/XML, codage UTF-8
   - Exemples: 
     - https://api.deezer.com/search/artist?q=eminem
     - https://api.deezer.com/user/2529/playlists
   - Clé: DEEZER_ACCESS_TOKEN=ton_token_deezer (utiliser API publique si pas de clé réelle)

3. **Spotify**
   - SPOTIFY_CLIENT_ID=4d8f8b29c4c645be84bfa5714bcc3af2
   - SPOTIFY_CLIENT_SECRET=d6da44bc84d6493494673b5a82a45e95

4. **AnythingLLM** (optionnel)
   - ANYTHINGLLM_API_KEY=98QAQ7R-WNY4016-JSEM27X-QF5H9JQ
   - Endpoint: http://127.0.0.1:3001/api/v1/openai/chat/completions

5. **Google Auth Platform** (OAuth 2.0, optionnel)
   - Application Google Ads:
     - import os

google_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
     - URI de redirection: https://oauth.n8n.cloud/oauth2/callback
   - Application YouTube API:
     - import os

google_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
     - URI de redirection: http://localhost:3000/oauth2callback, http://127.0.0.1:3000/oauth2callback

## Exigences pour la webapp
1. **Interface utilisateur**
   - Page d'accueil avec formulaire HTML simple
   - Champs: artiste, style musical, chanson, paroles, bio
   - Page de résultats avec la campagne finale
   - Design simple (HTML et Flask, pas de JavaScript complexe)

2. **Docker**
   - Chaque agent dans un conteneur Docker séparé
   - Orchestration via docker-compose.yml
   - Ports: 5000, 5001, 5002, 5003, 5004
   - Communication inter-conteneurs via l'API Flask centrale

3. **Gestion des erreurs**
   - Retours par défaut pour les erreurs API
   - Messages d'erreur clairs
   - Éviter les crashs

## Livrables attendus
1. Scripts Python pour chaque agent
2. Templates HTML pour la webapp
3. Dockerfile pour chaque agent
4. docker-compose.yml pour orchestrer les conteneurs
5. requirements.txt pour chaque agent
6. notes.txt avec instructions de déploiement

## Flux de travail typique
1. Utilisateur accède à http://127.0.0.1:5004
2. Remplit le formulaire avec informations sur l'artiste
3. Après soumission, voit une page avec:
   - Insights (artistes similaires, Lookalikes, vidéos)
   - Campagne optimisée (suggestions)
   - Drafts d'annonces respectant les règles Google Ads et FOMO
