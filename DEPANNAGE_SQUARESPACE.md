# 🔧 Dépannage - Page Squarespace sans Interface

## ❌ Problème

La page `https://www.regenord.com/quickbooks-integration` s'ouvre mais aucune interface n'apparaît (pas de bouton, pas de texte, page vide).

---

## 🔍 Diagnostic Étape par Étape

### Étape 1: Vérifier que le Code est Injecté

1. **Aller sur la page:**
   ```
   https://www.regenord.com/quickbooks-integration
   ```

2. **Ouvrir la console du navigateur:**
   - **Chrome/Edge:** `F12` ou `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - **Firefox:** `F12` ou `Cmd+Option+K` (Mac) / `Ctrl+Shift+K` (Windows)
   - **Safari:** `Cmd+Option+C` (Mac) - nécessite d'activer le menu Développement dans Préférences

3. **Vérifier l'onglet "Console":**
   - Cherchez des erreurs en rouge
   - Cherchez des messages qui commencent par "qbo" ou "QuickBooks"

**Si vous voyez des erreurs, notez-les !**

---

### Étape 2: Vérifier le Code Source

1. **Ouvrir le code source de la page:**
   - **Mac:** `Cmd+Option+U`
   - **Windows:** `Ctrl+U`

2. **Chercher dans le code source:**
   - Appuyez sur `Cmd+F` (Mac) ou `Ctrl+F` (Windows)
   - Cherchez: `qbo-integration-container` ou `BACKEND_URL`
   - Cherchez: `https://api.regenord.com`

**Si ces éléments ne sont PAS présents, le code n'est pas injecté !**

---

### Étape 3: Vérifier l'Injection dans Squarespace

1. **Se connecter à Squarespace:**
   - Aller sur: https://www.squarespace.com
   - Se connecter avec votre compte

2. **Vérifier le code injecté:**
   - Aller à: **Settings** → **Advanced** → **Code Injection**
   - Vérifier la section **Footer**
   - Le code devrait être présent (plusieurs lignes de JavaScript)

3. **Si le code n'est pas là:**
   - Ouvrir `SQUARESPACE_CODE_INJECTION_READY.html`
   - Sélectionner tout (`Cmd+A` / `Ctrl+A`)
   - Copier (`Cmd+C` / `Ctrl+C`)
   - Coller dans la section Footer
   - Cliquer sur **Save**

---

## 🐛 Problèmes Courants et Solutions

### Problème 1: "Cannot connect to backend" ou Erreur CORS

**Symptômes:**
- Console montre des erreurs de fetch
- Messages "Failed to fetch" ou "CORS error"

**Solutions:**

**A. Vérifier que le backend de production est accessible:**
```bash
curl https://api.regenord.com/health
```

**B. Si le backend n'est PAS déployé sur api.regenord.com:**
- Option 1: Déployer le backend sur `https://api.regenord.com`
- Option 2: Modifier le code Squarespace pour pointer vers votre backend local (pour tests seulement)

**C. Vérifier CORS dans le backend:**
- Le backend doit avoir `CORS_ORIGINS` incluant `https://www.regenord.com`

---

### Problème 2: Le Code n'apparaît pas du tout

**Symptômes:**
- Page complètement vide
- Aucune erreur dans la console
- Le code source ne contient pas le script

**Solution:**
1. Vérifier que le code est dans **Footer** (pas Header)
2. Vérifier qu'il n'y a pas de balises `<!-- -->` qui commentent le code
3. Réinjecter le code depuis `SQUARESPACE_CODE_INJECTION_READY.html`

---

### Problème 3: Erreur JavaScript

**Symptômes:**
- Erreurs dans la console du navigateur
- Messages comme "Uncaught TypeError" ou "ReferenceError"

**Solution:**
1. Vérifier que le code est complet (pas coupé)
2. Vérifier qu'il n'y a pas de caractères spéciaux corrompus
3. Utiliser `SQUARESPACE_CODE_CLEAN.html` (version sans commentaires HTML)

---

### Problème 4: Le Backend Local fonctionne mais Production non

**Symptômes:**
- `http://localhost:8000` fonctionne
- `https://api.regenord.com` ne répond pas

**Solution:**
1. **Déployer le backend sur api.regenord.com:**
   - Suivre le guide: `DEPLOIEMENT_ETAPE_PAR_ETAPE.md`
   - S'assurer que le backend est accessible publiquement

2. **Pour tester localement avec Squarespace (temporaire):**
   - Utiliser un tunnel (ngrok, localtunnel)
   - Ou modifier temporairement le code pour pointer vers localhost (ne fonctionnera que pour vous)

---

## 🔧 Solutions Rapides

### Solution A: Vérifier le Backend de Production

```bash
# Tester si le backend est accessible
curl https://api.regenord.com/health

# Tester la configuration QBO
curl https://api.regenord.com/api/qbo/config/check
```

**Si ça ne fonctionne pas:** Le backend n'est pas déployé sur api.regenord.com.

---

### Solution B: Utiliser le Backend Local (Pour Tests)

**⚠️ ATTENTION:** Cela ne fonctionnera que sur votre machine locale !

1. **Modifier le code Squarespace temporairement:**
   - Dans `SQUARESPACE_CODE_INJECTION_READY.html`
   - Changer: `const BACKEND_URL = 'https://api.regenord.com';`
   - Par: `const BACKEND_URL = 'http://localhost:8000';` (ou votre IP locale)

2. **Réinjecter dans Squarespace**

**Note:** Cette solution ne fonctionnera que si:
- Vous accédez depuis la même machine où tourne le backend
- Ou vous configurez un tunnel (ngrok)

---

### Solution C: Créer un Version de Test

Créer un fichier de test pour vérifier que le code fonctionne:

```html
<!-- TEST_SQUARESPACE.html -->
<script>
console.log('🔍 Test du script Squarespace...');
const BACKEND_URL = 'https://api.regenord.com';
console.log('Backend URL:', BACKEND_URL);

// Tester la connexion
fetch(`${BACKEND_URL}/health`)
  .then(r => r.json())
  .then(data => console.log('✅ Backend accessible:', data))
  .catch(err => console.error('❌ Erreur backend:', err));

// Tester l'initialisation
setTimeout(() => {
  console.log('🔍 Vérification du DOM...');
  console.log('Body:', document.body);
  console.log('Page content:', document.querySelector('.page-content'));
  console.log('Main:', document.querySelector('main'));
}, 2000);
</script>
```

Injecter ce code temporairement pour voir les messages dans la console.

---

## 📋 Checklist de Vérification

- [ ] Le code est injecté dans Squarespace (Settings > Advanced > Code Injection > Footer)
- [ ] Le code source de la page contient `qbo-integration-container` ou `BACKEND_URL`
- [ ] Aucune erreur JavaScript dans la console du navigateur
- [ ] Le backend `https://api.regenord.com` est accessible (curl fonctionne)
- [ ] Le backend de production est déployé et en cours d'exécution
- [ ] CORS est configuré dans le backend pour autoriser `https://www.regenord.com`

---

## 🆘 Si Rien Ne Fonctionne

1. **Vérifier les logs Squarespace:**
   - Squarespace peut avoir des logs d'erreur dans le panneau d'administration

2. **Tester avec un code minimal:**
   ```html
   <script>
   alert('Test - Code injecté avec succès!');
   </script>
   ```
   - Si cette alerte apparaît, le code est injecté
   - Si elle n'apparaît pas, vérifier l'injection

3. **Contacter le support:**
   - Avoir les messages d'erreur de la console
   - Avoir un screenshot de la page
   - Avoir vérifié tous les points de la checklist

---

**Date de création:** $(date)  
**Version:** Production 1.0
