(function () {
    'use strict';
    const { copyToClipboard, notify, bytesToHex } = window.ToolUtils;

    const countEl = document.getElementById('uuid-count');
    const countLabel = document.querySelector('[data-uuid-count]');
    const upperEl = document.getElementById('uuid-upper');
    const noDashEl = document.getElementById('uuid-no-dash');
    const regenBtn = document.getElementById('uuid-regen');
    const copyAllBtn = document.getElementById('uuid-copy-all');
    const resultsEl = document.getElementById('uuid-results');
    let version = 'v4';

    function uuidV4() {
        const bytes = new Uint8Array(16);
        crypto.getRandomValues(bytes);
        bytes[6] = (bytes[6] & 0x0f) | 0x40;
        bytes[8] = (bytes[8] & 0x3f) | 0x80;
        const hex = bytesToHex(bytes);
        return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
    }

    function uuidV7() {
        const bytes = new Uint8Array(16);
        crypto.getRandomValues(bytes);
        const ts = BigInt(Date.now());
        bytes[0] = Number((ts >> 40n) & 0xffn);
        bytes[1] = Number((ts >> 32n) & 0xffn);
        bytes[2] = Number((ts >> 24n) & 0xffn);
        bytes[3] = Number((ts >> 16n) & 0xffn);
        bytes[4] = Number((ts >> 8n) & 0xffn);
        bytes[5] = Number(ts & 0xffn);
        bytes[6] = (bytes[6] & 0x0f) | 0x70;
        bytes[8] = (bytes[8] & 0x3f) | 0x80;
        const hex = bytesToHex(bytes);
        return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
    }

    function format(raw) {
        let u = raw;
        if (upperEl.checked) u = u.toUpperCase();
        if (noDashEl.checked) u = u.replace(/-/g, '');
        return u;
    }

    function render() {
        const count = parseInt(countEl.value, 10);
        countLabel.textContent = count;
        const gen = version === 'v4' ? uuidV4 : uuidV7;
        const uuids = Array.from({ length: count }, () => format(gen()));
        resultsEl.innerHTML = uuids.map((u) => `
            <div class="tool-output__row">
                <code>${u}</code>
                <button class="tool-btn tool-btn--sm tool-btn--ghost" data-copy-uuid="${u}" aria-label="Copier">
                    <i class="fas fa-copy text-xs"></i>
                </button>
            </div>
        `).join('');
        resultsEl.querySelectorAll('[data-copy-uuid]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const ok = await copyToClipboard(btn.dataset.copyUuid);
                notify(ok ? 'Copié' : 'Erreur', ok ? 'success' : 'error');
            });
        });
    }

    document.querySelectorAll('[data-uuid-ver]').forEach((btn) => {
        btn.addEventListener('click', () => {
            version = btn.dataset.uuidVer;
            document.querySelectorAll('[data-uuid-ver]').forEach((b) => {
                const active = b.dataset.uuidVer === version;
                b.classList.toggle('tool-btn--indigo', active);
                b.classList.toggle('tool-btn--ghost', !active);
                b.setAttribute('aria-selected', String(active));
            });
            render();
        });
    });

    [countEl, upperEl, noDashEl].forEach((el) => el.addEventListener('input', render));
    regenBtn.addEventListener('click', render);
    copyAllBtn.addEventListener('click', async () => {
        const all = Array.from(resultsEl.querySelectorAll('code')).map((c) => c.textContent).join('\n');
        const ok = await copyToClipboard(all);
        notify(ok ? 'Tous les UUID copiés' : 'Erreur', ok ? 'success' : 'error');
    });

    render();
})();
