(function () {
    'use strict';
    const { debounce, downloadBlob, notify } = window.ToolUtils;

    const textEl = document.getElementById('qr-text');
    const sizeEl = document.getElementById('qr-size');
    const sizeLabel = document.querySelector('[data-qr-size-value]');
    const eclEl = document.getElementById('qr-ecl');
    const outEl = document.getElementById('qr-output');
    const actionsEl = document.getElementById('qr-actions');
    const dlPng = document.getElementById('qr-download-png');
    const dlSvg = document.getElementById('qr-download-svg');

    let currentSvg = null;

    function render() {
        const text = textEl.value.trim();
        if (!text) {
            outEl.innerHTML = '<span>Le QR code apparaîtra ici.</span>';
            outEl.className = 'tool-output__placeholder';
            actionsEl.hidden = true;
            return;
        }
        try {
            const qr = qrcode(0, eclEl.value);
            qr.addData(text);
            qr.make();
            const size = parseInt(sizeEl.value, 10);
            const svg = qr.createSvgTag({ cellSize: size, margin: 4 });
            outEl.innerHTML = svg;
            outEl.className = 'flex items-center justify-center p-4';
            currentSvg = outEl.querySelector('svg');
            if (currentSvg) {
                currentSvg.style.maxWidth = '100%';
                currentSvg.style.height = 'auto';
            }
            actionsEl.hidden = false;
        } catch (err) {
            outEl.innerHTML = `<span class="tool-badge tool-badge--err">${err.message}</span>`;
            outEl.className = 'tool-output__placeholder';
            actionsEl.hidden = true;
        }
    }

    const debounced = debounce(render, 150);
    textEl.addEventListener('input', debounced);
    eclEl.addEventListener('change', render);
    sizeEl.addEventListener('input', () => {
        sizeLabel.textContent = `${sizeEl.value} px`;
        debounced();
    });

    dlSvg.addEventListener('click', () => {
        if (!currentSvg) return;
        const xml = new XMLSerializer().serializeToString(currentSvg);
        downloadBlob(new Blob([xml], { type: 'image/svg+xml' }), 'qrcode.svg');
        notify('QR code téléchargé (SVG)', 'success');
    });

    dlPng.addEventListener('click', () => {
        if (!currentSvg) return;
        const xml = new XMLSerializer().serializeToString(currentSvg);
        const img = new Image();
        const svgBlob = new Blob([xml], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(svgBlob);
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width * 2;
            canvas.height = img.height * 2;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#fff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            canvas.toBlob((blob) => {
                if (blob) {
                    downloadBlob(blob, 'qrcode.png');
                    notify('QR code téléchargé (PNG)', 'success');
                }
                URL.revokeObjectURL(url);
            }, 'image/png');
        };
        img.src = url;
    });

    render();
})();
