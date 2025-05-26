"""
Outils essentiels pour Toolbox Everything
"""
import re
import json
import base64
import hashlib
import secrets
import string
import colorsys
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
import qrcode
from io import BytesIO
import requests

class QRCodeGenerator:
    """Générateur de QR codes"""
    
    ERROR_CORRECTION_LEVELS = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    
    def generate(self, text: str, size: int = 10, border: int = 4, 
                error_correction: str = 'M') -> str:
        """Génère un QR code et retourne l'image en base64"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=self.ERROR_CORRECTION_LEVELS.get(error_correction, 
                                                                qrcode.constants.ERROR_CORRECT_M),
                box_size=size,
                border=border,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en base64
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la génération du QR code: {str(e)}")

class PasswordGenerator:
    """Générateur de mots de passe sécurisés"""
    
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    NUMBERS = string.digits
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    AMBIGUOUS = "il1Lo0O"
    
    def generate(self, length: int = 16, uppercase: bool = True, 
                lowercase: bool = True, numbers: bool = True, 
                symbols: bool = True, exclude_ambiguous: bool = True) -> str:
        """Génère un mot de passe selon les critères"""
        
        char_pool = ""
        required_chars = []
        
        if lowercase:
            chars = self.LOWERCASE
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.AMBIGUOUS)
            char_pool += chars
            required_chars.append(secrets.choice(chars))
        
        if uppercase:
            chars = self.UPPERCASE
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.AMBIGUOUS)
            char_pool += chars
            required_chars.append(secrets.choice(chars))
        
        if numbers:
            chars = self.NUMBERS
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.AMBIGUOUS)
            char_pool += chars
            required_chars.append(secrets.choice(chars))
        
        if symbols:
            char_pool += self.SYMBOLS
            required_chars.append(secrets.choice(self.SYMBOLS))
        
        if not char_pool:
            raise ValueError("Aucun type de caractère sélectionné")
        
        # Générer le reste du mot de passe
        remaining_length = length - len(required_chars)
        if remaining_length < 0:
            remaining_length = 0
        
        password_chars = required_chars + [secrets.choice(char_pool) 
                                         for _ in range(remaining_length)]
        
        # Mélanger les caractères
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)
    
    def calculate_strength(self, password: str) -> Dict[str, Any]:
        """Calcule la force d'un mot de passe"""
        score = 0
        feedback = []
        
        # Longueur
        length = len(password)
        if length >= 12:
            score += 25
        elif length >= 8:
            score += 15
        else:
            feedback.append("Mot de passe trop court")
        
        # Types de caractères
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in self.SYMBOLS for c in password)
        
        char_types = sum([has_lower, has_upper, has_digit, has_symbol])
        score += char_types * 15
        
        if char_types < 3:
            feedback.append("Utilisez différents types de caractères")
        
        # Patterns répétitifs
        if re.search(r'(.)\1{2,}', password):
            score -= 10
            feedback.append("Évitez les caractères répétitifs")
        
        # Déterminer le niveau
        if score >= 80:
            level = "Très fort"
            color = "green"
        elif score >= 60:
            level = "Fort"
            color = "blue"
        elif score >= 40:
            level = "Moyen"
            color = "orange"
        else:
            level = "Faible"
            color = "red"
        
        return {
            'score': min(100, max(0, score)),
            'level': level,
            'color': color,
            'feedback': feedback
        }

class TextProcessor:
    """Processeur de texte avancé"""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyse complète d'un texte"""
        lines = text.split('\n')
        words = text.split()
        
        # Statistiques de base
        stats = {
            'characters': len(text),
            'characters_no_spaces': len(text.replace(' ', '')),
            'words': len(words),
            'lines': len(lines),
            'paragraphs': len([p for p in text.split('\n\n') if p.strip()]),
            'sentences': len(re.findall(r'[.!?]+', text)),
        }
        
        # Statistiques avancées
        if words:
            stats['avg_word_length'] = sum(len(word) for word in words) / len(words)
            stats['longest_word'] = max(words, key=len)
            stats['shortest_word'] = min(words, key=len)
        
        # Fréquence des mots
        word_freq = {}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Top 10 des mots les plus fréquents
        most_common = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'statistics': stats,
            'most_common_words': most_common,
            'reading_time': round(len(words) / 200)  # Mots par minute moyen
        }
    
    def format_text(self, text: str, format_type: str) -> str:
        """Formate le texte selon le type spécifié"""
        if format_type == 'uppercase':
            return text.upper()
        elif format_type == 'lowercase':
            return text.lower()
        elif format_type == 'title':
            return text.title()
        elif format_type == 'sentence':
            return '. '.join(s.strip().capitalize() for s in text.split('.') if s.strip())
        elif format_type == 'reverse':
            return text[::-1]
        elif format_type == 'remove_extra_spaces':
            return re.sub(r'\s+', ' ', text.strip())
        else:
            return text
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte des caractères indésirables"""
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # Nettoyer les sauts de ligne multiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

class ColorPaletteGenerator:
    """Générateur de palettes de couleurs"""
    
    def generate(self, base_color: str, palette_type: str, count: int) -> List[Dict[str, str]]:
        """Génère une palette de couleurs"""
        try:
            # Convertir la couleur de base en HSV
            base_rgb = self._hex_to_rgb(base_color)
            base_hsv = colorsys.rgb_to_hsv(*[c/255.0 for c in base_rgb])
            
            colors = []
            
            if palette_type == 'monochromatic':
                colors = self._generate_monochromatic(base_hsv, count)
            elif palette_type == 'analogous':
                colors = self._generate_analogous(base_hsv, count)
            elif palette_type == 'complementary':
                colors = self._generate_complementary(base_hsv, count)
            elif palette_type == 'triadic':
                colors = self._generate_triadic(base_hsv, count)
            else:
                colors = self._generate_random(count)
            
            return colors
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la génération de la palette: {str(e)}")
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convertit une couleur hex en RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convertit RGB en hex"""
        return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
    
    def _generate_monochromatic(self, base_hsv: tuple, count: int) -> List[Dict[str, str]]:
        """Génère une palette monochromatique"""
        colors = []
        h, s, v = base_hsv
        
        for i in range(count):
            # Varier la saturation et la luminosité
            new_s = max(0.1, min(1.0, s + (i - count//2) * 0.15))
            new_v = max(0.1, min(1.0, v + (i - count//2) * 0.1))
            
            rgb = colorsys.hsv_to_rgb(h, new_s, new_v)
            rgb = tuple(int(c * 255) for c in rgb)
            
            colors.append({
                'hex': self._rgb_to_hex(rgb),
                'rgb': f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
            })
        
        return colors
    
    def _generate_analogous(self, base_hsv: tuple, count: int) -> List[Dict[str, str]]:
        """Génère une palette analogique"""
        colors = []
        h, s, v = base_hsv
        
        for i in range(count):
            # Varier la teinte de ±30 degrés
            new_h = (h + (i - count//2) * 0.083) % 1.0  # 30°/360° = 0.083
            
            rgb = colorsys.hsv_to_rgb(new_h, s, v)
            rgb = tuple(int(c * 255) for c in rgb)
            
            colors.append({
                'hex': self._rgb_to_hex(rgb),
                'rgb': f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
            })
        
        return colors
    
    def _generate_complementary(self, base_hsv: tuple, count: int) -> List[Dict[str, str]]:
        """Génère une palette complémentaire"""
        colors = []
        h, s, v = base_hsv
        
        # Couleur de base
        rgb = colorsys.hsv_to_rgb(h, s, v)
        rgb = tuple(int(c * 255) for c in rgb)
        colors.append({
            'hex': self._rgb_to_hex(rgb),
            'rgb': f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
        })
        
        # Couleur complémentaire
        comp_h = (h + 0.5) % 1.0
        rgb = colorsys.hsv_to_rgb(comp_h, s, v)
        rgb = tuple(int(c * 255) for c in rgb)
        colors.append({
            'hex': self._rgb_to_hex(rgb),
            'rgb': f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
        })
        
        # Remplir avec des variations
        while len(colors) < count:
            variation_h = h if len(colors) % 2 == 0 else comp_h
            new_s = max(0.1, min(1.0, s + (len(colors) * 0.1)))
            new_v = max(0.1, min(1.0, v - (len(colors) * 0.05)))
            
            rgb = colorsys.hsv_to_rgb(variation_h, new_s, new_v)
            rgb = tuple(int(c * 255) for c in rgb)
            colors.append({
                'hex': self._rgb_to_hex(rgb),
                'rgb': f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
            })
        
        return colors[:count]
    
    def _generate_triadic(self, base_hsv: tuple, count: int) -> List[Dict[str, str]]:
        """Génère une palette triadique"""
        colors = []
        h, s, v = base_hsv
        
        # Trois couleurs espacées de 120°
        hues = [h, (h + 0.333) % 1.0, (h + 0.666) % 1.0]
        
        for i in range(count):
            current_h = hues[i % 3]
            # Varier légèrement s et v
            new_s = max(0.1, min(1.0, s + (i // 3) * 0.1))
            new_v = max(0.1, min(1.0, v - (i // 3) * 0.05))
            
            rgb = colorsys.hsv_to_rgb(current_h, new_s, new_v)
            rgb = tuple(int(c * 255) for c in rgb)
            
            colors.append({
                'hex': self._rgb_to_hex(rgb),
                'rgb': f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
            })
        
        return colors
    
    def _generate_random(self, count: int) -> List[Dict[str, str]]:
        """Génère une palette aléatoire"""
        colors = []
        for _ in range(count):
            h = secrets.randbelow(360) / 360.0
            s = 0.5 + secrets.randbelow(50) / 100.0
            v = 0.5 + secrets.randbelow(50) / 100.0
            
            rgb = colorsys.hsv_to_rgb(h, s, v)
            rgb = tuple(int(c * 255) for c in rgb)
            
            colors.append({
                'hex': self._rgb_to_hex(rgb),
                'rgb': f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
            })
        
        return colors

class URLValidator:
    """Validateur et analyseur d'URLs"""
    
    def validate_and_analyze(self, url: str) -> Dict[str, Any]:
        """Valide et analyse une URL"""
        try:
            parsed = urlparse(url)
            
            # Validation de base
            is_valid = bool(parsed.scheme and parsed.netloc)
            
            analysis = {
                'is_valid': is_valid,
                'url': url,
                'components': {
                    'scheme': parsed.scheme,
                    'domain': parsed.netloc,
                    'path': parsed.path,
                    'query': parsed.query,
                    'fragment': parsed.fragment
                }
            }
            
            if is_valid:
                # Informations supplémentaires
                analysis['is_secure'] = parsed.scheme == 'https'
                analysis['has_query'] = bool(parsed.query)
                analysis['has_fragment'] = bool(parsed.fragment)
                
                # Tentative de ping (avec timeout court)
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    analysis['status'] = {
                        'accessible': response.status_code < 400,
                        'status_code': response.status_code,
                        'final_url': response.url if response.url != url else None
                    }
                except:
                    analysis['status'] = {
                        'accessible': False,
                        'error': 'Impossible de vérifier l\'accessibilité'
                    }
            
            return analysis
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e)
            }

class HashCalculator:
    """Calculateur de hash"""
    
    ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512']
    
    def calculate(self, text: str, algorithm: str = 'sha256') -> Dict[str, str]:
        """Calcule le hash d'un texte"""
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"Algorithme non supporté: {algorithm}")
        
        try:
            hasher = hashlib.new(algorithm)
            hasher.update(text.encode('utf-8'))
            
            return {
                'algorithm': algorithm,
                'input': text,
                'hash': hasher.hexdigest(),
                'length': len(hasher.hexdigest())
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors du calcul du hash: {str(e)}")

class Base64Encoder:
    """Encodeur/Décodeur Base64"""
    
    def encode(self, text: str) -> str:
        """Encode en Base64"""
        try:
            encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')
            return encoded
        except Exception as e:
            raise ValueError(f"Erreur lors de l'encodage: {str(e)}")
    
    def decode(self, encoded_text: str) -> str:
        """Décode du Base64"""
        try:
            decoded = base64.b64decode(encoded_text.encode('ascii')).decode('utf-8')
            return decoded
        except Exception as e:
            raise ValueError(f"Erreur lors du décodage: {str(e)}")

class JSONFormatter:
    """Formateur JSON"""
    
    def process(self, json_text: str, operation: str = 'format') -> Dict[str, Any]:
        """Traite du JSON"""
        try:
            # Validation
            parsed = json.loads(json_text)
            
            result = {
                'is_valid': True,
                'original': json_text
            }
            
            if operation == 'format':
                result['formatted'] = json.dumps(parsed, indent=2, ensure_ascii=False)
            elif operation == 'minify':
                result['minified'] = json.dumps(parsed, separators=(',', ':'))
            elif operation == 'validate':
                result['structure'] = self._analyze_structure(parsed)
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                'is_valid': False,
                'error': str(e),
                'line': e.lineno,
                'column': e.colno
            }
    
    def _analyze_structure(self, obj: Any, depth: int = 0) -> Dict[str, Any]:
        """Analyse la structure d'un objet JSON"""
        if isinstance(obj, dict):
            return {
                'type': 'object',
                'keys': len(obj),
                'depth': depth,
                'properties': {k: self._analyze_structure(v, depth + 1) for k, v in obj.items()}
            }
        elif isinstance(obj, list):
            return {
                'type': 'array',
                'length': len(obj),
                'depth': depth,
                'items': [self._analyze_structure(item, depth + 1) for item in obj[:5]]  # Limiter à 5
            }
        else:
            return {
                'type': type(obj).__name__,
                'depth': depth,
                'value': str(obj)[:100]  # Limiter la longueur
            }

class TimestampConverter:
    """Convertisseur de timestamps"""
    
    def timestamp_to_date(self, timestamp: int, tz: str = 'UTC') -> Dict[str, Any]:
        """Convertit un timestamp en date"""
        try:
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            
            return {
                'timestamp': timestamp,
                'iso': dt.isoformat(),
                'human': dt.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'formats': {
                    'date': dt.strftime('%Y-%m-%d'),
                    'time': dt.strftime('%H:%M:%S'),
                    'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'iso': dt.isoformat()
                }
            }
            
        except Exception as e:
            raise ValueError(f"Timestamp invalide: {str(e)}")
    
    def date_to_timestamp(self, date_str: str, tz: str = 'UTC') -> Dict[str, Any]:
        """Convertit une date en timestamp"""
        try:
            # Essayer plusieurs formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y',
                '%Y-%m-%dT%H:%M:%S'
            ]
            
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                raise ValueError("Format de date non reconnu")
            
            # Appliquer le timezone UTC
            dt = dt.replace(tzinfo=timezone.utc)
            timestamp = int(dt.timestamp())
            
            return {
                'date': date_str,
                'timestamp': timestamp,
                'iso': dt.isoformat(),
                'human': dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            
        except Exception as e:
            raise ValueError(f"Date invalide: {str(e)}")
    
    def current_timestamp(self) -> Dict[str, Any]:
        """Retourne le timestamp actuel"""
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp())
        
        return {
            'current_timestamp': timestamp,
            'iso': now.isoformat(),
            'human': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'formats': {
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M:%S'),
                'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                'iso': now.isoformat()
            }
        } 