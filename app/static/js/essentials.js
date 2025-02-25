const categoryButtons = document.querySelectorAll('.category-btn');
const toolCards = document.querySelectorAll('.tool-card');

function filterTools(category) {
    toolCards.forEach(card => {
        const matches = category === 'all' || card.dataset.category === category;
        card.style.opacity = matches ? '1' : '0';
        card.style.transform = matches ? 'scale(1) translateY(0)' : 'scale(0.95) translateY(10px)';
        setTimeout(() => {
            card.style.display = matches ? 'block' : 'none';
        }, matches ? 0 : 300);
    });
}

categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        categoryButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        filterTools(btn.dataset.category);
    });
});

let searchTimeout;
toolSearch.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const query = e.target.value.toLowerCase();
        toolCards.forEach(card => {
            const title = card.querySelector('h2').textContent.toLowerCase();
            const matches = title.includes(query);
            card.style.opacity = matches ? '1' : '0';
            card.style.transform = matches ? 'scale(1) translateY(0)' : 'scale(0.95) translateY(10px)';
            setTimeout(() => {
                card.style.display = matches ? 'block' : 'none';
            }, matches ? 0 : 300);
        });
    }, 200);
});

function setLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('btn-loading');
        button.disabled = true;
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
    }
}

async function generatePassword() {
    const length = document.getElementById('pwdLength').value;
    const button = document.querySelector('button[onclick="generatePassword()"]');
    setLoading(button, true);
    try {
        const response = await fetch('/essentials/generate-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length: parseInt(length) })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        document.getElementById('generatedPassword').value = data.password;
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

let passwordDebounce;

function getStrengthColor(strength) {
    const colors = {
        'Très faible': 'text-red-500',
        'Faible': 'text-orange-500',
        'Moyen': 'text-yellow-500',
        'Fort': 'text-green-500',
        'Très fort': 'text-emerald-500'
    };
    return colors[strength] || 'text-gray-500';
}

document.getElementById('textToHash').addEventListener('input', async (e) => {
    if (!e.target.value) {
        document.getElementById('hashResult').value = '';
        return;
    }
    const button = document.querySelector('button[onclick="copyToClipboard(\'hashResult\')"]');
    setLoading(button, true);
    try {
        const algorithm = document.getElementById('hashAlgorithm').value;
        const response = await fetch('/essentials/calculate-hash', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text: e.target.value,
                algorithm: algorithm
            })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        document.getElementById('hashResult').value = data.hash;
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
});

async function handleBase64(operation) {
    const isFileMode = document.getElementById('base64FileSection').classList.contains('hidden') === false;
    const button = document.querySelector(`button[onclick="handleBase64('${operation}')"]`);
    setLoading(button, true);

    try {
        let response;
        if (isFileMode) {
            const file = document.getElementById('fileToBase64').files[0];
            if (!file) {
                throw new Error('Veuillez sélectionner un fichier');
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('operation', operation);
            
            response = await fetch('/essentials/base64-file', {
                method: 'POST',
                body: formData
            });
        } else {
            const text = document.getElementById('base64Input').value;
            if (!text) {
                throw new Error('Veuillez entrer du texte');
            }
            
            response = await fetch('/essentials/base64', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, operation })
            });
        }

        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        document.getElementById('base64Result').value = data.result;
        document.getElementById('downloadBase64Button').classList.toggle('hidden', !isFileMode);
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

async function formatJson() {
    const input = document.getElementById('jsonInput').value;
    const button = document.querySelector('button[onclick="formatJson()"]');
    setLoading(button, true);
    try {
        const response = await fetch('/essentials/format-json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ json: input, indent: 2 })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        document.getElementById('jsonResult').value = data.formatted;
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

async function minifyJson() {
    const input = document.getElementById('jsonInput').value;
    const button = document.querySelector('button[onclick="minifyJson()"]');
    setLoading(button, true);
    try {
        const response = await fetch('/essentials/minify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: input, language: 'json' })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        document.getElementById('jsonResult').value = data.minified;
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    document.execCommand('copy');
    showNotification('Copié dans le presse-papier !', 'success');
}

async function generateQRCode() {
    const content = document.getElementById('qrContent').value;
    if (!content) {
        showNotification('Veuillez entrer un contenu pour le QR code', 'error');
        return;
    }

    const button = document.querySelector('button[onclick="generateQRCode()"]');
    setLoading(button, true);

    try {
        const size = document.getElementById('qrSize').value;
        const border = document.getElementById('qrBorder').value;
        const color = hexToRgb(document.getElementById('qrColor').value);
        const bgColor = hexToRgb(document.getElementById('qrBgColor').value);

        const response = await fetch('/essentials/generate-qr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data: content,
                size: parseInt(size),
                border: parseInt(border),
                color: color,
                bg_color: bgColor
            })
        });

        if (!response.ok) {
            throw new Error('Erreur lors de la génération du QR code');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        const qrResult = document.getElementById('qrResult');
        const qrImage = document.getElementById('qrImage');
        qrImage.src = url;
        qrResult.classList.remove('hidden');

        showNotification('QR Code généré avec succès!', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
    ] : null;
}

function downloadQRCode() {
    const qrImage = document.getElementById('qrImage');
    const link = document.createElement('a');
    link.download = 'qrcode.png';
    link.href = qrImage.src;
    link.click();
}

async function upscaleImage() {
    const imageInput = document.getElementById('imageInput');
    const width = document.getElementById('imageWidth').value;
    const height = document.getElementById('imageHeight').value;
    const maintainRatio = document.getElementById('maintainRatio').checked;
    const button = document.querySelector('button[onclick="upscaleImage()"]');
    setLoading(button, true);

    if (!imageInput.files || !imageInput.files[0]) {
        showNotification('Veuillez sélectionner une image', 'error');
        setLoading(button, false);
        return;
    }

    if (!width && !height) {
        showNotification('Veuillez spécifier au moins une dimension', 'error');
        setLoading(button, false);
        return;
    }

    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    if (width) formData.append('width', width);
    if (height) formData.append('height', height);
    formData.append('maintain_ratio', maintainRatio);

    try {
        const response = await fetch('/essentials/upscale-image', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors du redimensionnement');
        }

        // Téléchargement du fichier
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resized_${imageInput.files[0].name}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showNotification('Image redimensionnée avec succès !', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

function resetImageForm() {
    document.getElementById('imageInput').value = '';
    document.getElementById('imageWidth').value = '';
    document.getElementById('imageHeight').value = '';
    document.getElementById('maintainRatio').checked = true;
    showNotification('Formulaire réinitialisé', 'success');
}

const toolSearch = document.getElementById('toolSearch');
const toolsContainer = document.getElementById('toolsContainer');
const filterButtons = document.querySelectorAll('button[data-category]');

filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const category = btn.getAttribute('data-category');
        document.querySelectorAll('.tool-card').forEach(card => {
            card.style.display = category === 'all' || card.dataset.category === category ? 'block' : 'none';
        });
    });
});

toolSearch.addEventListener('input', () => {
    const query = toolSearch.value.toLowerCase();
    document.querySelectorAll('.tool-card').forEach(card => {
        const title = card.querySelector('h2').textContent.toLowerCase();
        card.style.display = title.includes(query) ? 'block' : 'none';
    });
});

function updatePasswordStrength(analysis) {
    // Mise à jour des barres de force
    const score = analysis.score;
    const maxScore = 8;
    const bars = ['strengthBar1', 'strengthBar2', 'strengthBar3', 'strengthBar4'];
    const colors = {
        'Très faible': 'bg-red-500',
        'Faible': 'bg-orange-500',
        'Moyen': 'bg-yellow-500',
        'Fort': 'bg-green-500',
        'Très fort': 'bg-emerald-500'
    };
    
    // Calcul du nombre de barres à colorer
    const filledBars = Math.ceil((score / maxScore) * bars.length);
    const currentColor = colors[analysis.strength] || 'bg-gray-200';
    
    // Mise à jour des barres
    bars.forEach((barId, index) => {
        const bar = document.getElementById(barId);
        if (bar) {
            bar.className = `h-1.5 rounded-full transition-all duration-300 ${
                index < filledBars ? currentColor : 'bg-gray-200 dark:bg-gray-700'
            }`;
        }
    });
    
    // Mise à jour du texte de force
    const strengthElement = document.getElementById('passwordStrength');
    if (strengthElement) {
        strengthElement.textContent = analysis.strength;
        strengthElement.className = `text-sm ${colors[analysis.strength].replace('bg-', 'text-')}`;
    }
    
    // Mise à jour des critères
    const criteria = {
        'lengthCriterion': analysis.criteria.length.met,
        'upperCriterion': analysis.criteria.uppercase.met,
        'lowerCriterion': analysis.criteria.lowercase.met,
        'numberCriterion': analysis.criteria.digits.met,
        'specialCriterion': analysis.criteria.symbols.met
    };
    
    Object.entries(criteria).forEach(([id, met]) => {
        const element = document.getElementById(id);
        if (element) {
            const icon = element.querySelector('i');
            element.classList.toggle('text-green-500', met);
            element.classList.toggle('text-gray-500', !met);
            if (icon) {
                icon.className = `fas fa-${met ? 'check' : 'circle'} text-xs mr-2`;
            }
        }
    });
}

// Gestionnaire d'événements pour la validation du mot de passe
const passwordInput = document.getElementById('passwordToValidate');
if (passwordInput) {
    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        
        clearTimeout(passwordDebounce);
        passwordDebounce = setTimeout(async () => {
            try {
                const response = await fetch('/essentials/validate-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password })
                });
                
                if (!response.ok) throw new Error('Erreur serveur');
                const analysis = await response.json();
                
                if (analysis.error) throw new Error(analysis.error);
                updatePasswordStrength(analysis);
                
            } catch (error) {
                console.error('Erreur:', error);
                showNotification(error.message || 'Erreur lors de la validation', 'error');
            }
        }, 300);
    });
}

async function validatePassword() {
    const password = document.getElementById('passwordToValidate').value;
    const validationResult = document.getElementById('validationResult');
    const button = document.querySelector('button[onclick="validatePassword()"]');
    
    if (!password) {
        showNotification('Veuillez entrer un mot de passe', 'error');
        return;
    }
    
    setLoading(button, true);
    validationResult.classList.remove('hidden');
    
    try {
        const response = await fetch('/essentials/validate-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });
        
        if (!response.ok) throw new Error('Erreur serveur');
        const analysis = await response.json();
        
        if (analysis.error) throw new Error(analysis.error);
        
        // Mise à jour de l'interface
        const strengthElement = document.getElementById('passwordStrength');
        strengthElement.textContent = analysis.strength;
        strengthElement.className = `font-medium ${getStrengthColor(analysis.strength)}`;
        
        // Mise à jour des barres de force
        const score = analysis.score;
        const maxScore = 8;
        const bars = ['strengthBar1', 'strengthBar2', 'strengthBar3', 'strengthBar4'];
        const colors = {
            'Très faible': 'bg-red-500',
            'Faible': 'bg-orange-500',
            'Moyen': 'bg-yellow-500',
            'Fort': 'bg-green-500',
            'Très fort': 'bg-emerald-500'
        };
        
        const filledBars = Math.ceil((score / maxScore) * bars.length);
        const currentColor = colors[analysis.strength];
        
        bars.forEach((barId, index) => {
            const bar = document.getElementById(barId);
            bar.className = `h-1.5 rounded-full transition-all duration-300 ${
                index < filledBars ? currentColor : 'bg-gray-200 dark:bg-gray-700'
            }`;
        });
        
        // Mise à jour des critères
        const criteria = {
            'lengthCriterion': analysis.criteria.length.met,
            'upperCriterion': analysis.criteria.uppercase.met,
            'lowerCriterion': analysis.criteria.lowercase.met,
            'numberCriterion': analysis.criteria.digits.met,
            'specialCriterion': analysis.criteria.symbols.met
        };
        
        Object.entries(criteria).forEach(([id, met]) => {
            const element = document.getElementById(id);
            const icon = element.querySelector('i');
            element.className = met ? 'text-green-500' : 'text-gray-500';
            icon.className = `fas fa-${met ? 'check' : 'circle'} text-xs mr-2`;
        });
        
        // Affichage du feedback
        const feedbackElement = document.getElementById('passwordFeedback');
        feedbackElement.innerHTML = analysis.feedback.map(feedback => 
            `<div class="flex items-start gap-2 text-gray-600 dark:text-gray-400">
                <i class="fas fa-info-circle text-blue-500 mt-1"></i>
                <span>${feedback}</span>
            </div>`
        ).join('');
        
    } catch (error) {
        console.error('Erreur:', error);
        showNotification(error.message || 'Erreur lors de la validation', 'error');
    } finally {
        setLoading(button, false);
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg ${
        type === 'error' ? 'bg-red-500' : 'bg-green-500'
    } text-white z-50 animate-fade-in`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${type === 'error' ? 'times' : 'check'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Ajout des nouvelles fonctions pour le hash
function switchHashTab(tab) {
    const textSection = document.getElementById('hashTextSection');
    const fileSection = document.getElementById('hashFileSection');
    const textTab = document.getElementById('hashTabText');
    const fileTab = document.getElementById('hashTabFile');
    
    if (tab === 'text') {
        textSection.classList.remove('hidden');
        fileSection.classList.add('hidden');
        textTab.classList.add('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        textTab.classList.remove('text-gray-600', 'dark:text-gray-300');
        fileTab.classList.remove('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        fileTab.classList.add('text-gray-600', 'dark:text-gray-300');
    } else {
        textSection.classList.add('hidden');
        fileSection.classList.remove('hidden');
        fileTab.classList.add('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        fileTab.classList.remove('text-gray-600', 'dark:text-gray-300');
        textTab.classList.remove('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        textTab.classList.add('text-gray-600', 'dark:text-gray-300');
    }
    
    // Réinitialiser le résultat
    document.getElementById('hashResult').value = '';
}

// Amélioration de l'affichage du nom de fichier
document.getElementById('fileToHash').addEventListener('change', function(e) {
    const fileNameContainer = document.getElementById('selectedFileName');
    if (e.target.files[0]) {
        const fileName = e.target.files[0].name;
        const fileSize = (e.target.files[0].size / 1024).toFixed(1);
        fileNameContainer.innerHTML = `
            <i class="fas fa-file-alt text-purple-500"></i>
            <span class="font-medium">${fileName}</span>
            <span class="text-gray-400">(${fileSize} KB)</span>
            <button onclick="clearSelectedFile()" 
                    class="ml-2 text-gray-400 hover:text-red-500 transition-colors">
                <i class="fas fa-times"></i>
            </button>
        `;
    } else {
        fileNameContainer.innerHTML = `
            <i class="fas fa-file text-gray-400"></i>
            <span>Aucun fichier sélectionné</span>
        `;
    }
});

function clearSelectedFile() {
    const fileInput = document.getElementById('fileToHash');
    fileInput.value = '';
    document.getElementById('selectedFileName').innerHTML = `
        <i class="fas fa-file text-gray-400"></i>
        <span>Aucun fichier sélectionné</span>
    `;
}

async function calculateHash() {
    const algorithm = document.getElementById('hashAlgorithm').value;
    const isFileMode = document.getElementById('hashFileSection').classList.contains('hidden') === false;
    const button = document.querySelector('button[onclick="calculateHash()"]');
    
    setLoading(button, true);
    
    try {
        let response;
        if (isFileMode) {
            const file = document.getElementById('fileToHash').files[0];
            if (!file) {
                throw new Error('Veuillez sélectionner un fichier');
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('algorithm', algorithm);
            
            response = await fetch('/essentials/calculate-hash-file', {
                method: 'POST',
                body: formData
            });
        } else {
            const text = document.getElementById('textToHash').value;
            if (!text) {
                throw new Error('Veuillez entrer du texte à hasher');
            }
            
            response = await fetch('/essentials/calculate-hash', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, algorithm })
            });
        }
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        document.getElementById('hashResult').value = data.hash;
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

function clearHash() {
    document.getElementById('textToHash').value = '';
    document.getElementById('fileToHash').value = '';
    document.getElementById('selectedFileName').textContent = '';
    document.getElementById('hashResult').value = '';
}

function switchBase64Tab(tab) {
    const textSection = document.getElementById('base64TextSection');
    const fileSection = document.getElementById('base64FileSection');
    const textTab = document.getElementById('base64TabText');
    const fileTab = document.getElementById('base64TabFile');
    const downloadButton = document.getElementById('downloadBase64Button');
    
    if (tab === 'text') {
        textSection.classList.remove('hidden');
        fileSection.classList.add('hidden');
        textTab.classList.add('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        textTab.classList.remove('text-gray-600', 'dark:text-gray-300');
        fileTab.classList.remove('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        fileTab.classList.add('text-gray-600', 'dark:text-gray-300');
        downloadButton.classList.add('hidden');
    } else {
        textSection.classList.add('hidden');
        fileSection.classList.remove('hidden');
        fileTab.classList.add('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        fileTab.classList.remove('text-gray-600', 'dark:text-gray-300');
        textTab.classList.remove('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        textTab.classList.add('text-gray-600', 'dark:text-gray-300');
    }
    
    clearBase64();
}

function clearBase64() {
    document.getElementById('base64Input').value = '';
    document.getElementById('fileToBase64').value = '';
    document.getElementById('base64Result').value = '';
    document.getElementById('base64FileName').innerHTML = `
        <i class="fas fa-file text-gray-400"></i>
        <span>Aucun fichier sélectionné</span>
    `;
    document.getElementById('downloadBase64Button').classList.add('hidden');
}

// Ajout d'un event listener pour le fichier
document.getElementById('fileToBase64').addEventListener('change', function(e) {
    const fileNameContainer = document.getElementById('base64FileName');
    if (e.target.files[0]) {
        const fileName = e.target.files[0].name;
        const fileSize = (e.target.files[0].size / 1024).toFixed(1);
        fileNameContainer.innerHTML = `
            <i class="fas fa-file-alt text-blue-500"></i>
            <span class="font-medium">${fileName}</span>
            <span class="text-gray-400">(${fileSize} KB)</span>
            <button onclick="clearBase64()" 
                    class="ml-2 text-gray-400 hover:text-red-500 transition-colors">
                <i class="fas fa-times"></i>
            </button>
        `;
    } else {
        fileNameContainer.innerHTML = `
            <i class="fas fa-file text-gray-400"></i>
            <span>Aucun fichier sélectionné</span>
        `;
    }
});

function downloadBase64Result() {
    const base64Content = document.getElementById('base64Result').value;
    if (!base64Content) return;

    const link = document.createElement('a');
    link.href = 'data:application/octet-stream;base64,' + base64Content;
    link.download = 'fichier_base64.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Ajout des nouvelles fonctions pour le JSON
function switchJsonTab(tab) {
    const textSection = document.getElementById('jsonTextSection');
    const fileSection = document.getElementById('jsonFileSection');
    const textTab = document.getElementById('jsonTabText');
    const fileTab = document.getElementById('jsonTabFile');
    const downloadButton = document.getElementById('downloadJsonButton');
    
    if (tab === 'text') {
        textSection.classList.remove('hidden');
        fileSection.classList.add('hidden');
        textTab.classList.add('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        textTab.classList.remove('text-gray-600', 'dark:text-gray-300');
        fileTab.classList.remove('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        fileTab.classList.add('text-gray-600', 'dark:text-gray-300');
        downloadButton.classList.add('hidden');
    } else {
        textSection.classList.add('hidden');
        fileSection.classList.remove('hidden');
        fileTab.classList.add('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        fileTab.classList.remove('text-gray-600', 'dark:text-gray-300');
        textTab.classList.remove('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-gray-900', 'dark:text-white');
        textTab.classList.add('text-gray-600', 'dark:text-gray-300');
    }
    
    clearJson();
}

// Mise à jour des fonctions JSON existantes
async function formatJson() {
    const isFileMode = document.getElementById('jsonFileSection').classList.contains('hidden') === false;
    const button = document.querySelector('button[onclick="formatJson()"]');
    setLoading(button, true);

    try {
        let response;
        if (isFileMode) {
            const file = document.getElementById('fileToJson').files[0];
            if (!file) {
                throw new Error('Veuillez sélectionner un fichier JSON');
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            response = await fetch('/essentials/format-json-file', {
                method: 'POST',
                body: formData
            });
        } else {
            const input = document.getElementById('jsonInput').value;
            if (!input) {
                throw new Error('Veuillez entrer du JSON');
            }
            
            response = await fetch('/essentials/format-json', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ json: input, indent: 2 })
            });
        }

        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        document.getElementById('jsonResult').value = data.formatted;
        document.getElementById('downloadJsonButton').classList.toggle('hidden', !isFileMode);
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        setLoading(button, false);
    }
}

function clearJson() {
    document.getElementById('jsonInput').value = '';
    document.getElementById('fileToJson').value = '';
    document.getElementById('jsonResult').value = '';
    document.getElementById('jsonFileName').innerHTML = `
        <i class="fas fa-file text-gray-400"></i>
        <span>Aucun fichier sélectionné</span>
    `;
    document.getElementById('downloadJsonButton').classList.add('hidden');
}

document.getElementById('fileToJson').addEventListener('change', function(e) {
    const fileNameContainer = document.getElementById('jsonFileName');
    if (e.target.files[0]) {
        const fileName = e.target.files[0].name;
        const fileSize = (e.target.files[0].size / 1024).toFixed(1);
        fileNameContainer.innerHTML = `
            <i class="fas fa-file-code text-amber-500"></i>
            <span class="font-medium">${fileName}</span>
            <span class="text-gray-400">(${fileSize} KB)</span>
            <button onclick="clearJson()" 
                    class="ml-2 text-gray-400 hover:text-red-500 transition-colors">
                <i class="fas fa-times"></i>
            </button>
        `;
    } else {
        fileNameContainer.innerHTML = `
            <i class="fas fa-file text-gray-400"></i>
            <span>Aucun fichier sélectionné</span>
        `;
    }
});

function downloadJsonResult() {
    const jsonContent = document.getElementById('jsonResult').value;
    if (!jsonContent) return;

    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'formatted.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}