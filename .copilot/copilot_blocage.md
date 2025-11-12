# 🆘 CONSULTATION COPILOT → CLAUDE

**Date**: 2025-11-11 19:05  
**Status**: ✅ Prêt pour questions

---

## 📝 INSTRUCTIONS POUR COPILOT

Si tu bloques sur une tâche, remplis ce formulaire et **sauvegarde le fichier**.

Claude surveille ce fichier toutes les 5 minutes et répondra dans `.copilot/claude_reponse.md`

---

## 📋 FORMULAIRE BLOCAGE

### 1. Identification
**Tâche en cours**: _[Ex: Création middleware JWT]_

**Fichier concerné**: _[Ex: api/auth_middleware.py]_

**Ligne/fonction**: _[Ex: ligne 42, fonction validate_token()]_

---

### 2. Problème
**Description courte**:
_[Ex: "Je ne sais pas comment valider la signature JWT Azure AD"]_

**Erreur complète** (si applicable):
```
[Coller l'erreur ou traceback complet ici]
```

---

### 3. Contexte
**Ce que j'essaie de faire**:
_[Ex: "Valider un JWT token reçu depuis Azure AD pour vérifier l'identité de l'utilisateur"]_

**Ce que j'ai essayé**:
1. _[Ex: "Utilisé PyJWT.decode() mais erreur signature"]_
2. _[Ex: "Essayé de récupérer les clés publiques Azure AD"]_
3. _[...]_

---

### 4. Questions Spécifiques
**Question 1**: _[Ex: "Quelle est l'URL pour les clés publiques Azure AD?"]_

**Question 2**: _[Ex: "Comment configurer PyJWT pour valider avec RS256?"]_

**Question 3**: _[Ex: "Dois-je vérifier audience et issuer?"]_

---

### 5. Code Actuel
**Code qui pose problème**:
```python
# Coller le code problématique ici
```

**Tests échouant** (si applicable):
```python
# Coller le test qui échoue
```

---

### 6. Besoin
**Type d'aide recherchée**:
- [ ] Explication conceptuelle
- [ ] Exemple de code
- [ ] Debug erreur
- [ ] Guidance architecture
- [ ] Autre: _[préciser]_

**Urgence**:
- [ ] Bloquant (ne peux pas continuer)
- [ ] Important (ralentit le progrès)
- [ ] Nice-to-have (question de curiosité)

---

### 7. Attentes
**Résultat attendu**:
_[Ex: "Code fonctionnel qui valide JWT Azure AD et retourne les claims utilisateur"]_

**Délai souhaité**:
_[Ex: "Dans l'heure si possible"]_

---

## 📊 INFORMATIONS AUTOMATIQUES

**Environnement**:
- OS: Windows (twisterlab.local)
- Python: 3.11.9 / 3.12.10
- FastAPI: 0.115.5
- Dépendances: msal==1.31.1, PyJWT, cryptography

**Projet**:
- Repo: C:\twisterlab
- Branche: feature/azure-ad-auth
- Phase: Phase 1 - Azure AD Auth (API Integration)

---

## 🔄 WORKFLOW

1. **Copilot**: Remplis ce formulaire
2. **Copilot**: Sauvegarde le fichier
3. **Claude**: Détecte le changement (polling 5 min)
4. **Claude**: Analyse et crée `.copilot/claude_reponse.md`
5. **Copilot**: Lit la réponse et continue

**Temps réponse typique**: 5-10 minutes

---

## 💡 EXEMPLE REMPLI

### 1. Identification
**Tâche en cours**: Création middleware JWT

**Fichier concerné**: api/auth_middleware.py

**Ligne/fonction**: ligne 42, fonction validate_token()

---

### 2. Problème
**Description courte**: Erreur "Invalid signature" lors de validation JWT

**Erreur complète**:
```
jwt.exceptions.InvalidSignatureError: Signature verification failed
```

---

### 3. Contexte
**Ce que j'essaie de faire**: 
Valider un JWT token Azure AD pour authentifier l'utilisateur

**Ce que j'ai essayé**:
1. Utilisé jwt.decode() avec algorithme HS256 → Erreur
2. Changé pour RS256 → Même erreur
3. Essayé de load les clés depuis Azure AD JWKS

---

### 4. Questions Spécifiques
**Question 1**: Comment récupérer les clés publiques Azure AD?

**Question 2**: Quel algorithme utiliser (RS256, HS256)?

**Question 3**: Dois-je vérifier audience/issuer?

---

### 5. Code Actuel
```python
def validate_token(self, token: str):
    decoded = jwt.decode(
        token,
        key="???",  # Quelle clé ici?
        algorithms=["RS256"],
        audience=self.client_id
    )
    return decoded
```

---

### 6. Besoin
**Type d'aide recherchée**:
- [x] Explication conceptuelle
- [x] Exemple de code
- [ ] Debug erreur

**Urgence**:
- [x] Bloquant

---

### 7. Attentes
**Résultat attendu**: Code qui valide JWT et retourne user claims

**Délai souhaité**: Dans l'heure

---

## ⚠️ NOTE IMPORTANTE

**Ce fichier est surveillé par Claude**. Dès que tu sauvegardes, la consultation est enregistrée.

**NE PAS** supprimer ce fichier. Si résolu, marque:
```markdown
## ✅ RÉSOLU
Solution: [description]
```

---

**Prêt à t'aider!** - Claude 🤖
