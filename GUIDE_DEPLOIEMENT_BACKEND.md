# 🚀 Guide de Déploiement Backend - Production

Guide pratique pour déployer le backend sur `https://api.regenord.com`.

---

## 📋 Prérequis

### Infrastructure Nécessaire

- **Serveur:** VPS, Cloud Server (AWS, Google Cloud, DigitalOcean, etc.)
- **Base de données:** PostgreSQL (sur le serveur ou service géré)
- **Domaine:** `api.regenord.com` (sous-domaine configuré)
- **SSL/HTTPS:** Certificat SSL pour HTTPS

### Variables d'Environnement

Le fichier `backend/.env` doit être configuré avec:
- ✅ `QBO_ENVIRONMENT=production`
- ✅ `QBO_CLIENT_ID` et `QBO_CLIENT_SECRET` (production)
- ✅ `DATABASE_URL` (credentials PostgreSQL)
- ✅ Clés de sécurité générées
- ✅ URLs de production

---

## 🐳 Option 1: Déploiement avec Docker (Recommandé)

### Étape 1: Préparer les fichiers sur le serveur

```bash
# Sur votre machine locale
cd /Users/alain/Documents/aia-regenord
tar -czf backend-deploy.tar.gz backend/ --exclude='backend/__pycache__' --exclude='backend/.venv' --exclude='backend/logs/*.log'

# Transférer sur le serveur (via SCP, SFTP, etc.)
scp backend-deploy.tar.gz user@votre-serveur:/home/user/
scp backend/.env user@votre-serveur:/home/user/backend/.env
```

### Étape 2: Sur le serveur

```bash
# Se connecter au serveur
ssh user@votre-serveur

# Extraire les fichiers
cd /home/user
tar -xzf backend-deploy.tar.gz
cd backend

# S'assurer que le fichier .env est présent
ls -la .env
```

### Étape 3: Construire et démarrer avec Docker

```bash
# Construire l'image Docker
docker build -t aia-regenord-backend .

# Démarrer le conteneur
docker run -d \
  --name aia-regenord-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  aia-regenord-backend

# Vérifier les logs
docker logs -f aia-regenord-backend
```

### Étape 4: Configurer Nginx (Reverse Proxy)

```nginx
# /etc/nginx/sites-available/api.regenord.com
server {
    listen 80;
    server_name api.regenord.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/api.regenord.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Étape 5: Configurer SSL avec Certbot

```bash
# Installer Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d api.regenord.com

# Certbot configure automatiquement HTTPS
```

---

## 🖥️ Option 2: Déploiement Serveur Traditionnel

### Étape 1: Installer les dépendances système

```bash
# Sur Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv python3-pip postgresql nginx

# Créer un utilisateur pour l'application
sudo adduser --system --group aia-regenord
```

### Étape 2: Préparer l'application

```bash
# Créer un dossier pour l'application
sudo mkdir -p /var/www/aia-regenord
sudo chown aia-regenord:aia-regenord /var/www/aia-regenord

# Transférer les fichiers (voir Option 1, Étape 1)
# Puis sur le serveur:
cd /var/www/aia-regenord/backend

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 3: Configurer PostgreSQL

```bash
# Créer la base de données
sudo -u postgres psql
CREATE DATABASE aia_regenord;
CREATE USER aia_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE aia_regenord TO aia_user;
\q
```

Mettre à jour `DATABASE_URL` dans `.env`:
```env
DATABASE_URL=postgresql://aia_user:votre_mot_de_passe@localhost:5432/aia_regenord
```

### Étape 4: Créer un service systemd

```bash
# Créer le fichier service
sudo nano /etc/systemd/system/aia-regenord.service
```

Contenu du fichier:
```ini
[Unit]
Description=AIA Regenord Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=aia-regenord
Group=aia-regenord
WorkingDirectory=/var/www/aia-regenord/backend
Environment="PATH=/var/www/aia-regenord/backend/venv/bin"
ExecStart=/var/www/aia-regenord/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable aia-regenord
sudo systemctl start aia-regenord

# Vérifier le statut
sudo systemctl status aia-regenord

# Voir les logs
sudo journalctl -u aia-regenord -f
```

### Étape 5: Configurer Nginx (identique à Option 1)

Voir Option 1, Étape 4 et 5.

---

## ☁️ Option 3: Déploiement Cloud (AWS, Google Cloud, Azure)

### AWS (Elastic Beanstalk ou EC2)

**Avec Elastic Beanstalk (Simple):**

```bash
# Installer EB CLI
pip install awsebcli

# Initialiser
eb init -p python-3.9 aia-regenord

# Créer un environnement
eb create aia-regenord-prod

# Configurer les variables d'environnement
eb setenv QBO_ENVIRONMENT=production QBO_CLIENT_ID=... DATABASE_URL=...

# Déployer
eb deploy
```

**Avec EC2:**
Suivre Option 2 (Serveur Traditionnel) sur une instance EC2.

### Google Cloud (App Engine)

Créer `app.yaml`:
```yaml
runtime: python39

env_variables:
  QBO_ENVIRONMENT: production
  QBO_CLIENT_ID: ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
  # ... autres variables

handlers:
- url: /.*
  script: auto
```

```bash
gcloud app deploy
```

### Heroku

```bash
# Installer Heroku CLI
# Créer une app
heroku create aia-regenord-api

# Configurer les variables
heroku config:set QBO_ENVIRONMENT=production
heroku config:set QBO_CLIENT_ID=...
# ... etc

# Déployer
git push heroku main
```

---

## 🔐 Configuration SSL/HTTPS

### Avec Certbot (Let's Encrypt - Gratuit)

```bash
# Installer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtenir un certificat
sudo certbot --nginx -d api.regenord.com

# Renouvellement automatique
sudo certbot renew --dry-run
```

### Avec Cloudflare (Recommandé)

1. Configurer DNS dans Cloudflare
2. Activer "SSL/TLS" → "Full (strict)"
3. Configurer "Always Use HTTPS"
4. Cloudflare fournit SSL automatiquement

---

## ✅ Vérification Post-Déploiement

### Test 1: Santé du Backend

```bash
curl https://api.regenord.com/health
```

**Réponse attendue:**
```json
{"status": "healthy"}
```

### Test 2: Configuration QBO

```bash
curl https://api.regenord.com/api/qbo/config/check
```

**Vérifier:**
- `"environment": "production"`
- `"ready_for_production": true`
- `"api_base_url": "https://quickbooks.api.intuit.com"`

### Test 3: Statut de Connexion

```bash
curl "https://api.regenord.com/api/qbo/status?company_id=1"
```

### Test 4: CORS

Vérifier que les requêtes depuis `https://www.regenord.com` fonctionnent:

```bash
curl -H "Origin: https://www.regenord.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://api.regenord.com/health
```

---

## 🔄 Commandes de Gestion

### Arrêter le service

```bash
# Docker
docker stop aia-regenord-backend

# Systemd
sudo systemctl stop aia-regenord
```

### Démarrer le service

```bash
# Docker
docker start aia-regenord-backend

# Systemd
sudo systemctl start aia-regenord
```

### Redémarrer le service

```bash
# Docker
docker restart aia-regenord-backend

# Systemd
sudo systemctl restart aia-regenord
```

### Voir les logs

```bash
# Docker
docker logs -f aia-regenord-backend

# Systemd
sudo journalctl -u aia-regenord -f
```

### Mettre à jour l'application

```bash
# Arrêter
sudo systemctl stop aia-regenord

# Mettre à jour les fichiers
cd /var/www/aia-regenord/backend
git pull  # ou transférer les nouveaux fichiers

# Mettre à jour les dépendances
source venv/bin/activate
pip install -r requirements.txt

# Redémarrer
sudo systemctl start aia-regenord
```

---

## 🐛 Dépannage

### Le backend ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u aia-regenord -n 50

# Vérifier la configuration
cat /var/www/aia-regenord/backend/.env

# Vérifier les permissions
ls -la /var/www/aia-regenord/backend/
```

### Erreur de connexion base de données

```bash
# Tester la connexion PostgreSQL
psql $DATABASE_URL -c "SELECT 1;"

# Vérifier que PostgreSQL est en cours d'exécution
sudo systemctl status postgresql
```

### Erreur CORS

Vérifier dans `backend/.env`:
```env
CORS_ORIGINS=["https://www.regenord.com"]
```

Redémarrer le backend après modification.

### Port 8000 déjà utilisé

```bash
# Trouver le processus
sudo lsof -i:8000

# Tuer le processus
sudo kill <PID>
```

---

## 📋 Checklist de Déploiement

- [ ] Serveur configuré avec Python 3.9+ et PostgreSQL
- [ ] Fichier `backend/.env` transféré et configuré
- [ ] Base de données PostgreSQL créée et accessible
- [ ] Application déployée (Docker ou système traditionnel)
- [ ] Service démarré et fonctionnel
- [ ] Nginx configuré comme reverse proxy
- [ ] SSL/HTTPS configuré (Certbot ou Cloudflare)
- [ ] DNS configuré: `api.regenord.com` pointe vers le serveur
- [ ] Test `/health` fonctionne
- [ ] Test `/api/qbo/config/check` retourne production
- [ ] CORS configuré pour `https://www.regenord.com`
- [ ] Logs accessibles et surveillés

---

## 🎉 Déploiement Réussi!

Une fois tout configuré, votre backend sera accessible sur:
- **URL:** `https://api.regenord.com`
- **Health Check:** `https://api.regenord.com/health`
- **API Docs:** `https://api.regenord.com/docs`

Le frontend Squarespace pourra alors se connecter correctement!

---

**Date de création:** $(date)  
**Version:** Production 1.0
