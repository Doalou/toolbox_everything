document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imageForm = document.getElementById('imageConvertForm');
    const videoForm = document.getElementById('videoConvertForm');
    
    // Gestion du drag & drop
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
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    const progressOverlay = document.getElementById('progressOverlay');
    const progressText = document.getElementById('progressText');

    function showProgress(message) {
        progressText.textContent = message;
        progressOverlay.classList.remove('hidden');
    }

    function hideProgress() {
        progressOverlay.classList.add('hidden');
    }

    function handleFiles(files) {
        Array.from(files).forEach(file => {
            // Vérifier la taille du fichier (500MB max)
            if (file.size > 500 * 1024 * 1024) {
                showNotification('Le fichier est trop volumineux (max 500MB)', 'error');
                return;
            }
            
            if (file.type.startsWith('image/')) {
                processImage(file);
            } else if (file.type.startsWith('video/')) {
                processVideo(file);
            }
        });
    }

    async function processImage(file) {
        showProgress(`Conversion de l'image "${file.name}" en cours...`);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('output_format', imageForm.querySelector('[name="format"]').value);
        formData.append('quality', imageForm.querySelector('[name="quality"]').value);

        try {
            const response = await fetch('/media/convert', {  // Mise à jour du chemin
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.text();  // Utiliser text() au lieu de json()
                try {
                    const jsonError = JSON.parse(error);
                    throw new Error(jsonError.error || 'Erreur lors de la conversion');
                } catch (e) {
                    throw new Error(error || 'Erreur lors de la conversion');
                }
            }

            // Téléchargement du fichier
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `converted_${file.name}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showNotification('Conversion réussie !', 'success');
        } catch (error) {
            console.error('Erreur:', error);
            showNotification(error.message, 'error');
        } finally {
            hideProgress();
        }
    }

    async function processVideo(file) {
        showProgress(`Conversion de la vidéo "${file.name}" en cours...\nCela peut prendre quelques minutes.`);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('output_format', videoForm.querySelector('[name="format"]').value);
        formData.append('quality', videoForm.querySelector('[name="quality"]').value);

        try {
            const response = await fetch('/media/convert', {  // Mise à jour du chemin
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.text();  // Utiliser text() au lieu de json()
                try {
                    const jsonError = JSON.parse(error);
                    throw new Error(jsonError.error || 'Erreur lors de la conversion');
                } catch (e) {
                    throw new Error(error || 'Erreur lors de la conversion');
                }
            }

            // Téléchargement du fichier
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `converted_${file.name}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showNotification('Conversion réussie !', 'success');
        } catch (error) {
            console.error('Erreur:', error);
            showNotification(error.message, 'error');
        } finally {
            hideProgress();
        }
    }

    // Gestion des formulaires avec désactivation des boutons
    imageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = imageForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        try {
            const files = fileInput.files;
            await Promise.all(Array.from(files)
                .filter(f => f.type.startsWith('image/'))
                .map(processImage));
        } finally {
            submitBtn.disabled = false;
        }
    });

    videoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = videoForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        try {
            const files = fileInput.files;
            await Promise.all(Array.from(files)
                .filter(f => f.type.startsWith('video/'))
                .map(processVideo));
        } finally {
            submitBtn.disabled = false;
        }
    });
});

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
