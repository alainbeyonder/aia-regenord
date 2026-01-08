# ⚡ Déploiement Rapide Backend - Production

Guide de démarrage rapide pour déployer le backend sur `https://api.regenord.com`.

---

## 🎯 Choix de la Méthode

### Option A: Docker (Recommandé - Plus simple)
👉 Voir **Section 1** ci-dessous

### Option B: Serveur Traditionnel (Plus de contrôle)
👉 Voir **Section 2** ci-dessous

### Option C: Cloud (AWS, Google Cloud, etc.)
👉 Voir **Section 3** ci-dessous

---

## 🐳 Section 1: Déploiement avec Docker

### Prérequis

- Serveur avec Docker installé
- Accès SSH au serveur
- Domaine `api.regenord.com` pointant vers le serveur

### Étapes Rapides

#### 1. Sur votre machine locale

```bash
cd /Users/alain/Documents/aia-regenord

# Créer un package pour déploiement
tar -czf backend-deploy.tar.gz \
  backend/ \
  --exclude='backend/__pycache__' \
  --exclude='backend/.venv' \
  --exclude='backend/logs/*.log' \
  --exclude='backend/*.pyc'

# Transférer sur le serveur
scp backend-deploy.tar.gz user@votre-serveur:/tmp/
scp backend/.env user@votre-serveur:/tmp/backend.env
```

#### 2. Sur le serveur

```bash
# Se connecter
ssh user@votre-serveur

# Créer un dossier pour l'application
sudo mkdir -p /opt/aia-regenord
cd /opt/aia-regenord

# Extraire les fichiers
tar -xzf /tmp/backend-deploy.tar.gz
mv /tmp/backend.env backend/.env

# Construire et démarrer avec Docker
cd backend
docker build -t aia-regenord-backend .

docker run -d \
  --name aia-regenord-backend \
  --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  --env-file .env \
  aia-regenord-backend

# Vérifier
docker logs aia-regenord-backend
curl http://localhost:8000/health
```

#### 3. Configurer Nginx

```bash
# Installer Nginx
sudo apt-get update
sudo apt-get install -y nginx

# Créer la configuration
sudo nano /etc/nginx/sites-available/api.regenord.com
```

Contenu:
```nginx
server {
    listen 80;
    server_name api.regenord.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activer
sudo ln -s /etc/nginx/sites-available/api.regenord.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Configurer SSL

```bash
# Installer Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d api.regenord.com

# Tester le renouvellement
sudo certbot renew --dry-run
```

#### 5. Vérifier

```bash
# Test local
curl http://localhost:8000/health

# Test externe
curl https://api.regenord.com/health

# Test configuration QBO
curl https://api.regenord.com/api/qbo/config/check
```

---

## 🖥️ Section 2: Serveur Traditionnel

### Prérequis

- Serveur Ubuntu/Debian
- Python 3.9+ installé
- PostgreSQL installé
- Accès root ou sudo

### Étapes Rapides

#### 1. Installer les dépendances système

```bash
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3-pip postgresql nginx
```

#### 2. Créer la base de données

```bash
sudo -u postgres psql << EOF
CREATE DATABASE aia_regenord;
CREATE USER aia_user WITH PASSWORD 'VOTRE_MOT_DE_PASSE';
GRANT ALL PRIVILEGES ON DATABASE aia_regenord TO aia_user;
\q
EOF
```

#### 3. Préparer l'application

```bash
# Créer un dossier pour l'application
sudo mkdir -p /var/www/aia-regenord
sudo chown $USER:$USER /var/www/aia-regenord
cd /var/www/aia-regenord

# Extraire les fichiers (transférés depuis votre machine)
tar -xzf /tmp/backend-deploy.tar.gz
mv /tmp/backend.env backend/.env

# Configurer DATABASE_URL dans .env
nano backend/.env
# Modifier: DATABASE_URL=postgresql://aia_user:VOTRE_MOT_DE_PASSE@localhost:5432/aia_regenord
```

#### 4. Créer l'environnement virtuel

```bash
cd /var/www/aia-regenord/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Créer le service systemd

```bash
sudo nano /etc/systemd/system/aia-regenord.service
```

Contenu:
```ini
[Unit]
Description=AIA Regenord Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/aia-regenord/backend
Environment="PATH=/var/www/aia-regenord/backend/venv/bin"
ExecStart=/var/www/aia-regenord/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer
sudo systemctl daemon-reload
sudo systemctl enable aia-regenord
sudo systemctl start aia-regenord
sudo systemctl status aia-regenord
```

#### 6. Configurer Nginx (identique à Section 1)

Voir Section 1, étape 3 et 4.

---

## ☁️ Section 3: Déploiement Cloud

### Heroku (Le plus simple)

```bash
# Installer Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Se connecter
heroku login

# Créer une app
cd /Users/alain/Documents/aia-regenord/backend
heroku create aia-regenord-api

# Configurer les variables
heroku config:set QBO_ENVIRONMENT=production
heroku config:set QBO_CLIENT_ID=ABhjTWUsPqScOqpWeCghMKHpx85MbL0fM9JQnt4uXpD4Wynk
heroku config:set QBO_CLIENT_SECRET=d2R1L2EFjbZyNmJdcYnnbibh6AVsIVlZDFF9dc8V
heroku config:set QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback
heroku config:set APP_BASE_URL=https://aia-regenord-api.herokuapp.com
heroku config:set FRONTEND_URL=https://www.regenord.com
heroku config:set DATABASE_URL=postgresql://...  # Configurer PostgreSQL addon
heroku config:set AIA_TOKEN_ENCRYPTION_KEY=Jc8GWiI1zrJ9a-aWYgETa42PLx3FRUjbkJzQ_SEIg3c=
heroku config:set SECRET_KEY=o8x80d_-Uu_uPbE0vASawCqen_BrSr8hVtkelay_cpU

# Créer Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Déployer
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a aia-regenord-api
git push heroku main

# Vérifier
heroku open
curl https://aia-regenord-api.herokuapp.com/health
```

**Note:** Avec Heroku, l'URL sera `https://aia-regenord-api.herokuapp.com` (ou votre nom d'app). Mettre à jour `APP_BASE_URL` et le code Squarespace en conséquence.

### Railway (Simple et moderne)

```bash
# Installer Railway CLI
npm i -g @railway/cli

# Se connecter
railway login

# Initialiser
railway init

# Déployer
railway up

# Configurer les variables dans le dashboard Railway
# https://railway.app
```

### Render (Simple)

1. Créer un compte sur https://render.com
2. Créer un nouveau "Web Service"
3. Connecter votre repository GitHub
4. Configurer:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Ajouter les variables d'environnement dans le dashboard
6. Déployer

---

## 🔧 Configuration DNS

### Pour que `api.regenord.com` fonctionne

1. **Aller dans votre panneau DNS** (où vous gérez le domaine regenord.com)
2. **Créer un enregistrement A:**
   - **Type:** A
   - **Nom:** api (ou api.regenord.com)
   - **Valeur:** L'IP de votre serveur
   - **TTL:** 3600

3. **Ou créer un enregistrement CNAME:**
   - **Type:** CNAME
   - **Nom:** api
   - **Valeur:** Votre serveur (ex: server.regenord.com)

4. **Attendre la propagation DNS** (5-30 minutes généralement)

---

## ✅ Vérification Finale

### Checklist

- [ ] Backend accessible: `curl https://api.regenord.com/health`
- [ ] Configuration QBO correcte: `curl https://api.regenord.com/api/qbo/config/check`
- [ ] CORS configuré pour `https://www.regenord.com`
- [ ] SSL/HTTPS fonctionne (pas d'erreur de certificat)
- [ ] DNS configuré: `api.regenord.com` pointe vers le serveur
- [ ] Base de données accessible et connectée
- [ ] Logs accessibles et pas d'erreurs critiques

### Tests

```bash
# Test 1: Santé
curl https://api.regenord.com/health
# Réponse: {"status":"healthy"}

# Test 2: Configuration QBO
curl https://api.regenord.com/api/qbo/config/check
# Vérifier: "environment": "production", "ready_for_production": true

# Test 3: Depuis Squarespace (dans la console navigateur sur regenord.com)
fetch('https://api.regenord.com/health')
  .then(r => r.json())
  .then(console.log)
```

---

## 🎉 Déploiement Réussi!

Une fois déployé, votre backend sera accessible sur:
- **URL:** `https://api.regenord.com`
- **Health:** `https://api.regenord.com/health`
- **Docs:** `https://api.regenord.com/docs`

Le frontend Squarespace pourra alors se connecter correctement!

---

## 📚 Documentation Complète

Pour plus de détails, voir:
- **Guide complet:** `GUIDE_DEPLOIEMENT_BACKEND.md`
- **Guide étape par étape:** `DEPLOIEMENT_ETAPE_PAR_ETAPE.md`

---

**Date de création:** $(date)  
**Version:** Production 1.0
