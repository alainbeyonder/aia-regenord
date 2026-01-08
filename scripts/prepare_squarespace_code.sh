#!/bin/bash

# Script pour préparer le code Squarespace avec l'URL du backend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SQUARESPACE_CODE="$PROJECT_ROOT/SQUARESPACE_CODE_INJECTION_FINAL.html"
OUTPUT_CODE="$PROJECT_ROOT/SQUARESPACE_CODE_INJECTION_READY.html"

echo "=========================================="
echo "📝 Préparation Code Squarespace"
echo "=========================================="
echo ""

# Vérifier si backend/.env existe pour extraire APP_BASE_URL
BACKEND_ENV="$PROJECT_ROOT/backend/.env"
BACKEND_URL=""

if [ -f "$BACKEND_ENV" ]; then
    BACKEND_URL=$(grep "^APP_BASE_URL=" "$BACKEND_ENV" | cut -d'=' -f2 | sed 's/^"//;s/"$//' || echo "")
fi

# Demander l'URL du backend si non trouvée
if [ -z "$BACKEND_URL" ]; then
    read -p "🔗 Entrez l'URL de votre backend en production (ex: https://api.regenord.com): " BACKEND_URL
fi

if [ -z "$BACKEND_URL" ]; then
    echo "❌ L'URL du backend est requise!"
    exit 1
fi

# Créer la version prête du code
echo "📝 Création de SQUARESPACE_CODE_INJECTION_READY.html avec BACKEND_URL=${BACKEND_URL}..."
sed "s|YOUR_BACKEND_URL|${BACKEND_URL}|g" "$SQUARESPACE_CODE" > "$OUTPUT_CODE"

echo "✅ Code prêt créé: $OUTPUT_CODE"
echo ""
echo "📋 Instructions:"
echo "   1. Ouvrir le fichier: $OUTPUT_CODE"
echo "   2. Copier TOUT le contenu (Cmd+A, Cmd+C)"
echo "   3. Dans Squarespace: Settings > Advanced > Code Injection > Footer"
echo "   4. Coller le code (Cmd+V)"
echo "   5. Sauvegarder"
echo ""
echo "🔗 URL du backend configurée: ${BACKEND_URL}"
