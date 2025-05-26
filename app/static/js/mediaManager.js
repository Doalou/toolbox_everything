import { createNotification, handleError } from './main.js';

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
                createNotification('Fichier trop volumineux (max 500MB)', 'error');
                return false;
            }
            return true;
        });

        for (const file of validFiles) {
            try {
                this.showProgress(`Conversion de ${file.name}`);
                await this.processFile(file);
                createNotification('Conversion réussie !');
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
        formData.append('format', document.querySelector('[name="format"]').value);
        formData.append('quality', document.querySelector('[name="quality"]').value);

        const response = await fetch('/media/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(await response.text());

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted_${file.name}`;
        a.click();
        URL.revokeObjectURL(url);
    }

    showProgress(message) {
        this.progressText.textContent = message;
        this.progressOverlay.classList.remove('hidden');
    }

    hideProgress() {
        this.progressOverlay.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => new MediaManager());

function showNotification(message, type = 'info') {
    const notifications = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = `p-4 rounded-lg shadow-lg ${
        type === 'error' ? 'bg-red-500' : 'bg-green-500'
    } text-white mb-2`;
    notification.textContent = message;
    notifications.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}
