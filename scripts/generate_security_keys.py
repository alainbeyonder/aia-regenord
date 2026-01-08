#!/usr/bin/env python3
"""
Script pour générer les clés de sécurité nécessaires pour la production.
"""
import secrets
import sys

try:
    from cryptography.fernet import Fernet
    FERNET_AVAILABLE = True
except ImportError:
    FERNET_AVAILABLE = False
    print("⚠️  Module 'cryptography' non installé. Installer avec: pip install cryptography")

def generate_fernet_key():
    """Génère une clé Fernet pour l'encryption des tokens QBO."""
    if not FERNET_AVAILABLE:
        return None
    return Fernet.generate_key().decode()

def generate_secret_key():
    """Génère une clé secrète pour l'application."""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 Génération des Clés de Sécurité - Production")
    print("=" * 60)
    print()
    
    # Clé Fernet
    if FERNET_AVAILABLE:
        fernet_key = generate_fernet_key()
        print("✅ Clé Fernet (pour AIA_TOKEN_ENCRYPTION_KEY):")
        print(f"   {fernet_key}")
        print()
    else:
        print("❌ Impossible de générer la clé Fernet (module manquant)")
        print()
    
    # Clé secrète
    secret_key = generate_secret_key()
    print("✅ Clé Secrète (pour SECRET_KEY):")
    print(f"   {secret_key}")
    print()
    
    print("=" * 60)
    print("📝 Instructions:")
    print("   1. Copier ces clés dans votre fichier backend/.env")
    print("   2. NE JAMAIS committer le fichier .env dans Git!")
    print("   3. Garder ces clés en sécurité")
    print("=" * 60)
