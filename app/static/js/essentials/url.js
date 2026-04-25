(function () {
    'use strict';
    const { debounce } = window.ToolUtils;

    const inputEl = document.getElementById('url-input');
    const outputEl = document.getElementById('url-output');
    let op = 'encode';

    function run() {
        const value = inputEl.value;
        if (!value) {
            outputEl.value = '';
            return;
        }
        try {
            outputEl.value = op === 'encode' ? encodeURIComponent(value) : decodeURIComponent(value);
        } catch (err) {
            outputEl.value = `Erreur : ${err.message}`;
        }
    }

    document.querySelectorAll('[data-url-op]').forEach((btn) => {
        btn.addEventListener('click', () => {
            op = btn.dataset.urlOp;
            document.querySelectorAll('[data-url-op]').forEach((b) => {
                const active = b.dataset.urlOp === op;
                b.classList.toggle('tool-btn--indigo', active);
                b.classList.toggle('tool-btn--ghost', !active);
                b.setAttribute('aria-selected', String(active));
            });
            run();
        });
    });

    inputEl.addEventListener('input', debounce(run, 120));
})();
