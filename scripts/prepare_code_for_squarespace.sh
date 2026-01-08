#!/bin/bash

# Script pour préparer le code à injecter dans Squarespace
# Affiche le code et donne des instructions pour la copie

echo "============================================"
echo "📋 Préparation Code Squarespace"
echo "============================================"
echo ""

CODE_FILE="SQUARESPACE_CODE_INJECTION_READY.html"

if [ ! -f "$CODE_FILE" ]; then
    echo "❌ Fichier $CODE_FILE non trouvé"
    exit 1
fi

echo "✅ Fichier trouvé: $CODE_FILE"
echo ""
echo "📄 Contenu du fichier (${#CODE_FILE} lignes):"
echo ""

# Vérifier si on peut utiliser pbcopy (macOS) ou xclip (Linux)
if command -v pbcopy &> /dev/null; then
    echo "💡 Détecté: macOS - Option de copie automatique disponible"
    echo ""
    read -p "Voulez-vous copier le code dans le presse-papier? (o/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        cat "$CODE_FILE" | pbcopy
        echo "✅ Code copié dans le presse-papier!"
        echo ""
        echo "🚀 Prochaines étapes:"
        echo "   1. Aller dans Squarespace: Settings > Advanced > Code Injection"
        echo "   2. Dans la section Footer, coller le code (Cmd+V)"
        echo "   3. Cliquer sur Save"
        exit 0
    fi
elif command -v xclip &> /dev/null; then
    echo "💡 Détecté: Linux - Option de copie automatique disponible"
    echo ""
    read -p "Voulez-vous copier le code dans le presse-papier? (o/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        cat "$CODE_FILE" | xclip -selection clipboard
        echo "✅ Code copié dans le presse-papier!"
        echo ""
        echo "🚀 Prochaines étapes:"
        echo "   1. Aller dans Squarespace: Settings > Advanced > Code Injection"
        echo "   2. Dans la section Footer, coller le code (Ctrl+V)"
        echo "   3. Cliquer sur Save"
        exit 0
    fi
fi

echo "📋 Instructions pour copier manuellement:"
echo ""
echo "1. Ouvrir le fichier: $CODE_FILE"
echo "2. Sélectionner tout le contenu:"
echo "   - Mac: Cmd + A"
echo "   - Windows/Linux: Ctrl + A"
echo "3. Copier:"
echo "   - Mac: Cmd + C"
echo "   - Windows/Linux: Ctrl + C"
echo "4. Dans Squarespace:"
echo "   - Settings > Advanced > Code Injection"
echo "   - Section Footer"
echo "   - Coller (Cmd+V / Ctrl+V)"
echo "   - Save"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Afficher les premières et dernières lignes pour vérification
echo "📄 Aperçu du code (premières lignes):"
head -n 15 "$CODE_FILE"
echo ""
echo "... (${#CODE_FILE} lignes au total) ..."
echo ""
echo "📄 Dernières lignes:"
tail -n 5 "$CODE_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Configuration détectée:"
grep -E "BACKEND_URL|COMPANY_ID" "$CODE_FILE" | head -2 | sed 's/^/   /'
