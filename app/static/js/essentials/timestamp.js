(function () {
    'use strict';
    const { debounce } = window.ToolUtils;

    const inputEl = document.getElementById('ts-input');
    const nowBtn = document.getElementById('ts-now');
    const msBtn = document.getElementById('ts-ms');
    const fields = {
        unix: document.querySelector('[data-ts-field="unix"]'),
        unix_ms: document.querySelector('[data-ts-field="unix_ms"]'),
        iso: document.querySelector('[data-ts-field="iso"]'),
        utc: document.querySelector('[data-ts-field="utc"]'),
        local: document.querySelector('[data-ts-field="local"]'),
        relative: document.querySelector('[data-ts-field="relative"]'),
    };
    const errorEl = document.getElementById('ts-error');

    function parseValue(raw) {
        const v = raw.trim();
        if (!v) return null;
        if (/^\d{10}$/.test(v)) return new Date(parseInt(v, 10) * 1000);
        if (/^\d{13}$/.test(v)) return new Date(parseInt(v, 10));
        const d = new Date(v);
        return Number.isNaN(d.getTime()) ? null : d;
    }

    function formatRelative(date) {
        const diff = (date.getTime() - Date.now()) / 1000;
        const abs = Math.abs(diff);
        const rtf = new Intl.RelativeTimeFormat('fr', { numeric: 'auto' });
        const units = [
            ['year', 31536000],
            ['month', 2592000],
            ['week', 604800],
            ['day', 86400],
            ['hour', 3600],
            ['minute', 60],
            ['second', 1],
        ];
        for (const [unit, sec] of units) {
            if (abs >= sec || unit === 'second') {
                return rtf.format(Math.round(diff / sec), unit);
            }
        }
        return 'Aucun résultat';
    }

    function render(date) {
        if (!date) {
            Object.values(fields).forEach((f) => { f.textContent = 'Aucun résultat'; });
            errorEl.textContent = '';
            return;
        }
        const ts = date.getTime();
        fields.unix.textContent = String(Math.floor(ts / 1000));
        fields.unix_ms.textContent = String(ts);
        fields.iso.textContent = date.toISOString();
        fields.utc.textContent = date.toUTCString();
        fields.local.textContent = new Intl.DateTimeFormat('fr-FR', {
            dateStyle: 'full',
            timeStyle: 'long',
        }).format(date);
        fields.relative.textContent = formatRelative(date);
        errorEl.textContent = '';
    }

    function run() {
        const raw = inputEl.value;
        if (!raw.trim()) {
            render(null);
            return;
        }
        const date = parseValue(raw);
        if (!date) {
            Object.values(fields).forEach((f) => { f.textContent = 'Aucun résultat'; });
            errorEl.innerHTML = '<span class="tool-badge tool-badge--err">Format non reconnu</span>';
            return;
        }
        render(date);
    }

    inputEl.addEventListener('input', debounce(run, 120));
    nowBtn.addEventListener('click', () => {
        inputEl.value = String(Math.floor(Date.now() / 1000));
        run();
    });
    msBtn.addEventListener('click', () => {
        inputEl.value = String(Date.now());
        run();
    });

    inputEl.value = String(Math.floor(Date.now() / 1000));
    run();
})();
