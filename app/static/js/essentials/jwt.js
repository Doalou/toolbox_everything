(function () {
    'use strict';
    const { debounce, base64UrlDecode } = window.ToolUtils;

    const inputEl = document.getElementById('jwt-input');
    const headerEl = document.getElementById('jwt-header');
    const payloadEl = document.getElementById('jwt-payload');
    const signatureEl = document.getElementById('jwt-signature');
    const statusEl = document.getElementById('jwt-status');

    function decode(part, label) {
        try {
            const json = base64UrlDecode(part);
            const parsed = JSON.parse(json);
            return JSON.stringify(parsed, null, 2);
        } catch (err) {
            throw new Error(`${label} invalide : ${err.message}`);
        }
    }

    function humanizeTimestamp(ts) {
        if (typeof ts !== 'number') return null;
        const date = new Date(ts * 1000);
        if (Number.isNaN(date.getTime())) return null;
        return date.toISOString();
    }

    function run() {
        const token = inputEl.value.trim();
        if (!token) {
            headerEl.textContent = 'Aucun résultat';
            payloadEl.textContent = 'Aucun résultat';
            signatureEl.textContent = 'Aucun résultat';
            statusEl.textContent = '';
            return;
        }
        const parts = token.split('.');
        if (parts.length !== 3) {
            statusEl.innerHTML = '<span class="tool-badge tool-badge--err">Un JWT doit contenir 3 parties séparées par des points.</span>';
            return;
        }
        try {
            headerEl.textContent = decode(parts[0], 'Header');
            const payloadText = decode(parts[1], 'Payload');
            const payload = JSON.parse(payloadText);

            const notes = [];
            if (payload.exp) {
                const iso = humanizeTimestamp(payload.exp);
                const expired = payload.exp * 1000 < Date.now();
                notes.push(`exp → ${iso}${expired ? ' (expiré)' : ''}`);
            }
            if (payload.iat) notes.push(`iat → ${humanizeTimestamp(payload.iat)}`);
            if (payload.nbf) notes.push(`nbf → ${humanizeTimestamp(payload.nbf)}`);

            payloadEl.textContent = payloadText;
            signatureEl.textContent = parts[2];
            statusEl.innerHTML = notes.length
                ? `<span class="tool-badge tool-badge--ok">Décodé</span> <span class="opacity-70">· ${notes.join(' · ')}</span>`
                : '<span class="tool-badge tool-badge--ok">Décodé</span>';
        } catch (err) {
            statusEl.innerHTML = `<span class="tool-badge tool-badge--err">${err.message}</span>`;
        }
    }

    inputEl.addEventListener('input', debounce(run, 150));
    run();
})();
