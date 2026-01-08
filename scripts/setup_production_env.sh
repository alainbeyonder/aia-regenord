#!/bin/bash

# Script de configuration pour la production
# Ce script aide à configurer le fichier backend/.env pour la production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_ENV="$PROJECT_ROOT/backend/.env"
TEMPLATE="$PROJECT_ROOT/BACKEND_ENV_TEMPLATE.txt"

echo "=========================================="
echo "🚀 Configuration Production - QuickBooks"
echo "=========================================="
echo ""

# Vérifier si .env existe déjà
if [ -f "$BACKEND_ENV" ]; then
    echo "⚠️  Le fichier backend/.env existe déjà."
    read -p "Voulez-vous le sauvegarder en backup? (o/n): " backup_choice
    if [[ "$backup_choice" == "o" || "$backup_choice" == "O" ]]; then
        BACKUP_FILE="${BACKEND_ENV}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$BACKEND_ENV" "$BACKUP_FILE"
        echo "✅ Backup créé: $BACKUP_FILE"
    fi
fi

# Générer les clés de sécurité
echo ""
echo "🔑 Génération des clés de sécurité..."
python3 "$SCRIPT_DIR/generate_security_keys.py" > /tmp/keys_output.txt 2>&1

FERNET_KEY=$(grep -A 1 "Clé Fernet" /tmp/keys_output.txt | tail -1 | sed 's/^[[:space:]]*//' || echo "")
SECRET_KEY=$(grep -A 1 "Clé Secrète" /tmp/keys_output.txt | tail -1 | sed 's/^[[:space:]]*//' || echo "")

if [ -z "$FERNET_KEY" ]; then
    echo "⚠️  Impossible de générer la clé Fernet automatiquement."
    echo "   Assurez-vous que 'cryptography' est installé: pip install cryptography"
    read -p "   Entrez manuellement la clé Fernet (ou appuyez sur Entrée pour laisser vide): " FERNET_KEY
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  Impossible de générer la clé secrète."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "")
    if [ -z "$SECRET_KEY" ]; then
        read -p "   Entrez manuellement la clé secrète: " SECRET_KEY
    fi
fi

# Demander l'URL du backend
echo ""
read -p "🔗 Entrez l'URL de votre backend en production (ex: https://api.regenord.com): " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo "❌ L'URL du backend est requise!"
    exit 1
fi

# Créer le fichier .env
echo ""
echo "📝 Création du fichier backend/.env..."

cat > "$BACKEND_ENV" << EOF
# ============================================
# Configuration Backend - PRODUCTION
# Généré le: $(date)
# ============================================

# QuickBooks Online - PRODUCTION
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Application
APP_NAME=AIA Regenord
APP_ENV=production
DEBUG=False
APP_BASE_URL=${BACKEND_URL}
FRONTEND_URL=https://www.regenord.com

# Sécurité
AIA_TOKEN_ENCRYPTION_KEY=${FERNET_KEY:-YOUR_FERNET_KEY_HERE}
SECRET_KEY=${SECRET_KEY}

# Base de données
DATABASE_URL=postgresql://user:password@host:5432/aia_regenord

# CORS
CORS_ORIGINS=["https://www.regenord.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/aia-regenord.log
EOF

echo "✅ Fichier backend/.env créé avec succès!"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Vérifiez et modifiez DATABASE_URL si nécessaire"
echo "   2. Vérifiez que les clés de sécurité sont correctes"
echo "   3. Ne committez JAMAIS le fichier .env dans Git!"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Vérifier backend/.env"
echo "   2. Mettre à jour SQUARESPACE_CODE_INJECTION_FINAL.html avec BACKEND_URL=${BACKEND_URL}"
echo "   3. Configurer Intuit Developer (Redirect URI)"
echo "   4. Injecter le code dans Squarespace"
echo "   5. Tester la connexion"
