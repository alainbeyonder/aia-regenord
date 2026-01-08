# 🚀 Guide d'Installation et Démarrage du Frontend

## ❌ Problème Détecté

Le serveur React n'est pas démarré car **Node.js et npm ne sont pas installés** sur votre système.

---

## 📦 Étape 1: Installer Node.js

### Option A: Installation via Homebrew (macOS - Recommandé)

```bash
# Installer Homebrew si pas déjà installé
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Node.js (inclut npm)
brew install node

# Vérifier l'installation
node --version
npm --version
```

### Option B: Installation via le site officiel

1. Aller sur: https://nodejs.org/
2. Télécharger la version **LTS** (Long Term Support)
3. Installer le fichier `.pkg` téléchargé
4. Vérifier l'installation:
   ```bash
   node --version
   npm --version
   ```

### Option C: Installation via nvm (Node Version Manager)

```bash
# Installer nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Recharger le shell
source ~/.zshrc  # ou ~/.bash_profile

# Installer Node.js LTS
nvm install --lts
nvm use --lts

# Vérifier
node --version
npm --version
```

---

## 📋 Étape 2: Installer les Dépendances du Frontend

Une fois Node.js installé:

```bash
# Aller dans le dossier frontend
cd /Users/alain/Documents/aia-regenord/frontend

# Installer les dépendances
npm install
```

Cette commande va installer toutes les dépendances nécessaires (React, axios, recharts, etc.).

**Temps estimé:** 2-5 minutes selon votre connexion internet.

---

## 🚀 Étape 3: Démarrer le Serveur de Développement

```bash
# Toujours dans le dossier frontend
npm start
```

Le serveur va démarrer et ouvrir automatiquement votre navigateur à `http://localhost:3000`.

**Note:** Le serveur va rester en cours d'exécution. Pour l'arrêter, appuyez sur `Ctrl+C` dans le terminal.

---

## ✅ Vérification

Une fois le serveur démarré, vous devriez voir:

1. **Dans le terminal:**
   ```
   Compiled successfully!
   
   You can now view aia-regenord in the browser.
   
     Local:            http://localhost:3000
     On Your Network:  http://192.168.x.x:3000
   ```

2. **Dans le navigateur (http://localhost:3000):**
   - Titre: "📊 AIA Regenord"
   - Sous-titre: "Agent IA Financier - Projections Financières 3 Ans"
   - Bannière de statut avec l'état de connexion au backend
   - Cartes pour différentes fonctionnalités

---

## 🔧 Problèmes Courants

### Erreur: "command not found: npm"

**Cause:** Node.js n'est pas installé ou pas dans le PATH.

**Solution:**
1. Réinstaller Node.js (voir Étape 1)
2. Redémarrer le terminal après l'installation
3. Vérifier: `which node` et `which npm`

### Erreur: "npm ERR! code EACCES"

**Cause:** Problèmes de permissions.

**Solution:**
```bash
# Utiliser nvm (recommandé) ou
# Corriger les permissions npm
sudo chown -R $(whoami) ~/.npm
```

### Erreur: "Module not found" après npm install

**Solution:**
```bash
# Supprimer node_modules et réinstaller
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 déjà utilisé

**Solution:**
```bash
# Tuer le processus utilisant le port 3000
lsof -ti:3000 | xargs kill -9

# Ou démarrer sur un autre port
PORT=3001 npm start
```

### Le backend n'est pas accessible

**Vérifier:**
1. Le backend est démarré sur `http://localhost:8000`
2. L'URL dans `frontend/src/App.js` est correcte:
   ```javascript
   const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
   ```

---

## 📝 Variables d'Environnement (Optionnel)

Pour configurer l'URL du backend, créez un fichier `.env` dans `frontend/`:

```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 🔄 Commandes Utiles

```bash
# Démarrer le serveur de développement
npm start

# Construire pour la production
npm run build

# Exécuter les tests
npm test

# Vérifier les dépendances obsolètes
npm outdated
```

---

## 📚 Ressources

- **Documentation Node.js:** https://nodejs.org/docs/
- **Documentation React:** https://react.dev/
- **Documentation npm:** https://docs.npmjs.com/

---

**Une fois Node.js installé et le serveur démarré, l'application sera accessible à http://localhost:3000**
