(function () {
    'use strict';
    const { debounce, base64Encode, base64Decode } = window.ToolUtils;

    const inputEl = document.getElementById('b64-input');
    const outputEl = document.getElementById('b64-output');
    const urlsafeEl = document.getElementById('b64-urlsafe');
    let mode = 'encode';

    function run() {
        const value = inputEl.value;
        if (!value) {
            outputEl.value = '';
            return;
        }
        try {
            if (mode === 'encode') {
                let out = base64Encode(value);
                if (urlsafeEl.checked) {
                    out = out.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
                }
                outputEl.value = out;
            } else {
                let payload = value.trim();
                if (urlsafeEl.checked) {
                    payload = payload.replace(/-/g, '+').replace(/_/g, '/');
                    const pad = '='.repeat((4 - (payload.length % 4)) % 4);
                    payload += pad;
                }
                outputEl.value = base64Decode(payload);
            }
        } catch (err) {
            outputEl.value = `Erreur : ${err.message}`;
        }
    }

    document.querySelectorAll('[data-b64-mode]').forEach((btn) => {
        btn.addEventListener('click', () => {
            mode = btn.dataset.b64Mode;
            document.querySelectorAll('[data-b64-mode]').forEach((b) => {
                const active = b.dataset.b64Mode === mode;
                b.classList.toggle('tool-btn--indigo', active);
                b.classList.toggle('tool-btn--ghost', !active);
                b.setAttribute('aria-selected', String(active));
            });
            run();
        });
    });

    inputEl.addEventListener('input', debounce(run, 150));
    urlsafeEl.addEventListener('change', run);
})();
