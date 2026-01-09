#!/bin/bash
# Script de démarrage pour Railway
PORT=${PORT:-8000}
uvicorn app.main:app --host 0.0.0.0 --port $PORT
