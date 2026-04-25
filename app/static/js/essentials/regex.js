(function () {
    'use strict';
    const { debounce } = window.ToolUtils;

    const patternEl = document.getElementById('re-pattern');
    const flagsEl = document.getElementById('re-flags');
    const textEl = document.getElementById('re-text');
    const highlightEl = document.getElementById('re-highlight');
    const detailsEl = document.getElementById('re-details');
    const statusEl = document.getElementById('re-status');

    function escapeHtml(s) {
        return s.replace(/[&<>"']/g, (c) => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
        }[c]));
    }

    function run() {
        const pattern = patternEl.value;
        const flags = flagsEl.value.trim();
        const text = textEl.value;

        if (!pattern) {
            highlightEl.innerHTML = escapeHtml(text);
            detailsEl.textContent = 'Aucun résultat';
            statusEl.textContent = '';
            return;
        }

        let re;
        try {
            re = new RegExp(pattern, flags);
        } catch (err) {
            highlightEl.innerHTML = escapeHtml(text);
            detailsEl.textContent = '';
            statusEl.innerHTML = `<span class="tool-badge tool-badge--err">Regex invalide : ${err.message}</span>`;
            return;
        }

        const global = re.flags.includes('g');
        const matches = [];
        if (global) {
            let m;
            while ((m = re.exec(text)) !== null) {
                if (m[0] === '' && re.lastIndex === m.index) {
                    re.lastIndex += 1;
                }
                matches.push({ match: m[0], index: m.index, groups: m.slice(1) });
            }
        } else {
            const m = re.exec(text);
            if (m) matches.push({ match: m[0], index: m.index, groups: m.slice(1) });
        }

        if (matches.length === 0) {
            highlightEl.innerHTML = escapeHtml(text) || '<span class="opacity-60">(aucun texte)</span>';
            detailsEl.textContent = '';
            statusEl.innerHTML = '<span class="tool-badge tool-badge--warn">Aucune correspondance</span>';
            return;
        }

        let html = '';
        let cursor = 0;
        matches.forEach((m) => {
            html += escapeHtml(text.slice(cursor, m.index));
            html += `<span class="tool-regex-match">${escapeHtml(m.match)}</span>`;
            cursor = m.index + m.match.length;
        });
        html += escapeHtml(text.slice(cursor));
        highlightEl.innerHTML = html;

        detailsEl.textContent = matches
            .map((m, i) => {
                let line = `#${i + 1} @ ${m.index}: "${m.match}"`;
                if (m.groups.length) {
                    m.groups.forEach((g, gi) => {
                        line += `\n  groupe ${gi + 1}: ${g === undefined ? '(undefined)' : `"${g}"`}`;
                    });
                }
                return line;
            })
            .join('\n\n');
        statusEl.innerHTML = `<span class="tool-badge tool-badge--ok">${matches.length} correspondance${matches.length > 1 ? 's' : ''}</span>`;
    }

    const debounced = debounce(run, 120);
    [patternEl, flagsEl, textEl].forEach((el) => el.addEventListener('input', debounced));
    run();
})();
