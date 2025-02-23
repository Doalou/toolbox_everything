import string
import random
import hashlib
import base64
import json
import re
from typing import Dict, Any, Tuple, Optional
from io import BytesIO
import qrcode
from PIL import Image

# Constantes
HASH_ALGORITHMS = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha256': hashlib.sha256,
    'sha512': hashlib.sha512
}

SUPPORTED_LANGUAGES = {'json', 'html', 'css', 'js'}

class ValidationError(ValueError):
    """Erreur personnalisée pour la validation"""
    pass

class PasswordGenerator:
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    MIN_LENGTH = 8
    
    def __init__(self):
        self.length = 12
        self.use_lowercase = True
        self.use_uppercase = True
        self.use_digits = True
        self.use_symbols = True
        self.exclude_similar = False
        self.exclude_ambiguous = False
        
    def configure(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
        
    def _get_charset(self):
        charset = ""
        if self.use_lowercase:
            charset += self.LOWERCASE
        if self.use_uppercase:
            charset += self.UPPERCASE
        if self.use_digits:
            charset += self.DIGITS
        if self.use_symbols:
            charset += self.SYMBOLS
            
        if self.exclude_similar:
            charset = charset.translate(str.maketrans("", "", "il1Lo0O"))
        if self.exclude_ambiguous:
            charset = charset.translate(str.maketrans("", "", "`{}[]()\/'\";:,.<>"))
            
        return charset

    def generate(self):
        if self.length < self.MIN_LENGTH:
            raise ValueError("La longueur minimale est de 8 caractères")
            
        charset = self._get_charset()
        if not charset:
            raise ValueError("Au moins un ensemble de caractères doit être sélectionné")
            
        # Assure au moins un caractère de chaque type sélectionné
        password = []
        if self.use_lowercase:
            password.append(random.choice(self.LOWERCASE))
        if self.use_uppercase:
            password.append(random.choice(self.UPPERCASE))
        if self.use_digits:
            password.append(random.choice(self.DIGITS))
        if self.use_symbols:
            password.append(random.choice(self.SYMBOLS))
            
        # Complète avec des caractères aléatoires
        remaining_length = self.length - len(password)
        password.extend(random.choice(charset) for _ in range(remaining_length))
        
        # Mélange le mot de passe
        random.shuffle(password)
        return ''.join(password)

def analyze_password_strength(password: str) -> dict:
    """Analyse détaillée de la force d'un mot de passe"""
    
    # Critères de validation
    LENGTH_MIN = 8
    LENGTH_STRONG = 12
    UNIQUE_RATIO_MIN = 0.7
    
    analysis = {
        'score': 0,
        'strength': '',
        'feedback': [],
        'criteria': {
            'length': {'met': False, 'min': LENGTH_MIN, 'value': len(password)},
            'lowercase': {'met': False, 'count': 0},
            'uppercase': {'met': False, 'count': 0},
            'digits': {'met': False, 'count': 0},
            'symbols': {'met': False, 'count': 0},
            'unique_chars': {'met': False, 'count': 0, 'ratio': 0}
        }
    }
    
    if not password:
        analysis['strength'] = 'Très faible'
        analysis['feedback'].append('Le mot de passe est vide')
        return analysis
    
    # Calcul des statistiques
    analysis['criteria']['unique_chars']['count'] = len(set(password))
    analysis['criteria']['unique_chars']['ratio'] = len(set(password)) / len(password)
    analysis['criteria']['lowercase']['count'] = sum(c.islower() for c in password)
    analysis['criteria']['uppercase']['count'] = sum(c.isupper() for c in password)
    analysis['criteria']['digits']['count'] = sum(c.isdigit() for c in password)
    analysis['criteria']['symbols']['count'] = sum(not c.isalnum() for c in password)
    
    # Évaluation des critères
    score = 0
    
    # Longueur (0-2 points)
    if len(password) >= LENGTH_STRONG:
        score += 2
        analysis['criteria']['length']['met'] = True
    elif len(password) >= LENGTH_MIN:
        score += 1
        analysis['criteria']['length']['met'] = True
    else:
        analysis['feedback'].append(f'Le mot de passe doit faire au moins {LENGTH_MIN} caractères')
    
    # Caractères uniques (0-2 points)
    if analysis['criteria']['unique_chars']['ratio'] >= UNIQUE_RATIO_MIN:
        score += 2
        analysis['criteria']['unique_chars']['met'] = True
    
    # Types de caractères (1 point chacun)
    checks = [
        ('lowercase', 'minuscule'),
        ('uppercase', 'majuscule'),
        ('digits', 'chiffre'),
        ('symbols', 'caractère spécial')
    ]
    
    for key, name in checks:
        if analysis['criteria'][key]['count'] > 0:
            score += 1
            analysis['criteria'][key]['met'] = True
        else:
            analysis['feedback'].append(f'Ajoutez au moins un {name}')
    
    # Score final et niveau de force
    analysis['score'] = min(score, 8)
    
    # Attribution du niveau de force
    if score >= 7:
        analysis['strength'] = 'Très fort'
    elif score >= 5:
        analysis['strength'] = 'Fort'
    elif score >= 4:
        analysis['strength'] = 'Moyen'
    elif score >= 2:
        analysis['strength'] = 'Faible'
    else:
        analysis['strength'] = 'Très faible'
    
    # Feedback par défaut si aucun problème trouvé
    if not analysis['feedback']:
        if score >= 7:
            analysis['feedback'].append('Excellent mot de passe !')
        else:
            analysis['feedback'].append('Ajoutez plus de variété pour renforcer le mot de passe')
    
    return analysis

def calculate_hash(text: str, algorithm: str = 'sha256') -> str:
    """Calcule le hash d'un texte"""
    if algorithm not in HASH_ALGORITHMS:
        raise ValidationError(f"Algorithme non supporté. Utilisez: {', '.join(HASH_ALGORITHMS.keys())}")
        
    hasher = HASH_ALGORITHMS[algorithm]()
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
    if not json_str.strip():
        return ""
    try:
        return json.dumps(json.loads(json_str), indent=indent, ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise ValidationError(f"JSON invalide: {str(e)}")

def minify_code(code: str, language: str = 'json') -> str:
    """Minifie du code"""
    if language not in SUPPORTED_LANGUAGES:
        raise ValidationError(f"Language non supporté: {language}")
        
    if language == 'json':
        try:
            return json.dumps(json.loads(code), separators=(',', ':'))
        except json.JSONDecodeError as e:
            raise ValidationError(f"JSON invalide: {str(e)}")
            
    # Minification basique pour HTML/CSS/JS
    code = re.sub(r'\s+', ' ', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'//.*?\n', '', code)
    return code.strip()

def generate_qr(data: str, 
               size: int = 10,
               border: int = 4,
               color: Tuple[int, int, int] = (0, 0, 0),
               bg_color: Tuple[int, int, int] = (255, 255, 255)) -> BytesIO:
    """Génère un QR code avec les paramètres spécifiés"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Création de l'image avec les couleurs spécifiées
        img = qr.make_image(fill_color=color, back_color=bg_color)
        
        # Conversion en BytesIO avec format PNG explicite
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise ValueError(f"Erreur lors de la génération du QR code: {str(e)}")

def add_logo_to_qr(qr_img: BytesIO, 
                   logo_path: str, 
                   logo_size: Optional[Tuple[int, int]] = None) -> BytesIO:
    """Ajoute un logo au centre du QR code"""
    try:
        # Ouverture avec gestion explicite du mode RGBA
        qr_image = Image.open(qr_img).convert('RGBA')
        logo = Image.open(logo_path).convert('RGBA')
        
        # Calcul de la taille du logo (25% de la taille du QR code par défaut)
        if not logo_size:
            logo_size = (qr_image.size[0] // 4, qr_image.size[1] // 4)
        
        # Redimensionnement du logo avec antialiasing
        logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
        
        # Calcul de la position centrale
        pos = ((qr_image.size[0] - logo.size[0]) // 2,
               (qr_image.size[1] - logo.size[1]) // 2)
        
        # Création d'un nouveau QR code avec le logo
        qr_image.paste(logo, pos, logo)
        
        # Sauvegarde en PNG pour préserver la transparence
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise ValueError(f"Erreur lors de l'ajout du logo: {str(e)}")
