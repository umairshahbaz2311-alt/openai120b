"""
OpenAI 120B Advanced - Interface avec capacités de développement complètes
Version avec génération et exécution de code en temps réel
"""

import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import time
import json
import datetime
from pathlib import Path
import subprocess
import tempfile
import sys
import io
import contextlib
import traceback
import zipfile
import base64
import re

# Configuration de la page
st.set_page_config(
    page_title="OpenAI 120B Advanced",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Charger les variables d'environnement
load_dotenv()

# CSS amélioré avec support pour l'exécution de code
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1f4037, #99f2c8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .project-info {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
        display: inline-block;
    }
    .code-execution-area {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
    .file-tree {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
    .download-button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem;
        transition: all 0.3s;
    }
    .download-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .feature-badge {
            font-size: 0.7rem;
            padding: 0.3rem 0.8rem;
        }
        .main .block-container {
            padding: 1rem 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Fonctions utilitaires avancées
CONVERSATIONS_DIR = Path("conversations")
PROJECTS_DIR = Path("generated_projects")
CONVERSATIONS_DIR.mkdir(exist_ok=True)
PROJECTS_DIR.mkdir(exist_ok=True)
CREDITS_FILE = Path("credits_usage.json")

def load_credits_usage():
    if CREDITS_FILE.exists():
        try:
            with open(CREDITS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"total_tokens": 0, "total_requests": 0, "sessions": [], "projects_created": 0}

def save_credits_usage(credits_data):
    try:
        with open(CREDITS_FILE, 'w') as f:
            json.dump(credits_data, f, indent=2)
    except Exception as e:
        st.warning(f"Impossible de sauvegarder les stats: {e}")

def estimate_tokens(text):
    return int(len(text.split()) * 1.3)

def execute_python_code(code):
    """Exécute du code Python en toute sécurité"""
    try:
        # Nettoyer le code
        code = code.strip()
        if not code:
            return {"success": False, "output": "", "error": "Code vide"}
        
        # Capturer stdout et stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        captured_output = io.StringIO()
        captured_error = io.StringIO()
        
        sys.stdout = captured_output
        sys.stderr = captured_error
        
        # Créer un namespace sécurisé avec plus de modules
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'list': list,
                'dict': dict,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'sum': sum,
                'max': max,
                'min': min,
                'sorted': sorted,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'abs': abs,
                'round': round,
                'type': type,
                'isinstance': isinstance,
            }
        }
        
        # Ajouter des modules utiles
        try:
            safe_globals['math'] = __import__('math')
            safe_globals['datetime'] = __import__('datetime')
            safe_globals['json'] = __import__('json')
            safe_globals['random'] = __import__('random')
            safe_globals['time'] = __import__('time')
            safe_globals['re'] = __import__('re')
        except:
            pass
        
        # Essayer d'importer des modules de data science
        try:
            import matplotlib
            matplotlib.use('Agg')  # Backend non-interactif
            import matplotlib.pyplot as plt
            safe_globals['plt'] = plt
            safe_globals['matplotlib'] = matplotlib
        except:
            pass
            
        try:
            import numpy as np
            safe_globals['np'] = np
            safe_globals['numpy'] = np
        except:
            pass
            
        try:
            import pandas as pd
            safe_globals['pd'] = pd
            safe_globals['pandas'] = pd
        except:
            pass
        
        # Exécuter le code
        exec(code, safe_globals)
        
        # Restaurer stdout et stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        output = captured_output.getvalue()
        error = captured_error.getvalue()
        
        return {
            'success': True,
            'output': output,
            'error': error if error else None
        }
        
    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        return {
            'success': False,
            'output': '',
            'error': str(e) + '\n' + traceback.format_exc()
        }

def extract_code_blocks(text, language="python"):
    """Extrait les blocs de code d'un texte"""
    pattern = f"```{language}\\s*\\n(.*?)\\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def extract_json_from_text(text):
    """Extrait le JSON d'un texte"""
    try:
        # Chercher les blocs JSON
        json_pattern = r"```json\s*\n(.*?)\n```"
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match.strip())
            except:
                continue
        
        # Si pas de bloc ```json, chercher du JSON brut
        json_pattern = r'\{[^{}]*"files"[^{}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
                
        return None
    except:
        return None

def create_project_structure(project_data):
    """Crée la structure d'un projet complet"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project_data.get('name', 'project').replace(' ', '_').lower()
        project_name = re.sub(r'[^a-z0-9_]', '', project_name)
        project_path = PROJECTS_DIR / f"{project_name}_{timestamp}"
        project_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        for file_info in project_data.get('files', []):
            if isinstance(file_info, dict) and 'name' in file_info and 'content' in file_info:
                file_path = project_path / file_info['name']
                
                # Créer les dossiers nécessaires
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info['content'])
                
                created_files.append(str(file_path.relative_to(PROJECTS_DIR)))
        
        return project_path, created_files
    except Exception as e:
        st.error(f"Erreur création projet: {e}")
        return None, []

def create_download_zip(project_path):
    """Crée un zip téléchargeable du projet"""
    try:
        zip_path = project_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
        
        return zip_path
    except Exception as e:
        st.error(f"Erreur création ZIP: {e}")
        return None

def create_advanced_prompt(user_message, mode="standard"):
    """Crée un prompt avancé pour différents types de tâches"""
    
    if mode == "code_generation":
        system_prompt = """Tu es un développeur expert capable de créer des applications complètes et fonctionnelles.

CAPACITÉS:
🔧 Applications web (HTML/CSS/JS, React, Vue)
📱 Applications mobiles (concepts React Native, Flutter)
💻 Applications desktop (Electron, Python tkinter)
🌐 APIs et backends (Python Flask/FastAPI, Node.js)
📊 Outils d'analyse (Python data science)
🎮 Jeux web (JavaScript, Canvas)

FORMAT DE RÉPONSE pour projets:
```json
{
  "name": "nom_du_projet",
  "description": "Description complète",
  "type": "web/mobile/desktop/api/tool",
  "files": [
    {
      "name": "index.html",
      "content": "<!DOCTYPE html>...",
      "description": "Page principale"
    },
    {
      "name": "style.css", 
      "content": "body { margin: 0; }...",
      "description": "Styles CSS"
    }
  ],
  "installation": "Instructions détaillées",
  "usage": "Comment utiliser l'application"
}
```

RÈGLES:
- Toujours fournir du code complet et fonctionnel
- Inclure tous les fichiers nécessaires
- Ajouter des commentaires explicatifs
- Design moderne et responsive
- Optimisé pour mobile et desktop

Crée cette application:"""

    elif mode == "code_execution":
        system_prompt = """Tu es un expert Python capable d'écrire et d'exécuter du code pour résoudre des problèmes.

CAPACITÉS:
⚡ Calculs et algorithmes
📊 Visualisations (matplotlib, plotly si disponible)  
📈 Analyse de données (pandas, numpy si disponible)
🧮 Mathématiques et statistiques
🔍 Traitement de texte et regex
🎲 Simulations et modélisation

RÈGLES:
- Écris du code Python complet et exécutable
- Utilise print() pour afficher les résultats
- Ajoute des commentaires explicatifs
- Gère les erreurs potentielles
- Optimise pour la lisibilité

Résous ce problème avec du code Python:"""

    else:  # mode standard
        system_prompt = """Tu es un assistant IA très avancé avec des capacités complètes de développement.

🎯 CAPACITÉS PRINCIPALES:
🔧 Développement (web, mobile, desktop, APIs)
⚡ Exécution et test de code Python
💡 Résolution de problèmes complexes
📊 Analyse de données et visualisations
🎨 Design et interfaces utilisateur
📝 Rédaction et création de contenu
🚀 Innovation et brainstorming

STYLE DE RÉPONSE:
- Réponses détaillées et complètes
- Explications techniques claires
- Exemples pratiques
- Solutions immédiatement utilisables
- Adaptées au niveau de l'utilisateur

Réponds de manière complète et détaillée:"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

# Vérification du token
if not os.environ.get("HF_TOKEN"):
    st.error("❌ Token HF_TOKEN non configuré. Créez un fichier .env avec votre token Hugging Face")
    st.info("Format du fichier .env:\n```\nHF_TOKEN=votre_token_ici\n```")
    st.stop()

# Initialisation du client
@st.cache_resource
def init_client():
    return OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )

try:
    client = init_client()
    st.success("✅ Système avancé initialisé avec succès", icon="🚀")
except Exception as e:
    st.error(f"❌ Erreur d'initialisation: {e}")
    st.stop()

# Charger les données
credits_data = load_credits_usage()

# En-tête avancé
st.markdown('<h1 class="main-header">🧠 OpenAI 120B Advanced</h1>', unsafe_allow_html=True)
st.markdown('<p class="project-info">Assistant IA avec capacités de développement complètes</p>', unsafe_allow_html=True)

# Badges de fonctionnalités
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <span class="feature-badge">🔥 Génération de Code</span>
    <span class="feature-badge">⚡ Exécution Python</span>
    <span class="feature-badge">📱 Apps Mobile</span>
    <span class="feature-badge">🌐 Apps Web</span>
    <span class="feature-badge">💻 Apps Desktop</span>
    <span class="feature-badge">📊 Visualisations</span>
    <span class="feature-badge">🎨 Interface Design</span>
    <span class="feature-badge">🚀 Projets Complets</span>
</div>
""", unsafe_allow_html=True)

# Initialisation des variables
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_tokens = 0
    st.session_state.session_requests = 0
    st.session_state.projects_created = 0
    st.session_state.code_executions = 0

# Sidebar avancée
with st.sidebar:
    st.header("🎛️ Centre de Contrôle Advanced")
    
    # Mode de fonctionnement
    st.subheader("🚀 Mode de Travail")
    work_mode = st.selectbox(
        "Choisissez le mode:",
        ["💬 Chat Standard", "🔧 Génération de Code", "⚡ Exécution Python", "🎨 Création d'Apps"],
        help="Sélectionnez le mode adapté à votre tâche"
    )
    
    # Statistiques avancées
    st.subheader("📊 Statistiques")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎯 Tokens Session", f"{st.session_state.session_tokens:,}")
        st.metric("📊 Requêtes", st.session_state.session_requests)
        if st.session_state.projects_created > 0:
            st.metric("🚀 Projets", st.session_state.projects_created)
    
    with col2:
        st.metric("🏆 Total Tokens", f"{credits_data['total_tokens']:,}")
        st.metric("💰 Coût Session", f"${st.session_state.session_tokens * 0.00075:.4f}")
        if st.session_state.code_executions > 0:
            st.metric("⚡ Codes Exec", st.session_state.code_executions)
    
    # Paramètres IA
    st.subheader("🤖 Paramètres IA")
    temperature = st.slider("🌡️ Créativité", 0.1, 2.0, 0.8, 0.1, help="Plus élevé = plus créatif")
    max_tokens = st.slider("📝 Longueur Max", 1000, 4000, 2500, 250, help="Tokens maximum par réponse")
    
    # Options avancées
    st.subheader("🔬 Options Avancées")
    auto_execute = st.checkbox("⚡ Auto-exec Python", value=False, help="Exécuter automatiquement le code Python généré")
    create_projects = st.checkbox("📁 Auto-create Projects", value=True, help="Créer automatiquement les structures de projet")
    show_metrics = st.checkbox("📊 Afficher Métriques", value=True, help="Afficher les métriques détaillées")
    
    st.markdown("---")
    
    # Actions rapides
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Reset", type="secondary", use_container_width=True):
            # Sauvegarder les stats avant reset
            if st.session_state.session_tokens > 0:
                credits_data['sessions'].append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "tokens": st.session_state.session_tokens,
                    "requests": st.session_state.session_requests,
                    "projects": st.session_state.projects_created,
                    "executions": st.session_state.code_executions
                })
                save_credits_usage(credits_data)
            
            st.session_state.messages = []
            st.session_state.session_tokens = 0
            st.session_state.session_requests = 0
            st.session_state.projects_created = 0
            st.session_state.code_executions = 0
            st.rerun()
    
    with col2:
        if st.button("📊 Stats", use_container_width=True):
            st.session_state.show_detailed_stats = not st.session_state.get('show_detailed_stats', False)
    
    # Stats détaillées
    if st.session_state.get('show_detailed_stats', False):
        st.subheader("📈 Stats Détaillées")
        if credits_data.get('sessions'):
            recent_sessions = credits_data['sessions'][-5:]
            for i, session in enumerate(reversed(recent_sessions)):
                st.text(f"Session {len(recent_sessions)-i}: {session.get('tokens', 0):,} tokens")
    
    # Projets créés
    if PROJECTS_DIR.exists():
        projects = [p for p in PROJECTS_DIR.iterdir() if p.is_dir()]
        if projects:
            st.subheader("📂 Projets Récents")
            for project in sorted(projects, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                project_name = project.name[:20] + "..." if len(project.name) > 23 else project.name
                st.text(f"📁 {project_name}")
                
                if st.button(f"📥 ZIP", key=f"dl_{project.name}", help="Télécharger le projet"):
                    zip_path = create_download_zip(project)
                    if zip_path and zip_path.exists():
                        with open(zip_path, 'rb') as f:
                            st.download_button(
                                "💾 Télécharger",
                                f.read(),
                                file_name=f"{project.name}.zip",
                                mime="application/zip",
                                key=f"download_{project.name}"
                            )

# Zone principale
st.markdown("### 💬 Assistant IA Advanced")

# Afficher les messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Afficher les résultats d'exécution
        if "execution_result" in message:
            result = message["execution_result"]
            
            with st.expander("⚡ Résultat d'Exécution", expanded=True):
                if result["success"]:
                    if result["output"]:
                        st.success("✅ Exécution réussie")
                        st.code(result["output"], language="text")
                    if result.get("error"):
                        st.warning(f"⚠️ Warnings: {result['error']}")
                else:
                    st.error("❌ Erreur d'exécution")
                    st.code(result["error"], language="text")
        
        # Afficher les projets créés
        if "project_created" in message:
            project_info = message["project_created"]
            
            with st.expander("🚀 Projet Créé", expanded=True):
                st.success(f"✅ **{project_info['name']}** créé avec succès!")
                st.markdown(f"**Description:** {project_info['description']}")
                
                if project_info['files']:
                    st.markdown("**📁 Fichiers créés:**")
                    for file_path in project_info['files']:
                        st.text(f"📄 {file_path}")

# Input utilisateur avec placeholders adaptatifs
placeholder_map = {
    "🔧 Génération de Code": "Décrivez l'application à créer (ex: 'Crée une calculatrice web moderne')",
    "⚡ Exécution Python": "Décrivez le code à exécuter (ex: 'Crée un graphique des ventes')",
    "🎨 Création d'Apps": "Décrivez votre idée d'app (ex: 'App de gestion de tâches')",
    "💬 Chat Standard": "Posez votre question ou décrivez ce que vous voulez..."
}

if prompt := st.chat_input(placeholder_map.get(work_mode, "Votre message...")):
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Générer la réponse selon le mode
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner(f"🧠 {work_mode.split()[-1]} en cours..."):
                start_time = time.time()
                
                # Choisir le type de prompt selon le mode
                mode_map = {
                    "🔧 Génération de Code": "code_generation",
                    "⚡ Exécution Python": "code_execution",
                    "🎨 Création d'Apps": "code_generation",
                    "💬 Chat Standard": "standard"
                }
                
                api_messages = create_advanced_prompt(prompt, mode_map.get(work_mode, "standard"))
                
                # Ajouter l'historique récent (limité pour éviter les tokens excess)
                if len(st.session_state.messages) > 1:
                    recent_history = st.session_state.messages[-4:]  # 4 derniers messages
                    for msg in recent_history[:-1]:  # Exclure le message actuel
                        if len(msg["content"]) < 2000:  # Limiter la taille
                            api_messages.append({
                                "role": msg["role"], 
                                "content": msg["content"][:1500] + "..." if len(msg["content"]) > 1500 else msg["content"]
                            })
                
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-120b:together",
                    messages=api_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                response = completion.choices[0].message.content
                response_time = round(time.time() - start_time, 2)
                
                # Afficher la réponse
                message_placeholder.markdown(response)
                
                # Préparer les données du message
                message_data = {"role": "assistant", "content": response}
                
                # Post-traitement selon le mode
                
                # 1. Exécution automatique de code Python
                if (work_mode == "⚡ Exécution Python" or auto_execute) and "```python" in response:
                    st.markdown("---")
                    st.markdown("### ⚡ Exécution du Code")
                    
                    code_blocks = extract_code_blocks(response, "python")
                    
                    if code_blocks:
                        for i, code in enumerate(code_blocks):
                            with st.expander(f"🔥 Code {i+1}", expanded=True):
                                st.code(code, language="python")
                                
                                result = execute_python_code(code)
                                message_data["execution_result"] = result
                                
                                if result["success"]:
                                    if result["output"]:
                                        st.success("✅ Exécution réussie")
                                        st.code(result["output"], language="text")
                                    if result.get("error"):
                                        st.warning(f"⚠️ Warnings: {result['error']}")
                                else:
                                    st.error("❌ Erreur d'exécution")
                                    st.code(result["error"], language="text")
                        
                        st.session_state.code_executions += 1
                
                # 2. Création automatique de projets
                if create_projects and work_mode in ["🔧 Génération de Code", "🎨 Création d'Apps"]:
                    project_data = extract_json_from_text(response)
                    
                    if project_data and "files" in project_data:
                        st.markdown("---")
                        st.markdown("### 🚀 Création du Projet")
                        
                        project_path, created_files = create_project_structure(project_data)
                        
                        if project_path and created_files:
                            message_data["project_created"] = {
                                "name": project_data.get("name", "Projet"),
                                "description": project_data.get("description", ""),
                                "files": created_files,
                                "path": str(project_path.relative_to(PROJECTS_DIR))
                            }
                            
                            st.success(f"✅ Projet **{project_data.get('name')}** créé!")
                            
                            # Afficher la structure
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**📁 Fichiers créés:**")
                                for file_path in created_files:
                                    st.text(f"📄 {file_path}")
                            
                            with col2:
                                # Créer et proposer le téléchargement
                                zip_path = create_download_zip(project_path)
                                if zip_path and zip_path.exists():
                                    with open(zip_path, 'rb') as f:
                                        st.download_button(
                                            "📥 Télécharger Projet",
                                            f.read(),
                                            file_name=f"{project_data.get('name', 'project')}.zip",
                                            mime="application/zip"
                                        )
                            
                            st.session_state.projects_created += 1
                            credits_data['projects_created'] = credits_data.get('projects_created', 0) + 1
                
                # Afficher les métriques
                if show_metrics:
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.caption(f"⏱️ {response_time}s")
                    with col2:
                        output_tokens = estimate_tokens(response)
                        st.caption(f"📝 {output_tokens} tokens")
                    with col3:
                        input_tokens = sum(estimate_tokens(m["content"]) for m in api_messages)
                        total_tokens = input_tokens + output_tokens
                        st.caption(f"💰 ${total_tokens * 0.00075:.4f}")
                    with col4:
                        st.caption(f"🎯 {work_mode.split()[-1]}")
                
                # Mettre à jour les compteurs
                st.session_state.session_tokens += total_tokens
                st.session_state.session_requests += 1
                
                # Sauvegarder les stats
                credits_data['total_tokens'] += total_tokens
                credits_data['total_requests'] += 1
                save_credits_usage(credits_data)
                
        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            message_placeholder.error(error_msg)
            message_data = {"role": "assistant", "content": error_msg}
    
    # Ajouter le message à l'historique
    st.session_state.messages.append(message_data)

# Guide d'utilisation si pas de messages
if not st.session_state.messages:
    st.markdown("""
    ### 🎯 Guide OpenAI 120B Advanced
    
    #### 🔧 **Génération de Code** 
    - *"Crée une calculatrice web avec design moderne"*
    - *"Développe une API REST pour gestion d'utilisateurs"*
    - *"Génère une app React de todo-list avec localStorage"*
    - *"Crée un jeu Snake en JavaScript avec Canvas"*
    
    #### ⚡ **Exécution Python**  
    - *"Crée un graphique des ventes par mois"*
    - *"Analyse ce dataset et montre les tendances"*
    - *"Développe un algorithme de tri et benchmarke-le"*
    - *"Simule un lancer de dés 1000 fois et affiche les stats"*
    
    #### 🎨 **Création d'Apps**
    - *"Design une app mobile de fitness avec tracker"*
    - *"Crée un dashboard admin avec charts et tables"*
    - *"Développe un portfolio personnel responsive"*
    - *"Génère un e-commerce avec panier et paiement"*
    
    #### 💬 **Chat Standard**
    - Questions générales et conseils
    - Debugging et optimisation de code
    - Brainstorming et innovation
    - Explications techniques détaillées
    
    ### 🚀 **Fonctionnalités Avancées:**
    - ✅ **Génération complète** d'applications fonctionnelles
    - ✅ **Exécution temps réel** de code Python  
    - ✅ **Téléchargement automatique** des projets créés
    - ✅ **Support multi-langages** (Python, JS, HTML, CSS, React...)
    - ✅ **Visualisations** et analyses de données
    - ✅ **Mobile-responsive** et optimisé tous écrans
    
    **🎯 Commencez par sélectionner un mode dans la sidebar et posez votre question !**
    """)

# Footer avancé
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**🧠 OpenAI 120B**")
    st.caption("Assistant IA Avancé")

with col2:
    st.markdown("**💻 Développement**") 
    st.caption("Apps complètes")

with col3:
    st.markdown("**⚡ Exécution**")
    st.caption("Code temps réel")

with col4:
    st.markdown("**📊 Analytics**")
    st.caption("Stats détaillées")

st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8rem; margin-top: 1rem;'>"
    f"💡 Version 3.0 Advanced | {credits_data['total_tokens']:,} tokens utilisés | "
    f"{credits_data.get('projects_created', 0)} projets créés"
    "</div>", 
    unsafe_allow_html=True
)