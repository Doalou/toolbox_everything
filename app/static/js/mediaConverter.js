class MediaConverter {
    constructor() {
        this.files = new Map();
        this.initElements();
        this.initEventListeners();
    }

    initElements() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.fileGrid = document.getElementById('fileGrid');
        this.conversionOptions = document.getElementById('conversionOptions');
        this.quality = document.getElementById('quality');
        this.qualityValue = document.getElementById('qualityValue');
        this.outputFormat = document.getElementById('outputFormat');
        this.convertBtn = document.getElementById('convertBtn');
        this.resizeSelect = document.getElementById('resizeOption');
        this.fpsSelect = document.getElementById('fpsOption');
    }

    initEventListeners() {
        // Drag & Drop
        this.dropZone.addEventListener('dragover', e => this.handleDragOver(e));
        this.dropZone.addEventListener('drop', e => this.handleDrop(e));
        this.dropZone.addEventListener('dragenter', () => this.dropZone.classList.add('border-primary-500'));
        this.dropZone.addEventListener('dragleave', () => this.dropZone.classList.remove('border-primary-500'));

        // File Input
        this.fileInput.addEventListener('change', () => this.handleFiles(this.fileInput.files));

        // Quality Slider
        this.quality.addEventListener('input', () => {
            this.qualityValue.textContent = `${this.quality.value}%`;
        });

        // Convert Button
        this.convertBtn.addEventListener('click', () => this.convertFiles());
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }

    handleDrop(e) {
        e.preventDefault();
        this.dropZone.classList.remove('border-primary-500');
        this.handleFiles(e.dataTransfer.files);
    }

    handleFiles(fileList) {
        for (const file of fileList) {
            if (this.isValidFile(file)) {
                this.addFile(file);
            }
        }
        this.updateUI();
    }

    isValidFile(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 
                           'video/mp4', 'video/webm', 'video/x-matroska'];
        return validTypes.includes(file.type);
    }

    addFile(file) {
        const id = crypto.randomUUID();
        this.files.set(id, file);
        this.addFileCard(id, file);
    }

    addFileCard(id, file) {
        const template = document.getElementById('fileCardTemplate');
        const card = template.content.cloneNode(true);
        
        const preview = card.querySelector('.preview');
        if (file.type.startsWith('image/')) {
            preview.src = URL.createObjectURL(file);
        } else {
            preview.src = '/static/img/video-placeholder.png';  // À créer
        }

        card.querySelector('.filename').textContent = file.name;
        card.querySelector('.remove-file').addEventListener('click', () => {
            this.removeFile(id);
        });

        this.fileGrid.appendChild(card);
    }

    removeFile(id) {
        this.files.delete(id);
        this.updateUI();
    }

    updateUI() {
        const hasFiles = this.files.size > 0;
        this.fileList.classList.toggle('hidden', !hasFiles);
        this.conversionOptions.classList.toggle('hidden', !hasFiles);
    }

    async convertFiles() {
        try {
            this.convertBtn.disabled = true;
            this.convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Conversion...';

            for (const [id, file] of this.files.entries()) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('format', this.outputFormat.value);
                formData.append('quality', this.quality.value);

                // Ajout des options avancées
                if (this.resizeSelect?.value) {
                    formData.append('resize', this.resizeSelect.value);
                }
                if (this.fpsSelect?.value) {
                    formData.append('fps', this.fpsSelect.value);
                }

                const response = await fetch('/media/convert', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Erreur de conversion');
                }

                const blob = await response.blob();
                const downloadUrl = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `converted_${file.name.split('.')[0]}.${this.outputFormat.value}`;
                a.click();
                URL.revokeObjectURL(downloadUrl);
            }

            createNotification('Conversion terminée !', 'success');
        } catch (error) {
            createNotification(error.message, 'error');
        } finally {
            this.convertBtn.disabled = false;
            this.convertBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Convertir';
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => new MediaConverter());
