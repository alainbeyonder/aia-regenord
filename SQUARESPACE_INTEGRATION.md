# Intégration QuickBooks Online sur Squarespace

## 📋 Informations Nécessaires

Avant de déployer, vous devez avoir :

1. **Credentials QuickBooks Production**
   - Client ID de production
   - Client Secret de production
   - Application configurée dans Intuit Developer (mode Production)

2. **URLs Backend**
   - URL de votre backend en production (ex: `https://api.regenord.com`)
   - Endpoints OAuth configurés

3. **URLs Squarespace**
   - Page: `https://www.regenord.com/quickbooks-integration`
   - Launch: `/quickbooks-integration/connect`
   - Callback: `/quickbooks-integration/callback`
   - Disconnect: `/quickbooks-integration/disconnect`

---

## 🔧 Configuration Backend

### 1. Variables d'environnement Production

Mettre à jour `backend/.env`:

```env
# QuickBooks Production
QBO_ENVIRONMENT=production
QBO_CLIENT_ID=<VOTRE_CLIENT_ID_PRODUCTION>
QBO_CLIENT_SECRET=<VOTRE_CLIENT_SECRET_PRODUCTION>
QBO_REDIRECT_URI=https://www.regenord.com/quickbooks-integration/callback

# Backend URL
APP_BASE_URL=https://api.regenord.com
FRONTEND_URL=https://www.regenord.com

# CORS
CORS_ORIGINS=["https://www.regenord.com"]
```

### 2. Endpoints Backend Requis

Votre backend doit exposer ces endpoints:

- `GET /api/qbo/connect/production?company_id=1` - Connexion OAuth
- `GET /api/qbo/callback?code=...&realmId=...&state=...` - Callback OAuth
- `POST /api/qbo/disconnect?company_id=1` - Déconnexion
- `GET /api/qbo/status?company_id=1` - Statut de connexion

---

## 📝 Code d'Injection Squarespace

### Instructions

1. Aller dans Squarespace: **Settings > Advanced > Code Injection**
2. Coller le code suivant dans **Footer** (ou **Header** si préféré)
3. Remplacer `YOUR_BACKEND_URL` par l'URL de votre backend

### Code HTML/JavaScript

```html
<script>
(function() {
  // Configuration
  const BACKEND_URL = 'YOUR_BACKEND_URL'; // Ex: https://api.regenord.com
  const COMPANY_ID = 1; // ID de l'entreprise dans votre système
  
  // Fonctions utilitaires
  function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `qbo-message qbo-${type}`;
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
      padding: 15px;
      margin: 15px 0;
      border-radius: 8px;
      background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
      color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
      border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'error' ? '#f5c6cb' : '#bee5eb'};
    `;
    
    const container = document.querySelector('.qbo-integration-container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);
    
    setTimeout(() => {
      messageDiv.remove();
    }, 5000);
  }
  
  function setLoading(button, loading) {
    if (loading) {
      button.disabled = true;
      button.dataset.originalText = button.textContent;
      button.textContent = '⏳ Connexion en cours...';
    } else {
      button.disabled = false;
      button.textContent = button.dataset.originalText || button.textContent;
    }
  }
  
  // Fonction de connexion
  async function connectQuickBooks() {
    const button = document.getElementById('qbo-connect-btn');
    setLoading(button, true);
    
    try {
      // Obtenir l'URL d'autorisation
      const response = await fetch(`${BACKEND_URL}/api/qbo/connect/production?company_id=${COMPANY_ID}&redirect=false`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.auth_url) {
        // Rediriger vers Intuit OAuth
        window.location.href = data.auth_url;
      } else {
        throw new Error('URL d\'autorisation non reçue');
      }
    } catch (error) {
      console.error('Erreur de connexion:', error);
      showMessage(`Erreur de connexion: ${error.message}`, 'error');
      setLoading(button, false);
    }
  }
  
  // Fonction de déconnexion
  async function disconnectQuickBooks() {
    if (!confirm('Êtes-vous sûr de vouloir déconnecter QuickBooks ?')) {
      return;
    }
    
    const button = document.getElementById('qbo-disconnect-btn');
    setLoading(button, true);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/qbo/disconnect?company_id=${COMPANY_ID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }
      
      showMessage('QuickBooks déconnecté avec succès', 'success');
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
      showMessage(`Erreur de déconnexion: ${error.message}`, 'error');
      setLoading(button, false);
    }
  }
  
  // Vérifier le statut de connexion
  async function checkConnectionStatus() {
    try {
      const response = await fetch(`${BACKEND_URL}/api/qbo/status?company_id=${COMPANY_ID}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`);
      }
      
      const status = await response.json();
      
      const statusDiv = document.getElementById('qbo-status');
      const connectBtn = document.getElementById('qbo-connect-btn');
      const disconnectBtn = document.getElementById('qbo-disconnect-btn');
      
      if (status.connected) {
        statusDiv.innerHTML = `
          <div style="padding: 15px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; color: #155724;">
            <strong>✅ Connecté</strong>
            ${status.realm_id ? `<br><small>Realm ID: ${status.realm_id}</small>` : ''}
            ${status.last_sync ? `<br><small>Dernière sync: ${new Date(status.last_sync).toLocaleString('fr-CA')}</small>` : ''}
          </div>
        `;
        connectBtn.style.display = 'none';
        disconnectBtn.style.display = 'inline-block';
      } else {
        statusDiv.innerHTML = `
          <div style="padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; color: #856404;">
            <strong>⏳ Non connecté</strong>
            <br><small>Cliquez sur "Connecter QuickBooks" pour commencer</small>
          </div>
        `;
        connectBtn.style.display = 'inline-block';
        disconnectBtn.style.display = 'none';
      }
    } catch (error) {
      console.error('Erreur de vérification du statut:', error);
      const statusDiv = document.getElementById('qbo-status');
      statusDiv.innerHTML = `
        <div style="padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; color: #721c24;">
          <strong>❌ Erreur</strong>
          <br><small>Impossible de vérifier le statut: ${error.message}</small>
        </div>
      `;
    }
  }
  
  // Gérer le callback OAuth
  function handleOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const qboConnected = urlParams.get('qbo_connected');
    const realmId = urlParams.get('realm_id');
    
    if (qboConnected === 'true') {
      showMessage(`✅ QuickBooks connecté avec succès! Realm ID: ${realmId}`, 'success');
      // Nettoyer l'URL
      window.history.replaceState({}, document.title, window.location.pathname);
      // Recharger le statut
      setTimeout(() => checkConnectionStatus(), 1000);
    }
  }
  
  // Initialisation
  document.addEventListener('DOMContentLoaded', function() {
    // Attendre que la page soit chargée
    setTimeout(() => {
      // Créer le conteneur d'intégration si nécessaire
      let container = document.querySelector('.qbo-integration-container');
      if (!container) {
        // Chercher un élément existant ou créer un nouveau conteneur
        const pageContent = document.querySelector('.page-content') || document.querySelector('main') || document.body;
        container = document.createElement('div');
        container.className = 'qbo-integration-container';
        container.style.cssText = 'max-width: 800px; margin: 40px auto; padding: 20px;';
        pageContent.appendChild(container);
      }
      
      // Ajouter le HTML de l'interface
      if (!document.getElementById('qbo-status')) {
        container.innerHTML = `
          <div style="text-align: center; margin-bottom: 30px;">
            <h2>🔗 Intégration QuickBooks Online</h2>
            <p>Connectez votre compte QuickBooks pour synchroniser vos données financières.</p>
          </div>
          
          <div id="qbo-status" style="margin: 20px 0;">
            <div style="padding: 15px; text-align: center;">
              <p>Chargement du statut...</p>
            </div>
          </div>
          
          <div style="text-align: center; margin: 30px 0;">
            <button id="qbo-connect-btn" 
                    onclick="connectQuickBooks()"
                    style="
                      background: #667eea;
                      color: white;
                      border: none;
                      padding: 15px 30px;
                      font-size: 16px;
                      border-radius: 8px;
                      cursor: pointer;
                      font-weight: 600;
                      transition: background 0.2s;
                    "
                    onmouseover="this.style.background='#5568d3'"
                    onmouseout="this.style.background='#667eea'">
              🔗 Connecter QuickBooks
            </button>
            
            <button id="qbo-disconnect-btn" 
                    onclick="disconnectQuickBooks()"
                    style="
                      background: #f44336;
                      color: white;
                      border: none;
                      padding: 15px 30px;
                      font-size: 16px;
                      border-radius: 8px;
                      cursor: pointer;
                      font-weight: 600;
                      margin-left: 15px;
                      display: none;
                      transition: background 0.2s;
                    "
                    onmouseover="this.style.background='#d32f2f'"
                    onmouseout="this.style.background='#f44336'">
              🚫 Déconnecter QuickBooks
            </button>
          </div>
          
          <div style="margin-top: 40px; padding: 20px; background: #f5f7fa; border-radius: 8px;">
            <h3 style="margin-top: 0;">ℹ️ Informations</h3>
            <ul style="line-height: 1.8;">
              <li>La connexion est sécurisée via OAuth 2.0</li>
              <li>Vos données sont synchronisées automatiquement</li>
              <li>Vous pouvez déconnecter à tout moment</li>
              <li>Les tokens sont stockés de manière sécurisée</li>
            </ul>
          </div>
        `;
      }
      
      // Vérifier le statut au chargement
      checkConnectionStatus();
      
      // Gérer le callback OAuth
      handleOAuthCallback();
      
      // Exposer les fonctions globalement pour les boutons
      window.connectQuickBooks = connectQuickBooks;
      window.disconnectQuickBooks = disconnectQuickBooks;
    }, 500);
  });
})();
</script>
```

---

## 🔄 Gestion du Callback OAuth

Le callback OAuth doit rediriger vers Squarespace avec les paramètres de succès.

### Modification Backend (si nécessaire)

Dans `backend/app/api/qbo.py`, modifier la fonction `qbo_callback`:

```python
@router.get("/callback")
def qbo_callback(code: str, realmId: str, state: str):
    """
    Reçoit le code OAuth et le realmId, échange contre tokens et sauvegarde.
    Redirige vers Squarespace après connexion réussie.
    """
    QBOService.handle_callback(code=code, realm_id=realmId, state=state)
    
    # Rediriger vers Squarespace
    squarespace_url = "https://www.regenord.com/quickbooks-integration"
    return RedirectResponse(url=f"{squarespace_url}?qbo_connected=true&realm_id={realmId}")
```

---

## ✅ Checklist de Déploiement

### Backend
- [ ] Backend déployé en production avec HTTPS
- [ ] Variables d'environnement production configurées
- [ ] `QBO_REDIRECT_URI` = `https://www.regenord.com/quickbooks-integration/callback`
- [ ] CORS configuré pour `https://www.regenord.com`
- [ ] Endpoints testés et fonctionnels

### Intuit Developer
- [ ] Application en mode Production
- [ ] Client ID et Secret de production obtenus
- [ ] Redirect URI configurée: `https://www.regenord.com/quickbooks-integration/callback`
- [ ] Scopes autorisés: `com.intuit.quickbooks.accounting openid profile email`

### Squarespace
- [ ] Code d'injection ajouté dans Settings > Advanced > Code Injection
- [ ] `YOUR_BACKEND_URL` remplacé par l'URL réelle du backend
- [ ] Page `/quickbooks-integration` créée et accessible
- [ ] Test de connexion effectué

---

## 🧪 Tests

1. **Test de connexion**
   - Aller sur `https://www.regenord.com/quickbooks-integration`
   - Cliquer sur "Connecter QuickBooks"
   - Autoriser l'application dans Intuit
   - Vérifier la redirection et le message de succès

2. **Test de statut**
   - Vérifier que le statut affiche "✅ Connecté"
   - Vérifier que le Realm ID est affiché

3. **Test de déconnexion**
   - Cliquer sur "Déconnecter QuickBooks"
   - Confirmer la déconnexion
   - Vérifier que le statut change

---

## 📞 Support

En cas de problème:
1. Vérifier la console du navigateur (F12) pour les erreurs
2. Vérifier les logs du backend
3. Vérifier que les URLs sont correctes (HTTPS, pas de slash final)
4. Vérifier que CORS est configuré correctement
