(function () {
    'use strict';
    const { debounce } = window.ToolUtils;

    const inputEl = document.getElementById('json-input');
    const outputEl = document.getElementById('json-output');
    const statusEl = document.getElementById('json-status');
    const indentEl = document.getElementById('json-indent');
    let op = 'format';

    function analyze(obj, depth = 0) {
        if (obj === null) return { type: 'null', depth };
        if (Array.isArray(obj)) {
            return {
                type: 'array',
                length: obj.length,
                depth,
                items_sample: obj.slice(0, 3).map((v) => analyze(v, depth + 1)),
            };
        }
        if (typeof obj === 'object') {
            return {
                type: 'object',
                keys: Object.keys(obj).length,
                depth,
                properties: Object.fromEntries(
                    Object.entries(obj).map(([k, v]) => [k, analyze(v, depth + 1)]),
                ),
            };
        }
        return { type: typeof obj, depth, value: String(obj).slice(0, 80) };
    }

    function run() {
        const text = inputEl.value.trim();
        if (!text) {
            outputEl.textContent = '';
            statusEl.textContent = '';
            statusEl.className = 'tool-field__hint';
            return;
        }
        try {
            const parsed = JSON.parse(text);
            const indentRaw = indentEl.value;
            const indent = indentRaw === '\\t' ? '\t' : parseInt(indentRaw, 10);

            if (op === 'format') {
                outputEl.textContent = JSON.stringify(parsed, null, indent);
            } else if (op === 'minify') {
                outputEl.textContent = JSON.stringify(parsed);
            } else {
                outputEl.textContent = JSON.stringify(analyze(parsed), null, 2);
            }

            const size = new Blob([text]).size;
            const outSize = new Blob([outputEl.textContent]).size;
            statusEl.innerHTML = `<span class="tool-badge tool-badge--ok">JSON valide</span> <span class="opacity-70">· entrée ${size} o, sortie ${outSize} o</span>`;
        } catch (err) {
            outputEl.textContent = '';
            statusEl.innerHTML = `<span class="tool-badge tool-badge--err">Erreur : ${err.message}</span>`;
        }
    }

    document.querySelectorAll('[data-json-op]').forEach((btn) => {
        btn.addEventListener('click', () => {
            op = btn.dataset.jsonOp;
            document.querySelectorAll('[data-json-op]').forEach((b) => {
                const active = b.dataset.jsonOp === op;
                b.classList.toggle('tool-btn--indigo', active);
                b.classList.toggle('tool-btn--ghost', !active);
                b.setAttribute('aria-selected', String(active));
            });
            run();
        });
    });

    inputEl.addEventListener('input', debounce(run, 150));
    indentEl.addEventListener('change', run);
})();
