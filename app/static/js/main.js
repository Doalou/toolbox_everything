// Configuration globale
const NOTIFICATION_DURATION = 3000;
const NOTIFICATION_TYPES = { ERROR: 'error', SUCCESS: 'success' };

// Création de notification moderne
const createNotification = (message, type = NOTIFICATION_TYPES.SUCCESS) => {
    const element = document.createElement('div');
    element.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === NOTIFICATION_TYPES.ERROR ? 'bg-red-500' : 'bg-green-500'
    } text-white z-50 transform translate-x-full transition-transform duration-300`;
    element.textContent = message;
    
    document.body.appendChild(element);
    
    // Animation d'entrée
    requestAnimationFrame(() => {
        element.classList.remove('translate-x-full');
    });
    
    // Suppression automatique
    setTimeout(() => {
        element.classList.add('translate-x-full');
        setTimeout(() => {
            if (element.parentNode) {
                element.remove();
            }
        }, 300);
    }, NOTIFICATION_DURATION);
};

// Fonction globale compatible avec les templates existants
function showNotification(message, type = 'success') {
    const notificationsContainer = document.getElementById('notifications');
    if (!notificationsContainer) {
        // Fallback à la notification moderne si le container n'existe pas
        createNotification(message, type);
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = `p-4 rounded-lg shadow-lg mb-2 transform translate-x-full transition-all duration-300 ${
        type === 'error' ? 'bg-red-500' : 'bg-green-500'
    } text-white`;
    notification.textContent = message;
    
    notificationsContainer.appendChild(notification);
    
    // Animation d'entrée
    requestAnimationFrame(() => {
        notification.classList.remove('translate-x-full');
    });
    
    // Suppression automatique
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, NOTIFICATION_DURATION);
}

// Gestionnaire d'erreurs global
const handleError = (error) => {
    console.error('Error:', error);
    showNotification(error.message || 'Une erreur est survenue', NOTIFICATION_TYPES.ERROR);
};

// Utilitaires pour les formulaires
const FormUtils = {
    // Validation d'email
    validateEmail: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Validation d'URL
    validateURL: (url) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },
    
    // Sérialisation de formulaire
    serializeForm: (form) => {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    }
};

// Utilitaires pour les fichiers
const FileUtils = {
    // Formatage de taille de fichier
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Validation de type de fichier
    isValidFileType: (file, allowedTypes) => {
        return allowedTypes.includes(file.type);
    }
};

// Export pour utilisation en modules ES6
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { createNotification, handleError, showNotification, FormUtils, FileUtils };
}

// Export pour utilisation globale
window.showNotification = showNotification;
window.createNotification = createNotification;
window.handleError = handleError;
window.FormUtils = FormUtils;
window.FileUtils = FileUtils;
