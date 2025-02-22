import string
import random
import hashlib
import base64
import json
import re
from typing import Dict, Any

def generate_password(length: int = 12, include_numbers: bool = True, include_symbols: bool = True) -> str:
    """Génère un mot de passe sécurisé"""
    if length < 8:
        raise ValueError("La longueur minimale est de 8 caractères")
    
    chars = string.ascii_letters
    if include_numbers:
        chars += string.digits
    if include_symbols:
        chars += string.punctuation
        
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

def validate_password(password: str) -> Dict[str, Any]:
    """Valide la force d'un mot de passe"""
    score = 0
    feedback = []
    
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Le mot de passe est trop court")

    if re.search(r'[A-Z]', password): score += 1
    if re.search(r'[a-z]', password): score += 1
    if re.search(r'\d', password): score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 1
    
    strength = ['Très faible', 'Faible', 'Moyen', 'Fort', 'Très fort'][min(score, 4)]
    
    return {
        'score': score,
        'strength': strength,
        'feedback': feedback
    }

def calculate_hash(text: str, algorithm: str = 'sha256') -> str:
    """Calcule le hash d'un texte"""
    algorithms = {
        'md5': hashlib.md5(),
        'sha1': hashlib.sha1(),
        'sha256': hashlib.sha256(),
        'sha512': hashlib.sha512()
    }
    
    if algorithm not in algorithms:
        raise ValueError(f"Algorithme non supporté. Utilisez: {', '.join(algorithms.keys())}")
        
    hasher = algorithms[algorithm]
    hasher.update(text.encode())
    return hasher.hexdigest()

def encode_decode_base64(text: str, operation: str = 'encode') -> str:
    """Encode ou décode en Base64"""
    if operation == 'encode':
        return base64.b64encode(text.encode()).decode()
    elif operation == 'decode':
        return base64.b64decode(text.encode()).decode()
    else:
        raise ValueError("Opération invalide. Utilisez 'encode' ou 'decode'")

def format_json(json_str: str, indent: int = 2) -> str:
    """Formate du JSON"""
    try:
        if not json_str.strip():
            return ""
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=indent, ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide: {str(e)}")

def minify_code(code: str, language: str = 'json') -> str:
    """Minifie du code"""
    if language == 'json':
        try:
            return json.dumps(json.loads(code), separators=(',', ':'))
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide: {str(e)}")
    elif language in ['html', 'css', 'js']:
        # Suppression basique des espaces et commentaires
        code = re.sub(r'\s+', ' ', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'//.*?\n', '', code)
        return code.strip()
    else:
        raise ValueError(f"Language non supporté: {language}")
