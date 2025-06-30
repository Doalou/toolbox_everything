// Configuration
const CONFIG = {
    MAX_FILE_SIZE: 500 * 1024 * 1024,
    SUPPORTED_FORMATS: {
        image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        video: ['video/mp4', 'video/webm', 'video/avi']
    }
};

class MediaManager {
    constructor() {
        this.initElements();
        this.initEventListeners();
    }

    initElements() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.progressOverlay = document.getElementById('progressOverlay');
        this.progressText = document.getElementById('progressText');
    }

    initEventListeners() {
        const dropZone = this.dropZone;
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('border-primary-500');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('border-primary-500');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('border-primary-500');
                this.handleFiles(e.dataTransfer.files);
            });
        }

        this.fileInput?.addEventListener('change', (e) => this.handleFiles(e.target.files));
    }

    async handleFiles(files) {
        const validFiles = Array.from(files).filter(file => {
            if (file.size > CONFIG.MAX_FILE_SIZE) {
                showNotification('Fichier trop volumineux (max 500MB)', 'error');
                return false;
            }
            
            // Vérification du type MIME
            const isValidType = Object.values(CONFIG.SUPPORTED_FORMATS)
                .flat()
                .includes(file.type);
            
            if (!isValidType) {
                showNotification(`Type de fichier non supporté: ${file.type}`, 'error');
                return false;
            }
            
            return true;
        });

        for (const file of validFiles) {
            try {
                this.showProgress(`Conversion de ${file.name}`);
                await this.processFile(file);
                showNotification('Conversion réussie !');
            } catch (error) {
                handleError(error);
            } finally {
                this.hideProgress();
            }
        }
    }

    async processFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Récupération des options depuis les éléments de la page
        const formatElement = document.querySelector('[name="format"]');
        const qualityElement = document.querySelector('[name="quality"]');
        
        if (formatElement) {
            formData.append('format', formatElement.value);
        }
        if (qualityElement) {
            formData.append('quality', qualityElement.value);
        }

        const response = await fetch('/media/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erreur de conversion: ${errorText}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted_${file.name}`;
        a.click();
        URL.revokeObjectURL(url);
    }

    showProgress(message) {
        if (this.progressText) {
            this.progressText.textContent = message;
        }
        if (this.progressOverlay) {
            this.progressOverlay.classList.remove('hidden');
        }
    }

    hideProgress() {
        if (this.progressOverlay) {
            this.progressOverlay.classList.add('hidden');
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    new MediaManager();
});
