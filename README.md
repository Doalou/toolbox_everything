# 🛠️ Toolbox Everything

Une boîte à outils web moderne pour vos besoins quotidiens.

## 🌟 Fonctionnalités

### 🔒 Sécurité
- Générateur et validateur de mots de passe
- Calculateur de hash (MD5, SHA-1, SHA-256, SHA-512)

### 🔄 Conversion
- Encodeur/Décodeur Base64
- Formateur JSON
- Générateur de QR Code

### 🎬 Multimédia
- YouTube Downloader (MP4/MP3)
- Convertisseur de médias (images/vidéos)
- Redimensionnement d'images

## 🚀 Technologies utilisées

- Backend: Python avec Flask
- Frontend: HTML, TailwindCSS, JavaScript
- Dépendances principales:
  - `yt-dlp` pour YouTube
  - `Pillow` pour le traitement d'images
  - `qrcode` pour la génération de QR codes

## 📦 Installation

1. Clonez le dépôt
```bash
git clone https://github.com/doalou/toolbox_everything.git
cd toolbox_everything
```

2. Installez les dépendances
```bash
pip install -r requirements.txt
```

3. Lancez l'application
```bash
flask run
```

L'application sera disponible à l'adresse `http://localhost:5000`

## 🔧 Configuration

Pas besoin de configuration, tout est "clé en main"

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou un pull request.

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez un Pull Request

## 📝 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 🙏 Remerciements

- [Flask](https://flask.palletsprojects.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [Font Awesome](https://fontawesome.com/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)