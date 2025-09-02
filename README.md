# 🧠 OpenAI 120B Advanced

Assistant IA avancé avec capacités de développement complètes - Génération et exécution de code en temps réel.

## ✨ Fonctionnalités Avancées

### 🔧 **Génération de Code Complète**
- ✅ **Applications Web** (HTML/CSS/JS, React, Vue)
- ✅ **Applications Mobiles** (concepts React Native, Flutter)  
- ✅ **Applications Desktop** (Electron, Python tkinter)
- ✅ **APIs et Backends** (Python Flask/FastAPI, Node.js)
- ✅ **Outils et Scripts** (Python, automation)
- ✅ **Jeux Web** (JavaScript Canvas, WebGL)

### ⚡ **Exécution Python Temps Réel**
- ✅ **Exécution sécurisée** dans l'application
- ✅ **Visualisations** (matplotlib, plotly, seaborn)
- ✅ **Analyse de données** (pandas, numpy)
- ✅ **Calculs mathématiques** et statistiques
- ✅ **Debugging automatique** avec messages d'erreur

### 📁 **Gestion de Projets Automatisée**
- ✅ **Génération automatique** de structures complètes
- ✅ **Fichiers multiples** avec dépendances
- ✅ **Instructions d'installation** détaillées
- ✅ **Téléchargement ZIP** immédiat
- ✅ **Historique des projets** créés

### 📊 **Analytics et Suivi**
- ✅ **Tracking complet** des tokens utilisés
- ✅ **Coûts estimés** en temps réel
- ✅ **Statistiques de session** et globales
- ✅ **Métriques de performance** détaillées

## 🚀 Installation

### **1. Installation Locale**

```bash
# Cloner ou télécharger le projet
git clone [votre-repo] 
cd openai120b

# Installer les dépendances
pip install -r requirements.txt

# Configurer le token (créer le fichier .env)
echo "HF_TOKEN=votre_token_huggingface" > .env

# Lancer l'application
streamlit run app.py
```

### **2. Déploiement Streamlit Cloud** 

1. **GitHub**: Uploadez tous les fichiers sur un repo public
2. **Streamlit Cloud**: Connectez sur [share.streamlit.io](https://share.streamlit.io)
3. **Secrets**: Ajoutez votre `HF_TOKEN` dans les secrets Streamlit
4. **Deploy**: L'app sera disponible sur une URL publique

### **3. Installation Mobile (PWA)**

1. Ouvrez l'URL sur votre mobile
2. Menu navigateur → "Ajouter à l'écran d'accueil"  
3. L'app devient une PWA native !

## 🎯 Modes d'Utilisation

### **💬 Chat Standard**
Assistant IA général pour questions, conseils, explications.

**Exemples:**
- *"Explique-moi l'intelligence artificielle"*
- *"Comment optimiser ce code Python ?"*
- *"Donne-moi des idées pour mon projet"*

### **🔧 Génération de Code**
Création d'applications complètes et fonctionnelles.

**Exemples:**
- *"Crée une calculatrice web moderne avec design glassmorphism"*
- *"Développe une API REST pour gestion d'utilisateurs avec JWT"*
- *"Génère un portfolio responsive avec animations CSS"*

### **⚡ Exécution Python**
Écriture et exécution de code Python en temps réel.

**Exemples:**
- *"Crée un graphique des ventes par mois avec matplotlib"*
- *"Analyse ce dataset CSV et montre les tendances"*
- *"Simule 10000 lancers de dés et calcule les probabilités"*

### **🎨 Création d'Apps**
Développement de projets complets avec interface moderne.

**Exemples:**
- *"Design une app mobile de méditation avec timer"*
- *"Crée un dashboard analytics avec charts interactifs"*
- *"Développe un jeu de puzzle avec niveaux progressifs"*

## 📱 Optimisations Mobile

L'interface est entièrement responsive et optimisée pour:
- ✅ **Écrans tactiles** avec boutons 44px minimum
- ✅ **Navigation mobile** avec sidebar collapsible
- ✅ **Performance optimisée** pour 3G/4G
- ✅ **PWA support** pour installation native
- ✅ **Offline-ready** avec cache intelligent

## 💰 Coûts et Limites

### **Pricing Hugging Face**
- **Input**: $0.15 / 1M tokens  
- **Output**: $0.60 / 1M tokens
- **Exemple**: 10,000 tokens ≈ $0.0075 (moins d'1 centime)

### **Crédits Gratuits**
- **Hugging Face Free**: Crédits mensuels inclus
- **Hugging Face Pro**: 20x plus de crédits ($9/mois)

### **Comparaison vs ChatGPT**
| Fonctionnalité | ChatGPT Free | OpenAI 120B Advanced |
|---|---|---|
| **Context Window** | 16K tokens | **128K tokens** (8x plus) |
| **Max Output** | 8K tokens | **10K tokens** |
| **Code Execution** | ❌ | ✅ **Temps réel** |
| **Project Creation** | ❌ | ✅ **Automatique** |
| **File Download** | ❌ | ✅ **ZIP complet** |
| **Cost per 10K tokens** | Limité | **$0.0075** |

## 🔧 Configuration Avancée

### **Variables d'Environnement**
```bash
# Token obligatoire
HF_TOKEN=votre_token_huggingface

# Configuration optionnelle
MAX_TOKENS_DEFAULT=2500      # Tokens max par réponse
TEMPERATURE_DEFAULT=0.8      # Créativité par défaut  
AUTO_EXECUTE_CODE=false      # Exécution auto du code
CREATE_PROJECTS_AUTO=true    # Création auto des projets
```

### **Sécurité Code Execution**
L'exécution Python est sécurisée via:
- ✅ **Namespace isolé** avec modules whitelistés
- ✅ **Pas d'accès fichiers système** sensibles
- ✅ **Timeout automatique** pour éviter les boucles infinies
- ✅ **Capture d'erreurs** avec traceback détaillé

## 📊 Structure du Projet

```
openai120b/
├── app.py                    # Application principale
├── requirements.txt          # Dépendances Python  
├── .env                     # Configuration locale
├── secrets.toml             # Secrets Streamlit Cloud
├── README.md                # Documentation
├── conversations/           # Historique conversations
├── generated_projects/      # Projets créés automatiquement
└── credits_usage.json       # Statistiques d'utilisation
```

## 🎯 Exemples d'Usage

### **Créer une App Web Complète**
```
Prompt: "Crée une todo-list moderne avec:
- Interface Material Design
- Stockage localStorage  
- Filtres par statut
- Animations smooth
- Mobile-responsive"

→ Génère: HTML + CSS + JS complets
→ Crée: Structure de projet téléchargeable
→ Inclut: Instructions d'installation
```

### **Analyse de Données Python**
```
Prompt: "Analyse des ventes trimestrielles:
Q1: 15000€, Q2: 22000€, Q3: 18000€, Q4: 28000€
Crée graphiques et calcule tendances"

→ Exécute: Code Python avec matplotlib
→ Affiche: Graphiques générés
→ Calcule: Statistiques et prédictions
```

### **API Backend Complete**
```
Prompt: "Crée une API REST pour blog avec:
- CRUD articles
- Authentification JWT
- Validation données
- Documentation Swagger"

→ Génère: Code Python Flask/FastAPI
→ Crée: Structure MVC complète  
→ Inclut: Tests et déploiement
```

## 🛠️ Dépannage

### **Erreurs Communes**

**"Token non configuré"**
```bash
# Vérifiez le fichier .env
cat .env
# Doit contenir: HF_TOKEN=votre_token
```

**"Module not found"** 
```bash
# Réinstallez les dépendances
pip install -r requirements.txt --upgrade
```

**"Port already in use"**
```bash
# Utilisez un autre port
streamlit run app.py --server.port 8502
```

### **Optimisation Performance**
- ✅ Réduisez `max_tokens` pour des réponses plus rapides
- ✅ Utilisez le mode "Chat Standard" pour questions simples  
- ✅ Activez le cache Streamlit pour éviter les re-calculs
- ✅ Nettoyez l'historique régulièrement

## 🤝 Contribution

Les contributions sont bienvenues ! 

1. **Fork** le projet
2. **Créez** une branche feature
3. **Committez** vos changements
4. **Push** sur la branche
5. **Ouvrez** une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - libre d'utilisation pour projets personnels et commerciaux.

## 🆘 Support

- **Issues**: Ouvrez une issue GitHub pour les bugs
- **Discussions**: Utilisez GitHub Discussions pour les questions
- **Email**: contact@votre-domain.com

## 🎉 Remerciements

- **OpenAI** pour les modèles GPT-OSS
- **Hugging Face** pour l'infrastructure  
- **Streamlit** pour le framework web
- **Communauté Open Source** pour les contributions

---

**🚀 Transformez vos idées en applications réelles avec OpenAI 120B Advanced !**