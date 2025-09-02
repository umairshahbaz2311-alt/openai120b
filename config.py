"""
Configuration personnalisable pour OpenAI 120B Advanced - Version Corrigée
Modifiez ce fichier pour personnaliser votre assistant IA
"""

import streamlit as st
import json
import datetime
import re
import os
from typing import Dict, List, Any

# ==========================================
# 🎨 CONFIGURATION DES THÈMES
# ==========================================

THEMES = {
    "default_light": {
        "primary_color": "#667eea",
        "secondary_color": "#764ba2", 
        "background_color": "#ffffff",
        "text_color": "#000000",
        "card_background": "#f8f9fa",
        "border_color": "#e0e0e0",
        "success_color": "#10b981",
        "warning_color": "#f59e0b",
        "error_color": "#ef4444"
    },
    "default_dark": {
        "primary_color": "#4CAF50",
        "secondary_color": "#2196F3",
        "background_color": "#0f0f23",
        "text_color": "#e0e6ed",
        "card_background": "#16213e",
        "border_color": "#304570",
        "success_color": "#10b981",
        "warning_color": "#f59e0b", 
        "error_color": "#ef4444"
    },
    "cyberpunk": {
        "primary_color": "#ff0080",
        "secondary_color": "#00ffff",
        "background_color": "#0a0a0a",
        "text_color": "#00ff41",
        "card_background": "#1a1a2e",
        "border_color": "#ff0080",
        "success_color": "#00ff41",
        "warning_color": "#ffff00",
        "error_color": "#ff0080"
    },
    "nature": {
        "primary_color": "#2d5016",
        "secondary_color": "#7cb342",
        "background_color": "#f1f8e9",
        "text_color": "#1b5e20",
        "card_background": "#e8f5e8",
        "border_color": "#a5d6a7",
        "success_color": "#4caf50",
        "warning_color": "#ff9800",
        "error_color": "#f44336"
    },
    "ocean": {
        "primary_color": "#006064",
        "secondary_color": "#0097a7",
        "background_color": "#e0f2f1",
        "text_color": "#004d40",
        "card_background": "#b2dfdb",
        "border_color": "#4db6ac",
        "success_color": "#009688",
        "warning_color": "#ff9800",
        "error_color": "#f44336"
    }
}

# ==========================================
# 🤖 CONFIGURATION DE L'IA
# ==========================================

AI_CONFIG = {
    "default_model": "openai/gpt-oss-120b:together",
    "max_tokens_range": {
        "min": 100,
        "max": 8000,
        "default": 2000,
        "step": 250
    },
    "temperature_range": {
        "min": 0.0,
        "max": 2.0,
        "default": 0.7,
        "step": 0.1
    },
    "conversation_memory": {
        "max_messages": 20,
        "max_chars_per_message": 2000,
        "context_window": 6
    },
    "retry_attempts": 3,
    "timeout_seconds": 45
}

# ==========================================
# 📝 PROMPTS SYSTÈME OPTIMISÉS
# ==========================================

SYSTEM_PROMPTS = {
    "chat": """Tu es un assistant IA avancé créé pour aider les utilisateurs avec des réponses précises et détaillées.

PERSONNALITÉ:
- Réponds de manière claire et structurée
- Sois créatif mais factuel
- Adapte ton ton à l'utilisateur
- Pose des questions de clarification si nécessaire

CAPACITÉS:
- Analyse de fichiers uploadés (CSV, images, texte)
- Génération de code complet et fonctionnel
- Exécution de Python sécurisée
- Création de projets téléchargeables

Réponds toujours en français sauf si demandé autrement.""",

    "code": """Tu es un architecte logiciel expert avec 15+ ans d'expérience.

EXPERTISE TECHNIQUE:
🌐 Web: HTML5/CSS3, JavaScript ES6+, React, Vue.js
🖥️ Desktop: Electron, Python Tkinter, Qt
📱 Mobile: React Native, Flutter (concepts)
🔧 Backend: Python (FastAPI/Flask), Node.js, APIs REST
🎨 Design: UI/UX moderne, responsive, accessible

POUR CRÉER UN PROJET, utilise OBLIGATOIREMENT ce format JSON:
```json
{
  "name": "nom_du_projet",
  "description": "Description complète et détaillée",
  "type": "web|desktop|mobile|api|tool",
  "files": [
    {
      "name": "index.html",
      "content": "<!DOCTYPE html>\\n<html>\\n<head>\\n  <title>Titre</title>\\n</head>\\n<body>\\n  <!-- Contenu -->\\n</body>\\n</html>",
      "description": "Page principale de l'application"
    }
  ],
  "installation": "Instructions détaillées d'installation",
  "usage": "Guide d'utilisation pour l'utilisateur final"
}
```

RÈGLES STRICTES:
- Code complet et entièrement fonctionnel
- Commentaires détaillés et explicatifs
- Sécurité et bonnes pratiques respectées
- Design moderne et responsive""",

    "python": """Tu es un expert en data science et développement Python.

MODULES DISPONIBLES:
✅ Autorisés: math, datetime, json, random, time, re, statistics, numpy, pandas
❌ Interdits: os, sys, subprocess, eval, exec, __import__, open, file

SPÉCIALITÉS:
📊 Analyse de données avec pandas/numpy
📈 Visualisations avec matplotlib
🧮 Calculs mathématiques et statistiques
🔍 Traitement de texte avec regex
🎲 Simulations et modélisation

FORMAT DE RÉPONSE:
1. Explication claire du problème
2. Code Python complet et commenté
3. Utilisation de print() pour les résultats
4. Gestion d'erreurs appropriée

RÈGLES DE SÉCURITÉ:
- Jamais d'opérations sur fichiers système
- Code exécutable dans sandbox uniquement
- Validation des entrées"""
}

# ==========================================
# 🔧 CONFIGURATION FONCTIONNALITÉS
# ==========================================

FEATURES_CONFIG = {
    "auto_execute_python": True,
    "auto_create_projects": True, 
    "save_chat_history": True,
    "show_token_usage": True,
    "show_cost_estimation": True,
    "enable_file_upload": True,
    "max_file_size_mb": 25,
    "supported_file_types": [
        'txt', 'py', 'js', 'html', 'css', 'md', 'json',
        'csv', 'xlsx', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf'
    ],
    "dark_mode_default": False,
    "enable_code_highlighting": True,
    "enable_auto_scroll": True
}

# ==========================================
# 🎯 CONFIGURATION SÉCURITÉ
# ==========================================

SECURITY_CONFIG = {
    "python_execution": {
        "max_execution_time": 15,
        "max_memory_mb": 150,
        "max_code_length": 10000,
        "allowed_modules": {
            'math', 'datetime', 'json', 'random', 'time', 're', 
            'statistics', 'numpy', 'pandas', 'matplotlib'
        },
        "blocked_functions": {
            'exec', 'eval', 'compile', '__import__', 'open', 'file',
            'input', 'raw_input', 'reload', 'vars', 'globals', 'locals',
            'setattr', 'getattr', 'hasattr', 'delattr'
        },
        "blocked_patterns": [
            r'\bos\.',
            r'\bsys\.',
            r'\bsubprocess\.',
            r'__.*__',
            r'import\s+os',
            r'from\s+os',
            r'import\s+sys',
            r'from\s+sys'
        ]
    },
    "file_upload": {
        "max_file_size_mb": 25,
        "allowed_extensions": {
            'text': ['txt', 'md', 'py', 'js', 'html', 'css', 'json'],
            'data': ['csv', 'xlsx', 'json'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'document': ['pdf']
        },
        "scan_for_malware": False,
        "quarantine_suspicious": True
    }
}

# ==========================================
# 🎨 GÉNÉRATION CSS DYNAMIQUE
# ==========================================

def generate_custom_css(theme_name: str = "default_light") -> str:
    """Génère le CSS personnalisé basé sur le thème sélectionné"""
    
    theme = THEMES.get(theme_name, THEMES["default_light"])
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: {theme['background_color']};
        color: {theme['text_color']};
        transition: all 0.3s ease;
    }}
    
    .main-header {{
        font-size: clamp(2.5rem, 6vw, 4rem);
        font-weight: 800;
        text-align: center;
        margin: 2rem 0;
        background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .usage-card {{
        background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }}
    
    .usage-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }}
    
    .feature-badge {{
        background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.3rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }}
    
    .feature-badge:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }}
    
    .metric-card {{
        background: {theme['card_background']};
        border: 1px solid {theme['border_color']};
        border-left: 4px solid {theme['primary_color']};
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}
    
    .code-result {{
        background: {theme['card_background']};
        border: 1px solid {theme['border_color']};
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Fira Code', 'Monaco', 'Menlo', monospace;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    .stButton > button {{
        background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.2);
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .main-header {{
            font-size: 2rem;
            margin: 1rem 0;
        }}
        .usage-card {{
            padding: 1rem;
        }}
        .feature-badge {{
            font-size: 0.75rem;
            padding: 0.4rem 0.8rem;
        }}
    }}
    </style>
    """

# ==========================================
# 🎯 CONFIGURATION INTERFACE
# ==========================================

UI_MESSAGES = {
    "welcome": {
        "title": "🧠 Bienvenue dans OpenAI 120B Advanced",
        "subtitle": "Assistant IA avec exécution Python et génération de projets",
        "description": """
        Interface optimisée pour une productivité maximale :
        - ⚡ **Exécution Python Sécurisée** - Code dans un sandbox protégé
        - 🚀 **Génération de Projets** - Applications complètes téléchargeables
        - 📎 **Upload de Fichiers** - Analyse d'images, CSV, code
        - 🎨 **Thèmes Personnalisés** - Interface adaptée à vos préférences
        - 💾 **Historique Persistant** - Conversations sauvegardées
        """
    },
    "no_token_warning": """
        ## 🔐 Configuration Requise
        
        Pour utiliser cette application, configurez votre token Hugging Face.
        
        ### Comment obtenir votre token :
        1. **Créez un compte** sur [Hugging Face](https://huggingface.co/join)
        2. **Settings** → [Access Tokens](https://huggingface.co/settings/tokens)
        3. **Créez un nouveau token** (Read access)
        4. **Collez-le** dans la sidebar
    """,
    "usage_examples": """
        ## 📚 Exemples d'Utilisation
        
        ### ⚡ **Python**
        - "Analyse ces données : [1, 5, 10, 15, 20]"
        - "Crée un graphique des ventes mensuelles"
        - "Calcule l'écart-type de cette liste"
        
        ### 🚀 **Projets**
        - "Crée une calculatrice web moderne"
        - "Développe une todo-list responsive"
        - "Génère un site portfolio"
        
        ### 📊 **Fichiers**
        - "Analyse ce CSV uploadé"
        - "Résumé statistique de ces données"
        - "Génère un rapport sur ce dataset"
    """
}

# ==========================================
# 🔧 FONCTIONS UTILITAIRES
# ==========================================

def get_theme_selector():
    """Interface de sélection de thème"""
    if 'sidebar_rendered' not in st.session_state:
        st.session_state.sidebar_rendered = True
        
    st.subheader("🎨 Personnalisation")
    
    theme_names = list(THEMES.keys())
    theme_labels = {
        "default_light": "🌞 Défaut Clair",
        "default_dark": "🌙 Défaut Sombre", 
        "cyberpunk": "🔮 Cyberpunk",
        "nature": "🌿 Nature",
        "ocean": "🌊 Océan"
    }
    
    current_theme = st.selectbox(
        "Choisir un thème :",
        theme_names,
        format_func=lambda x: theme_labels.get(x, x),
        key="theme_selector"
    )
    
    return current_theme

def get_ai_config_panel():
    """Panel de configuration IA"""
    st.subheader("🤖 Configuration IA")
    
    # Température
    temperature = st.slider(
        "🌡️ Créativité",
        AI_CONFIG["temperature_range"]["min"],
        AI_CONFIG["temperature_range"]["max"],
        AI_CONFIG["temperature_range"]["default"],
        AI_CONFIG["temperature_range"]["step"],
        help="Contrôle la créativité (0 = précis, 2 = créatif)"
    )
    
    # Tokens
    max_tokens = st.slider(
        "📝 Tokens Maximum",
        AI_CONFIG["max_tokens_range"]["min"],
        AI_CONFIG["max_tokens_range"]["max"],
        AI_CONFIG["max_tokens_range"]["default"],
        AI_CONFIG["max_tokens_range"]["step"],
        help="Longueur maximale des réponses"
    )
    
    # Mémoire
    memory_length = st.slider(
        "🧠 Mémoire Conversation",
        1, 20, AI_CONFIG["conversation_memory"]["max_messages"],
        help="Messages gardés en contexte"
    )
    
    return {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "memory_length": memory_length
    }

# ==========================================
# 📊 ANALYTICS
# ==========================================

ANALYTICS_CONFIG = {
    "track_usage": True,
    "show_cost_breakdown": True,
    "export_analytics": True,
    "cost_per_1k_tokens": {
        "input": 0.00015,   # $0.15 per 1M tokens
        "output": 0.0006    # $0.60 per 1M tokens  
    }
}

def calculate_session_cost(input_tokens: int, output_tokens: int) -> dict:
    """Calcule le coût de la session"""
    input_cost = (input_tokens / 1000) * ANALYTICS_CONFIG["cost_per_1k_tokens"]["input"]
    output_cost = (output_tokens / 1000) * ANALYTICS_CONFIG["cost_per_1k_tokens"]["output"]
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }

def format_cost_display(cost_data: dict) -> str:
    """Formate l'affichage des coûts"""
    return f"""
    **💰 Coût Session :**
    - Input: ${cost_data['input_cost']:.4f} ({cost_data['input_tokens']} tokens)
    - Output: ${cost_data['output_cost']:.4f} ({cost_data['output_tokens']} tokens)
    - **Total: ${cost_data['total_cost']:.4f}**
    """

# ==========================================
# 🔍 VALIDATION ET SÉCURITÉ
# ==========================================

def validate_python_code(code: str) -> dict:
    """Valide le code Python avant exécution"""
    validation_result = {
        "is_safe": True,
        "warnings": [],
        "errors": [],
        "risk_level": "low"
    }
    
    # Vérification de la longueur
    if len(code) > SECURITY_CONFIG["python_execution"]["max_code_length"]:
        validation_result["is_safe"] = False
        validation_result["errors"].append(f"Code trop long (max {SECURITY_CONFIG['python_execution']['max_code_length']} caractères)")
        validation_result["risk_level"] = "high"
    
    # Vérification des patterns dangereux
    for pattern in SECURITY_CONFIG["python_execution"]["blocked_patterns"]:
        if re.search(pattern, code, re.IGNORECASE):
            validation_result["is_safe"] = False
            validation_result["errors"].append(f"Pattern dangereux: {pattern}")
            validation_result["risk_level"] = "high"
    
    # Vérification des fonctions bloquées
    for func in SECURITY_CONFIG["python_execution"]["blocked_functions"]:
        if func in code:
            validation_result["is_safe"] = False
            validation_result["errors"].append(f"Fonction interdite: {func}")
            validation_result["risk_level"] = "high"
    
    return validation_result

def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier"""
    # Supprime les caractères dangereux
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limite la longueur
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:95] + ext
    return sanitized

def validate_project_data(project_data: dict) -> dict:
    """Valide les données d'un projet"""
    validation = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Vérifications obligatoires
    required_fields = ["name", "files"]
    for field in required_fields:
        if field not in project_data:
            validation["is_valid"] = False
            validation["errors"].append(f"Champ obligatoire manquant: {field}")
    
    # Validation des fichiers
    if "files" in project_data:
        max_files = 20  # Limite par défaut
        if len(project_data["files"]) > max_files:
            validation["is_valid"] = False
            validation["errors"].append(f"Trop de fichiers (max {max_files})")
        
        for file_info in project_data["files"]:
            if not isinstance(file_info, dict):
                validation["warnings"].append("Structure de fichier invalide")
                continue
                
            if "name" not in file_info or "content" not in file_info:
                validation["warnings"].append("Fichier sans nom ou contenu")
                continue
                
            # Validation du nom
            if not re.match(r'^[a-zA-Z0-9._-]+$', file_info["name"]):
                validation["warnings"].append(f"Nom suspect: {file_info['name']}")
            
            # Vérification taille
            if len(file_info["content"]) > 100000:  # 100KB
                validation["warnings"].append(f"Fichier volumineux: {file_info['name']}")
    
    return validation

# ==========================================
# 🎨 PERSONNALISATION AVANCÉE
# ==========================================

CUSTOMIZATION_OPTIONS = {
    "interface": {
        "show_welcome_message": True,
        "show_usage_examples": True,
        "enable_animations": True,
        "compact_mode": False,
        "show_token_counter": True,
        "show_cost_tracker": True,
        "auto_scroll_chat": True
    },
    "behavior": {
        "auto_execute_python": True,
        "auto_create_projects": True,
        "save_conversation": True,
        "clear_on_restart": False,
        "confirm_dangerous_operations": True,
        "enable_debug_mode": False
    }
}

# ==========================================
# 🔧 EXPORT/IMPORT CONFIGURATION
# ==========================================

def export_config():
    """Exporte la configuration actuelle"""
    config_export = {
        "themes": THEMES,
        "ai_config": AI_CONFIG,
        "features": FEATURES_CONFIG,
        "security": SECURITY_CONFIG,
        "customization": CUSTOMIZATION_OPTIONS,
        "export_timestamp": datetime.datetime.now().isoformat(),
        "version": "4.0"
    }
    return json.dumps(config_export, indent=2, ensure_ascii=False)

def import_config(config_json: str):
    """Importe une configuration"""
    try:
        config = json.loads(config_json)
        
        # Validation de base
        required_keys = ["themes", "ai_config", "features", "security"]
        for key in required_keys:
            if key not in config:
                return {"success": False, "error": f"Clé manquante: {key}"}
        
        return {"success": True, "message": "Configuration importée"}
        
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON invalide: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur: {str(e)}"}

# ==========================================
# 🎊 CONFIGURATION ACTIVE
# ==========================================

# Configuration par défaut active
ACTIVE_THEME = "default_light"
ACTIVE_CONFIG = AI_CONFIG.copy()
ACTIVE_FEATURES = FEATURES_CONFIG.copy()

# Message de bienvenue
WELCOME_MESSAGE = """
## 🎯 OpenAI 120B Advanced - Configuration Active

### ✨ Fonctionnalités
- 🎨 **5 Thèmes** disponibles
- 🤖 **IA** optimisée  
- 🔒 **Sécurité** renforcée
- 📱 **Responsive** design

### 🚀 Prêt à Utiliser
Assistant configuré et optimisé. Commencez par une question !
"""

# Export des principales fonctions
__all__ = [
    'THEMES', 'AI_CONFIG', 'SYSTEM_PROMPTS', 'FEATURES_CONFIG', 'SECURITY_CONFIG',
    'generate_custom_css', 'get_theme_selector', 'get_ai_config_panel',
    'calculate_session_cost', 'validate_python_code', 'validate_project_data',
    'export_config', 'import_config', 'WELCOME_MESSAGE'
]