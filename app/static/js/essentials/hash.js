(function () {
    'use strict';
    const { debounce, bytesToHex, copyToClipboard, notify } = window.ToolUtils;

    const ALGOS = [
        { id: 'SHA-1', label: 'SHA-1' },
        { id: 'SHA-256', label: 'SHA-256' },
        { id: 'SHA-384', label: 'SHA-384' },
        { id: 'SHA-512', label: 'SHA-512' },
    ];

    const inputEl = document.getElementById('hash-input');
    const formatEl = document.getElementById('hash-format');
    const resultsEl = document.getElementById('hash-results');

    function bytesToBase64(bytes) {
        let binary = '';
        bytes.forEach((b) => { binary += String.fromCharCode(b); });
        return btoa(binary);
    }

    function renderSkeleton() {
        resultsEl.innerHTML = ALGOS.map((a) => `
            <div class="tool-output__row">
                <span class="tool-output__label">${a.label}</span>
                <code data-hash-of="${a.id}">Aucun résultat</code>
                <button class="tool-btn tool-btn--sm tool-btn--ghost" data-hash-copy="${a.id}" aria-label="Copier ${a.label}">
                    <i class="fas fa-copy text-xs"></i>
                </button>
            </div>
        `).join('');

        resultsEl.querySelectorAll('[data-hash-copy]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const target = resultsEl.querySelector(`[data-hash-of="${btn.dataset.hashCopy}"]`);
                if (!target) return;
                const ok = await copyToClipboard(target.textContent);
                notify(ok ? 'Hash copié' : 'Impossible de copier', ok ? 'success' : 'error');
            });
        });
    }

    async function compute() {
        const text = inputEl.value;
        const format = formatEl.value;
        if (!text) {
            ALGOS.forEach((a) => {
                const el = resultsEl.querySelector(`[data-hash-of="${a.id}"]`);
                if (el) el.textContent = 'Aucun résultat';
            });
            return;
        }
        const bytes = new TextEncoder().encode(text);
        await Promise.all(ALGOS.map(async (a) => {
            try {
                const digest = await crypto.subtle.digest(a.id, bytes);
                const arr = new Uint8Array(digest);
                const el = resultsEl.querySelector(`[data-hash-of="${a.id}"]`);
                if (el) el.textContent = format === 'hex' ? bytesToHex(arr) : bytesToBase64(arr);
            } catch (err) {
                const el = resultsEl.querySelector(`[data-hash-of="${a.id}"]`);
                if (el) el.textContent = `Erreur : ${err.message}`;
            }
        }));
    }

    renderSkeleton();
    inputEl.addEventListener('input', debounce(compute, 150));
    formatEl.addEventListener('change', compute);
})();
