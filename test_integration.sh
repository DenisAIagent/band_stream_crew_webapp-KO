#!/bin/bash

# Script de test pour vérifier l'intégration et la fonctionnalité de Band Stream Crew IA Agent

echo "=== Test d'intégration de Band Stream Crew IA Agent ==="
echo ""

# Vérifier que tous les fichiers nécessaires existent
echo "Vérification des fichiers..."

FILES=(
    "api_server/api_server.py"
    "api_server/Dockerfile"
    "api_server/requirements.txt"
    "campaign_analyst/campaign_analyst.py"
    "campaign_analyst/Dockerfile"
    "campaign_analyst/requirements.txt"
    "campaign_optimizer/campaign_optimizer.py"
    "campaign_optimizer/Dockerfile"
    "campaign_optimizer/requirements.txt"
    "marketing_agents/marketing_agents.py"
    "marketing_agents/Dockerfile"
    "marketing_agents/requirements.txt"
    "campaign_supervisor/campaign_supervisor.py"
    "campaign_supervisor/Dockerfile"
    "campaign_supervisor/requirements.txt"
    "campaign_supervisor/templates/index.html"
    "campaign_supervisor/templates/results.html"
    "docker-compose.yml"
)

all_files_exist=true
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier manquant: $file"
        all_files_exist=false
    else
        echo "✅ Fichier trouvé: $file"
    fi
done

echo ""
if [ "$all_files_exist" = false ]; then
    echo "❌ Certains fichiers sont manquants. Veuillez vérifier la structure du projet."
    exit 1
else
    echo "✅ Tous les fichiers nécessaires sont présents."
fi

echo ""
echo "=== Test des endpoints de santé ==="
echo ""
echo "Note: Ce test suppose que les services sont déjà en cours d'exécution."
echo "Si ce n'est pas le cas, veuillez exécuter 'docker-compose up -d' avant de lancer ce test."
echo ""

# Tester les endpoints de santé de chaque service
ENDPOINTS=(
    "http://localhost:5000/health"
    "http://localhost:5001/health"
    "http://localhost:5002/health"
    "http://localhost:5003/health"
    "http://localhost:5004/health"
)

SERVICES=(
    "API Server"
    "Campaign Analyst"
    "Campaign Optimizer"
    "Marketing Agents"
    "Campaign Supervisor"
)

echo "Pour tester manuellement les endpoints de santé, exécutez les commandes suivantes :"
echo ""

for i in "${!ENDPOINTS[@]}"; do
    echo "curl ${ENDPOINTS[$i]} # Test de ${SERVICES[$i]}"
done

echo ""
echo "=== Test de l'interface utilisateur ==="
echo ""
echo "Pour tester l'interface utilisateur, ouvrez votre navigateur et accédez à :"
echo "http://localhost:5004"
echo ""
echo "Remplissez le formulaire avec les informations suivantes :"
echo "- Nom de l'artiste: Gojira"
echo "- Style musical: metal progressif"
echo "- Chanson: L'Enfant Sauvage"
echo "- Paroles: (ajoutez quelques paroles)"
echo "- Biographie: (ajoutez une courte biographie)"
echo ""
echo "Cliquez sur 'Générer la campagne' et vérifiez que les résultats s'affichent correctement."
echo ""

echo "=== Fin des tests ==="
