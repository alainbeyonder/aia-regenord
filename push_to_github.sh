#!/bin/bash

# Script pour pousser le code sur GitHub
# Usage: ./push_to_github.sh

echo "============================================"
echo "🚀 Push vers GitHub"
echo "============================================"
echo ""

cd /Users/alain/Documents/aia-regenord

echo "📋 Vérification du statut Git..."
git status --short | head -10
echo ""

echo "🔍 Dernier commit:"
git log --oneline -1
echo ""

echo "🚀 Poussée vers GitHub..."
echo ""
echo "⚠️  Si une authentification est requise:"
echo "   1. GitHub peut demander votre nom d'utilisateur"
echo "   2. Pour le mot de passe, utilisez un Personal Access Token"
echo "   3. Créer un token: https://github.com/settings/tokens"
echo "   4. Sélectionner la permission: repo"
echo ""

git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Code poussé avec succès sur GitHub!"
    echo ""
    echo "📋 Prochaines étapes:"
    echo "   1. Aller sur: https://railway.app"
    echo "   2. Suivre: FINALISER_RAILWAY.md"
else
    echo ""
    echo "⚠️  Push nécessite authentification interactive"
    echo ""
    echo "💡 Alternatives:"
    echo "   1. Utiliser GitHub Desktop (interface graphique)"
    echo "   2. Configurer SSH key pour GitHub"
    echo "   3. Utiliser GitHub CLI: gh auth login"
    echo ""
    echo "📖 Ou suivre: COMMANDES_FINALES_RAILWAY.md"
fi
