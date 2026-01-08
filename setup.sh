#!/bin/bash

# Script pour créer tous les fichiers __init__.py
echo "Création des fichiers __init__.py..."

touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/endpoints/__init__.py
touch backend/app/schemas/__init__.py

echo "✅ Tous les fichiers __init__.py sont créés!"
echo ""
echo "📝 Maintenant, copie les fichiers depuis le Google Doc:"
echo ""
echo "Liste des fichiers à créer:"
echo "2. backend/app/core/config.py"
echo "3. backend/app/core/database.py"
echo "4. backend/app/models/company.py"
echo "5. backend/app/models/qbo_account.py"
echo "6. backend/app/models/qbo_transaction.py"
echo "7. backend/app/models/scenario.py"
echo "8. backend/app/models/projection.py"
echo "9. backend/app/services/qbo_service.py"
echo "10. backend/app/services/projection_engine.py"
echo "11. backend/app/api/endpoints/scenarios.py"
echo "12. backend/app/api/endpoints/qbo.py"
echo "13. backend/alembic.ini"
echo "14. backend/alembic/env.py"
echo "15. backend/Dockerfile"
echo "16. docker-compose.yml (à la racine)"
echo "17. frontend/package.json"

