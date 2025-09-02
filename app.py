"""
OpenAI 120B Advanced - Version Simplifiée et Optimisée
Interface complète avec génération de code, exécution Python et projets
"""

import os
import streamlit as st
from openai import OpenAI
import time
import json
import datetime
from pathlib import Path
import sys
import io
import traceback
import zipfile
import re
import requests
import pandas as pd
from PIL import Image
import hashlib
from contextlib import redirect_stdout, redirect_stderr
from functools import lru_cache
from typing import Dict, List, Optional, Any
import uuid

# Configuration sécurisée
SECURITY_CONFIG = {
    "max_execution_time": 10,
    "max_memory_mb": 100,
    "allowed_modules": {'math', 'datetime', 'json', 'random', 'time', 're', 'statistics', 'numpy', 'pandas'},
    "blocked_functions": {'exec', 'eval', 'open', '__import__', 'compile', 'memoryview'},
    "max_file_size_mb": 10,
    "max_project_files": 20
}

# Configuration de la page
st.set_page_config(
    page_title="OpenAI 120B Advanced",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Répertoires
BASE_DIR = Path(".")
CONVERSATIONS_DIR = BASE_DIR / "conversations" 
GENERATED_PROJECTS_DIR = BASE_DIR / "generated_projects"
UPLOADS_DIR = BASE_DIR / "uploads"

# Créer les répertoires
for directory in [CONVERSATIONS_DIR, GENERATED_PROJECTS_DIR, UPLOADS_DIR]:
    directory.mkdir(exist_ok=True)

# Fichiers de données
CHAT_HISTORY_FILE = BASE_DIR / "chat_history.json"
CREDITS_USAGE_FILE = BASE_DIR / "credits_usage.json"

# Initialisation des états de session
def init_session_state():
    defaults = {
        'dark_mode': False,
        'messages': [],
        'session_tokens': 0,
        'session_requests': 0,
        'projects_created': 0,
        'code_executions': 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# CSS optimisé
@st.cache_data
def get_optimized_css(dark_mode: bool) -> str:
    base_styles = """
    <style>
    .stApp { 
        transition: all 0.3s ease;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main-header {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 800;
        text-align: center;
        margin: 1rem 0 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .usage-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        color: white;
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.2rem;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #667eea;
    }
    .code-result {
        background: #f6f8fa;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Fira Code', monospace;
    }
    """
    
    if dark_mode:
        return base_styles + """
        .stApp { 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #e0e6ed;
        }
        .metric-card {
            background: #16213e;
            color: #e0e6ed;
            border-left-color: #667eea;
        }
        .code-result {
            background: #0d1117;
            border-color: #30363d;
            color: #e6edf3;
        }
        """
    else:
        return base_styles

st.markdown(get_optimized_css(st.session_state.dark_mode), unsafe_allow_html=True)

# Utilitaires
@lru_cache(maxsize=256)
def estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))

def secure_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()[:16]

# Gestionnaire de fichiers
def load_json_file(filepath: Path, default=None):
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erreur lecture {filepath}: {e}")
    return default or {}

def save_json_file(filepath: Path, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Erreur sauvegarde {filepath}: {e}")

# Chargement des données
def load_chat_history():
    return load_json_file(CHAT_HISTORY_FILE, [])

def save_chat_history():
    save_json_file(CHAT_HISTORY_FILE, st.session_state.messages)

def load_credits_usage():
    return load_json_file(CREDITS_USAGE_FILE, {
        "total_tokens": 0,
        "total_requests": 0,
        "sessions": [],
        "projects_created": 0
    })

def save_credits_usage(data):
    save_json_file(CREDITS_USAGE_FILE, data)

# Exécuteur de code sécurisé
class SecureCodeExecutor:
    def __init__(self):
        self.safe_builtins = {
            'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
            'float', 'int', 'len', 'list', 'map', 'max', 'min', 'print',
            'range', 'round', 'sorted', 'str', 'sum', 'type', 'zip',
            'set', 'tuple', 'reversed', 'chr', 'ord'
        }
    
    def execute(self, code: str) -> Dict[str, Any]:
        if not code.strip():
            return {"success": False, "output": "", "error": "Code vide"}
        
        # Vérifications sécuritaires
        dangerous_patterns = [
            r'\b(exec|eval|compile|__import__)\s*\(',
            r'\bopen\s*\(',
            r'\bfile\s*\(',
            r'subprocess',
            r'os\.(system|popen|remove)',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return {"success": False, "output": "", "error": f"Code dangereux détecté: {pattern}"}
        
        if len(code) > 10000:
            return {"success": False, "output": "", "error": "Code trop long (max 10000 caractères)"}
        
        try:
            # Environnement sécurisé
            safe_globals = {
                '__builtins__': {name: getattr(__builtins__, name) 
                               for name in self.safe_builtins if hasattr(__builtins__, name)}
            }
            
            # Modules autorisés
            for module in SECURITY_CONFIG['allowed_modules']:
                try:
                    safe_globals[module] = __import__(module)
                    if module == 'numpy':
                        safe_globals['np'] = safe_globals[module]
                    elif module == 'pandas':
                        safe_globals['pd'] = safe_globals[module]
                except ImportError:
                    continue
            
            # Redirection des sorties
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    exec(code, safe_globals)
                
                output = output_buffer.getvalue()
                error = error_buffer.getvalue()
                
                return {
                    'success': True,
                    'output': output,
                    'error': error if error else None
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Erreur d'exécution: {str(e)}"
                }
                
        except Exception as e:
            return {"success": False, "output": "", "error": f"Erreur système: {str(e)}"}

# Gestionnaire de projets
def create_project_structure(project_data: Dict) -> tuple:
    """Crée la structure d'un projet"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project_data.get('name', 'project').replace(' ', '_').lower()
        project_name = re.sub(r'[^a-z0-9_]', '', project_name)
        
        project_path = GENERATED_PROJECTS_DIR / f"{project_name}_{timestamp}"
        project_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        files = project_data.get('files', [])
        
        for file_info in files:
            if isinstance(file_info, dict) and 'name' in file_info and 'content' in file_info:
                file_path = project_path / file_info['name']
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info['content'])
                
                created_files.append(str(file_path.relative_to(GENERATED_PROJECTS_DIR)))
        
        return project_path, created_files
        
    except Exception as e:
        st.error(f"Erreur création projet: {e}")
        return None, []

def create_download_zip(project_path: Path) -> Optional[Path]:
    """Crée un ZIP téléchargeable"""
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

# Gestionnaire de fichiers uploadés
def handle_file_upload(uploaded_file) -> Optional[str]:
    """Traite un fichier uploadé"""
    if not uploaded_file:
        return None
    
    # Vérification taille
    if uploaded_file.size > SECURITY_CONFIG['max_file_size_mb'] * 1024 * 1024:
        st.error(f"Fichier trop volumineux (max {SECURITY_CONFIG['max_file_size_mb']}MB)")
        return None
    
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_ext in ['txt', 'py', 'js', 'html', 'css', 'md']:
            content = uploaded_file.getvalue().decode('utf-8')
            with st.expander(f"📄 {uploaded_file.name}", expanded=False):
                st.code(content[:2000] + ("..." if len(content) > 2000 else ""), language=file_ext)
            return f"Fichier texte '{uploaded_file.name}' analysé ({len(content)} caractères)."
            
        elif file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            image = Image.open(uploaded_file)
            st.image(image, caption=uploaded_file.name, width=400)
            return f"Image '{uploaded_file.name}' affichée ({image.size[0]}x{image.size[1]}px)."
            
        elif file_ext == 'csv':
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(100))
            return f"CSV '{uploaded_file.name}': {len(df)} lignes, {len(df.columns)} colonnes."
            
        else:
            st.info(f"Type de fichier '{file_ext}' non supporté pour prévisualisation")
            return f"Fichier '{uploaded_file.name}' uploadé."
            
    except Exception as e:
        st.error(f"Erreur traitement fichier: {e}")
        return None

# Client OpenAI
@st.cache_resource
def init_openai_client(token: str) -> OpenAI:
    return OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=token,
        timeout=30.0
    )

# Prompts système simplifiés
def get_system_prompt(mode: str) -> str:
    prompts = {
        "💬 Chat": "Tu es un assistant IA avancé, serviable et précis. Réponds de manière claire et détaillée en français.",
        
        "🔧 Code": """Tu es un expert développeur. Génère du code complet et fonctionnel.

Pour créer des projets, utilise ce format JSON:
```json
{
  "name": "nom_du_projet",
  "description": "Description détaillée",
  "type": "web|desktop|mobile|api",
  "files": [
    {
      "name": "index.html",
      "content": "<!DOCTYPE html>...",
      "description": "Fichier principal"
    }
  ],
  "installation": "Instructions d'installation",
  "usage": "Instructions d'utilisation"
}
```

Règles:
- Code complet et commenté
- Sécurité et bonnes pratiques
- Design moderne et responsive""",
        
        "⚡ Python": """Tu es un expert Python. Écris du code exécutable et sûr.

Modules disponibles: math, datetime, json, random, time, re, statistics, numpy, pandas.
Utilise print() pour afficher les résultats.
Évite les opérations dangereuses ou non autorisées.

Format:
1. Explication du problème
2. Code Python complet et commenté
3. Exemple d'utilisation si pertinent"""
    }
    return prompts.get(mode, prompts["💬 Chat"])

# Extraction des données
def extract_json_from_response(response: str) -> Optional[Dict]:
    """Extrait JSON de la réponse"""
    try:
        json_pattern = r'```json\s*\n(.*?)\n```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
        
        return None
    except:
        return None

def extract_code_blocks(response: str, language: str = "python") -> List[str]:
    """Extrait les blocs de code"""
    pattern = f"```{language}\\s*\\n(.*?)\\n```"
    return re.findall(pattern, response, re.DOTALL)

# Interface principale
def main():
    # Header
    st.markdown('<h1 class="main-header">🧠 OpenAI 120B Advanced</h1>', 
                unsafe_allow_html=True)
    
    # Badges de fonctionnalités
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <span class="feature-badge">🔥 Code Generation</span>
        <span class="feature-badge">⚡ Python Exec</span>
        <span class="feature-badge">📎 File Upload</span>
        <span class="feature-badge">🌓 Dark Mode</span>
        <span class="feature-badge">💾 Persistent Chat</span>
        <span class="feature-badge">🔒 Secure Sandbox</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Centre de Contrôle")
        
        # Toggle thème
        if st.button("🌓 Basculer Thème", key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        theme_status = "🌙 Mode Sombre" if st.session_state.dark_mode else "☀️ Mode Clair"
        st.caption(f"Thème actuel: {theme_status}")
        
        st.markdown("---")
        
        # Configuration token
        st.subheader("🔐 Configuration")
        user_token = st.text_input(
            "Token Hugging Face",
            type="password",
            placeholder="hf_...",
            help="Votre token HF pour accéder à l'API",
            key="hf_token_input"
        )
        
        if not user_token or not user_token.startswith("hf_"):
            st.warning("⚠️ Token HF requis (format: hf_...)")
            st.markdown("""
            **Comment obtenir votre token:**
            1. [Créer un compte HF](https://huggingface.co/join)
            2. Aller dans [Settings > Access Tokens](https://huggingface.co/settings/tokens)
            3. Créer un nouveau token (Read access)
            4. Copier et coller ici
            """)
            st.stop()
        
        st.success("✅ Token détecté")
        
        # Paramètres IA
        st.subheader("🤖 Paramètres IA")
        work_mode = st.selectbox(
            "Mode de travail:",
            ["💬 Chat", "🔧 Code", "⚡ Python"],
            key="work_mode"
        )
        
        temperature = st.slider("🌡️ Créativité", 0.1, 1.5, 0.7, 0.1)
        max_tokens = st.slider("📝 Tokens Max", 500, 4000, 2000, 250)
        
        # Options
        st.subheader("⚙️ Options")
        auto_execute = st.checkbox("⚡ Auto-exécution Python", value=True)
        auto_projects = st.checkbox("📁 Auto-création projets", value=True)
        
        # Upload de fichiers
        st.subheader("📎 Upload Fichiers")
        uploaded_file = st.file_uploader(
            "Choisir un fichier",
            type=['txt', 'py', 'js', 'html', 'css', 'md', 'csv', 'jpg', 'jpeg', 'png', 'pdf'],
            help="Fichiers supportés: texte, code, images, CSV"
        )
        
        # Statistiques de session
        st.subheader("📊 Session")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", len(st.session_state.messages))
            st.metric("Tokens", st.session_state.session_tokens)
        with col2:
            st.metric("Requêtes", st.session_state.session_requests)
            st.metric("Projets", st.session_state.projects_created)
        
        # Actions
        st.subheader("🛠️ Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Reset Chat", type="secondary"):
                st.session_state.messages = []
                save_chat_history()
                st.success("Chat réinitialisé!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("💾 Export") and st.session_state.messages:
                export_data = {
                    "messages": st.session_state.messages,
                    "metadata": {
                        "export_date": datetime.datetime.now().isoformat(),
                        "total_messages": len(st.session_state.messages),
                        "session_tokens": st.session_state.session_tokens
                    }
                }
                
                st.download_button(
                    "📥 Télécharger Chat",
                    json.dumps(export_data, indent=2, ensure_ascii=False),
                    file_name=f"chat_export_{int(time.time())}.json",
                    mime="application/json"
                )
    
    # Initialisation du client OpenAI
    try:
        client = init_openai_client(user_token)
        st.success("✅ Client OpenAI initialisé")
    except Exception as e:
        st.error(f"❌ Erreur client: {e}")
        st.stop()
    
    # Chargement de l'historique
    if not st.session_state.messages:
        st.session_state.messages = load_chat_history()
    
    # Gestionneurs
    executor = SecureCodeExecutor()
    
    # Zone de chat
    st.markdown("### 💬 Chat avec Historique Persistant")
    
    # Affichage des messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Résultats d'exécution Python
            if "execution_result" in message:
                result = message["execution_result"]
                with st.expander("⚡ Résultat d'Exécution Python", expanded=True):
                    if result["success"]:
                        if result["output"]:
                            st.success("✅ Exécution réussie")
                            st.code(result["output"], language="text")
                        else:
                            st.info("✅ Code exécuté sans sortie")
                        if result.get("error"):
                            st.warning(f"⚠️ Avertissements: {result['error']}")
                    else:
                        st.error("❌ Erreur d'exécution")
                        st.code(result["error"], language="text")
            
            # Projets créés
            if "project_created" in message:
                project_info = message["project_created"]
                with st.expander("🚀 Projet Créé", expanded=True):
                    st.success(f"✅ **{project_info['name']}** créé!")
                    st.markdown(f"**Description:** {project_info['description']}")
                    
                    if project_info.get('files'):
                        st.markdown("**📁 Fichiers créés:**")
                        for file_path in project_info['files']:
                            st.text(f"📄 {file_path}")
    
    # Traitement du fichier uploadé
    file_context = ""
    if uploaded_file:
        with st.spinner("Traitement du fichier..."):
            file_context = handle_file_upload(uploaded_file) or ""
    
    # Zone de saisie
    placeholder_texts = {
        "💬 Chat": "Posez votre question...",
        "🔧 Code": "Décrivez l'application à créer...",
        "⚡ Python": "Décrivez le calcul à effectuer..."
    }
    
    if prompt := st.chat_input(placeholder_texts.get(work_mode, "Votre message...")):
        # Ajouter contexte du fichier si présent
        full_prompt = f"{prompt}\n\n[Contexte fichier: {file_context}]" if file_context else prompt
        
        # Message utilisateur
        st.session_state.messages.append({"role": "user", "content": full_prompt})
        save_chat_history()
        
        with st.chat_message("user"):
            st.markdown(full_prompt)
        
        # Génération de la réponse
        with st.chat_message("assistant"):
            try:
                # Préparation des messages pour l'API
                system_prompt = get_system_prompt(work_mode)
                api_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
                
                # Ajout de l'historique récent (limité)
                recent_messages = st.session_state.messages[-6:]
                for msg in recent_messages[:-1]:
                    if len(msg["content"]) < 1500:
                        api_messages.append({
                            "role": msg["role"],
                            "content": msg["content"][:1000] + ("..." if len(msg["content"]) > 1000 else "")
                        })
                
                # Appel API avec retry
                response = None
                with st.spinner("Génération de la réponse..."):
                    for attempt in range(3):
                        try:
                            completion = client.chat.completions.create(
                                model="openai/gpt-oss-120b:together",
                                messages=api_messages,
                                max_tokens=max_tokens,
                                temperature=temperature,
                            )
                            response = completion.choices[0].message.content
                            break
                        except Exception as e:
                            if attempt == 2:
                                raise e
                            time.sleep(1)
                
                if not response:
                    response = "❌ Erreur: Impossible de générer une réponse"
                
                # Affichage de la réponse
                st.markdown(response)
                
                # Préparation des données du message
                message_data = {"role": "assistant", "content": response}
                
                # Post-traitement selon le mode
                if work_mode == "⚡ Python" or auto_execute:
                    # Exécution automatique du code Python
                    python_blocks = extract_code_blocks(response, "python")
                    if python_blocks:
                        st.markdown("---")
                        st.markdown("### ⚡ Exécution Automatique du Code")
                        
                        for i, code_block in enumerate(python_blocks):
                            with st.expander(f"🐍 Code Python {i+1}", expanded=True):
                                st.code(code_block, language="python")
                                
                                with st.spinner("Exécution en cours..."):
                                    result = executor.execute(code_block)
                                
                                message_data["execution_result"] = result
                                
                                if result["success"]:
                                    if result["output"]:
                                        st.success("✅ Exécution réussie")
                                        st.code(result["output"], language="text")
                                    else:
                                        st.info("✅ Code exécuté sans sortie")
                                    if result.get("error"):
                                        st.warning(f"⚠️ Avertissements: {result['error']}")
                                else:
                                    st.error("❌ Erreur d'exécution")
                                    st.code(result["error"], language="text")
                        
                        st.session_state.code_executions += 1
                
                elif work_mode == "🔧 Code" or auto_projects:
                    # Création automatique de projets
                    project_data = extract_json_from_response(response)
                    if project_data and project_data.get('files'):
                        st.markdown("---")
                        st.markdown("### 🚀 Création du Projet")
                        
                        with st.spinner("Création du projet..."):
                            project_path, created_files = create_project_structure(project_data)
                        
                        if project_path and created_files:
                            message_data["project_created"] = {
                                "name": project_data.get("name", "Projet Sans Nom"),
                                "description": project_data.get("description", ""),
                                "files": created_files,
                                "path": str(project_path.relative_to(GENERATED_PROJECTS_DIR))
                            }
                            
                            st.success(f"✅ Projet **{project_data.get('name')}** créé!")
                            
                            # Affichage des fichiers
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**📁 Fichiers créés:**")
                                for file_path in created_files:
                                    st.text(f"📄 {file_path}")
                            
                            with col2:
                                # Bouton de téléchargement
                                zip_path = create_download_zip(project_path)
                                if zip_path and zip_path.exists():
                                    with open(zip_path, 'rb') as f:
                                        st.download_button(
                                            "📥 Télécharger Projet (ZIP)",
                                            f.read(),
                                            file_name=f"{project_data.get('name', 'project')}.zip",
                                            mime="application/zip"
                                        )
                            
                            st.session_state.projects_created += 1
                
                # Calcul des tokens et coût
                tokens_used = estimate_tokens(response)
                input_tokens = sum(estimate_tokens(msg["content"]) for msg in api_messages)
                total_tokens = tokens_used + input_tokens
                cost_estimate = total_tokens * 0.00075 / 1000  # Estimation du coût
                
                # Métriques en bas
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.caption(f"📝 {tokens_used} tokens sortie")
                with col2:
                    st.caption(f"📊 {total_tokens} tokens total")
                with col3:
                    st.caption(f"💰 ~${cost_estimate:.4f}")
                with col4:
                    st.caption(f"🎯 {work_mode}")
                
                # Mise à jour des compteurs de session
                st.session_state.session_tokens += total_tokens
                st.session_state.session_requests += 1
                
                # Sauvegarde des statistiques
                credits_data = load_credits_usage()
                credits_data['total_tokens'] = credits_data.get('total_tokens', 0) + total_tokens
                credits_data['total_requests'] = credits_data.get('total_requests', 0) + 1
                save_credits_usage(credits_data)
                
            except Exception as e:
                error_msg = f"❌ Erreur: {str(e)}"
                st.error(error_msg)
                message_data = {"role": "assistant", "content": error_msg}
        
        # Sauvegarde du message
        st.session_state.messages.append(message_data)
        save_chat_history()
    
    # Guide d'utilisation si aucun message
    if not st.session_state.messages:
        st.markdown("""
        ## 🎯 Guide d'Utilisation OpenAI 120B Advanced
        
        ### 🆕 **Fonctionnalités Disponibles**
        - ⚡ **Exécution Python Sécurisée** - Code exécuté dans un sandbox
        - 🚀 **Génération de Projets** - Applications complètes téléchargeables
        - 💾 **Chat Persistant** - Historique sauvegardé automatiquement
        - 📎 **Upload Fichiers** - Support images, CSV, code
        - 🌓 **Mode Sombre/Clair** - Interface adaptable
        - 🔒 **Sécurité Renforcée** - Validation stricte du code
        
        ### ⚡ **Exemples Python**
        - *"Analyse ce fichier CSV uploadé"*
        - *"Crée un graphique des données de vente"*
        - *"Calcule les statistiques de ce dataset: [1,2,3,4,5]"*
        - *"Génère 10 nombres aléatoires et calcule leur moyenne"*
        
        ### 🔧 **Exemples Projets**
        - *"Développe une todo-list en HTML/CSS/JS"*
        - *"Crée une calculatrice web moderne"*
        - *"Génère un site portfolio responsive"*
        - *"Fais une API REST Flask simple"*
        
        ### 💬 **Chat Général**
        - Questions techniques avec contexte
        - Analyse de fichiers uploadés
        - Explications détaillées
        - Conseils et recommandations
        
        **🚀 Commencez par uploader un fichier ou poser une question !**
        """)
    
    # Footer avec statistiques
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**🧠 OpenAI 120B**")
        st.caption("Assistant IA Avancé")
    
    with col2:
        st.markdown("**⚡ Python**")
        st.caption("Exécution sécurisée")
    
    with col3:
        st.markdown("**🚀 Projets**")
        st.caption(f"{st.session_state.projects_created} créés")
    
    with col4:
        st.markdown("**💾 Session**")
        st.caption(f"{len(st.session_state.messages)} messages")
    
    # Version et informations
    st.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.8rem; margin-top: 1rem;'>"
        f"💡 Version 4.0 Simplifié | Session: {st.session_state.session_tokens} tokens | "
        f"Projets: {st.session_state.projects_created} | "
        f"Exécutions: {st.session_state.code_executions} | "
        f"{theme_status}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()