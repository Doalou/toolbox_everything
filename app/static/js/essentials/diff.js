(function () {
    'use strict';
    const { debounce } = window.ToolUtils;

    const aEl = document.getElementById('diff-a');
    const bEl = document.getElementById('diff-b');
    const trimEl = document.getElementById('diff-trim');
    const outEl = document.getElementById('diff-output');
    const statusEl = document.getElementById('diff-status');

    function escapeHtml(s) {
        return s.replace(/[&<>"']/g, (c) => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
        }[c]));
    }

    // LCS (Longest Common Subsequence) basique. OK pour des textes raisonnables.
    function diffLines(a, b) {
        const n = a.length;
        const m = b.length;
        const lcs = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
        for (let i = 1; i <= n; i += 1) {
            for (let j = 1; j <= m; j += 1) {
                if (a[i - 1] === b[j - 1]) {
                    lcs[i][j] = lcs[i - 1][j - 1] + 1;
                } else {
                    lcs[i][j] = Math.max(lcs[i - 1][j], lcs[i][j - 1]);
                }
            }
        }

        const result = [];
        let i = n;
        let j = m;
        while (i > 0 && j > 0) {
            if (a[i - 1] === b[j - 1]) {
                result.unshift({ type: 'eq', value: a[i - 1] });
                i -= 1; j -= 1;
            } else if (lcs[i - 1][j] >= lcs[i][j - 1]) {
                result.unshift({ type: 'del', value: a[i - 1] });
                i -= 1;
            } else {
                result.unshift({ type: 'add', value: b[j - 1] });
                j -= 1;
            }
        }
        while (i > 0) { result.unshift({ type: 'del', value: a[i - 1] }); i -= 1; }
        while (j > 0) { result.unshift({ type: 'add', value: b[j - 1] }); j -= 1; }
        return result;
    }

    function run() {
        const normalize = (text) => {
            let lines = text.split('\n');
            if (trimEl.checked) lines = lines.map((l) => l.trim());
            return lines;
        };

        const a = normalize(aEl.value);
        const b = normalize(bEl.value);

        if (!aEl.value && !bEl.value) {
            outEl.innerHTML = '<div class="tool-output__placeholder"><span>Collez deux textes pour voir leurs différences.</span></div>';
            statusEl.textContent = '';
            return;
        }

        const diff = diffLines(a, b);
        let added = 0;
        let deleted = 0;
        outEl.innerHTML = diff.map((d) => {
            if (d.type === 'add') { added += 1; return `<div class="tool-diff__line tool-diff__line--add">+ ${escapeHtml(d.value) || '&nbsp;'}</div>`; }
            if (d.type === 'del') { deleted += 1; return `<div class="tool-diff__line tool-diff__line--del">- ${escapeHtml(d.value) || '&nbsp;'}</div>`; }
            return `<div class="tool-diff__line">&nbsp; ${escapeHtml(d.value) || '&nbsp;'}</div>`;
        }).join('');

        if (added === 0 && deleted === 0) {
            statusEl.innerHTML = '<span class="tool-badge tool-badge--ok">Textes identiques</span>';
        } else {
            statusEl.innerHTML = `<span class="tool-badge tool-badge--ok">+${added}</span> <span class="tool-badge tool-badge--err">-${deleted}</span>`;
        }
    }

    const debounced = debounce(run, 200);
    [aEl, bEl, trimEl].forEach((el) => el.addEventListener('input', debounced));
    run();
})();
