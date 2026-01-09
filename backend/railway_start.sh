#!/bin/bash
# Script de démarrage pour Railway (fallback si nécessaire)
PORT=${PORT:-8000}
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
