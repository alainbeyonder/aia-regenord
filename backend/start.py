#!/usr/bin/env python3
"""Script de démarrage pour Railway."""
import os
import subprocess
import sys

# Obtenir le port depuis les variables d'environnement
port = os.environ.get('PORT', '8000')

try:
    port_int = int(port)
except ValueError:
    print(f"Erreur: PORT doit être un entier, reçu: {port}", file=sys.stderr)
    sys.exit(1)

print(f"Démarrage du service sur le port {port_int}...")

# Démarrer uvicorn
cmd = [
    'uvicorn',
    'app.main:app',
    '--host', '0.0.0.0',
    '--port', str(port_int)
]

try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    print("\nArrêt du service...")
except Exception as e:
    print(f"Erreur lors du démarrage: {e}", file=sys.stderr)
    sys.exit(1)
