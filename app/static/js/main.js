const NOTIFICATION_DURATION = 3000;
const NOTIFICATION_TYPES = { ERROR: 'error', SUCCESS: 'success' };

const createNotification = (message, type = NOTIFICATION_TYPES.SUCCESS) => {
    const element = document.createElement('div');
    element.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === NOTIFICATION_TYPES.ERROR ? 'bg-red-500' : 'bg-green-500'
    } text-white z-50`;
    element.textContent = message;
    
    requestAnimationFrame(() => {
        document.body.appendChild(element);
        setTimeout(() => element.remove(), NOTIFICATION_DURATION);
    });
};

const handleError = (error) => {
    console.error('Error:', error);
    createNotification(error.message || 'Une erreur est survenue', NOTIFICATION_TYPES.ERROR);
};

export { createNotification, handleError };
