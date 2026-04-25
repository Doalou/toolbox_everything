(function () {
    'use strict';

    const LOWER = 'abcdefghijkmnopqrstuvwxyz';
    const LOWER_ALL = 'abcdefghijklmnopqrstuvwxyz';
    const UPPER = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
    const UPPER_ALL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const NUMS = '23456789';
    const NUMS_ALL = '0123456789';
    const SYMS = '!@#$%^&*()_+-=[]{}|;:,.<>?';

    const WORDS = [
        'alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel',
        'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa',
        'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'whisky', 'xray',
        'yankee', 'zulu', 'aurore', 'bateau', 'cactus', 'dragon', 'etoile', 'falaise',
        'geant', 'horizon', 'iceberg', 'jungle', 'koala', 'lagune', 'mirage', 'neon',
        'ocean', 'planete', 'quartz', 'rocher', 'soleil', 'tempete', 'univers', 'violet',
        'whisper', 'xenon', 'yeti', 'zephyr', 'aimant', 'brume', 'cristal', 'douane',
        'escargot', 'feutre', 'givre', 'huile', 'ivoire', 'jasmin', 'kiosque', 'liane',
    ];

    function pickFrom(str, count = 1) {
        const bytes = new Uint32Array(count);
        crypto.getRandomValues(bytes);
        const result = [];
        for (let i = 0; i < count; i += 1) {
            result.push(str[bytes[i] % str.length]);
        }
        return result;
    }

    function pickOne(arr) {
        const buf = new Uint32Array(1);
        crypto.getRandomValues(buf);
        return arr[buf[0] % arr.length];
    }

    function shuffle(arr) {
        for (let i = arr.length - 1; i > 0; i -= 1) {
            const buf = new Uint32Array(1);
            crypto.getRandomValues(buf);
            const j = buf[0] % (i + 1);
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    }

    function generateRandom(length, opts) {
        const pool = [];
        const required = [];

        const lower = opts.noAmbig ? LOWER : LOWER_ALL;
        const upper = opts.noAmbig ? UPPER : UPPER_ALL;
        const nums = opts.noAmbig ? NUMS : NUMS_ALL;

        if (opts.lower) { pool.push(...lower); required.push(pickOne(lower.split(''))); }
        if (opts.upper) { pool.push(...upper); required.push(pickOne(upper.split(''))); }
        if (opts.numbers) { pool.push(...nums); required.push(pickOne(nums.split(''))); }
        if (opts.symbols) { pool.push(...SYMS); required.push(pickOne(SYMS.split(''))); }

        if (pool.length === 0) {
            throw new Error('Au moins un type de caractère doit être sélectionné');
        }

        const remaining = Math.max(0, length - required.length);
        const chars = required.concat(pickFrom(pool.join(''), remaining));
        return shuffle(chars).join('');
    }

    function generatePassphrase(count, sep, capitalize, addNumber) {
        let words = [];
        for (let i = 0; i < count; i += 1) {
            let w = pickOne(WORDS);
            if (capitalize) w = w.charAt(0).toUpperCase() + w.slice(1);
            words.push(w);
        }
        let result = words.join(sep);
        if (addNumber) {
            const buf = new Uint32Array(1);
            crypto.getRandomValues(buf);
            result += (buf[0] % 90) + 10;
        }
        return result;
    }

    function strengthOf(password) {
        const len = password.length;
        let variety = 0;
        if (/[a-z]/.test(password)) variety += 1;
        if (/[A-Z]/.test(password)) variety += 1;
        if (/[0-9]/.test(password)) variety += 1;
        if (/[^a-zA-Z0-9]/.test(password)) variety += 1;

        let score = 0;
        if (len >= 20) score += 45;
        else if (len >= 16) score += 35;
        else if (len >= 12) score += 25;
        else if (len >= 8) score += 15;
        score += variety * 14;
        if (/(.)\1{2,}/.test(password)) score -= 10;
        score = Math.max(0, Math.min(100, score));

        let level, color, hint;
        if (score >= 85) { level = 'Excellent'; color = '#059669'; hint = 'Très robuste, adapté aux usages critiques.'; }
        else if (score >= 65) { level = 'Fort'; color = '#2563eb'; hint = 'Solide pour la plupart des usages.'; }
        else if (score >= 40) { level = 'Moyen'; color = '#d97706'; hint = 'Augmentez la longueur ou la variété.'; }
        else { level = 'Faible'; color = '#dc2626'; hint = 'Allongez le mot de passe.'; }

        return { score, level, color, hint };
    }

    const lengthEl = document.getElementById('pw-length');
    const lengthLabel = document.querySelector('[data-pw-length-value]');
    const upperEl = document.getElementById('pw-upper');
    const lowerEl = document.getElementById('pw-lower');
    const numbersEl = document.getElementById('pw-numbers');
    const symbolsEl = document.getElementById('pw-symbols');
    const noAmbigEl = document.getElementById('pw-no-ambig');
    const regenBtn = document.getElementById('pw-regen');
    const result = document.getElementById('pw-result');
    const strengthFill = document.getElementById('pw-strength-fill');
    const strengthLevel = document.getElementById('pw-strength-level');
    const strengthHint = document.getElementById('pw-strength-hint');

    const ppWordsEl = document.getElementById('pp-words');
    const ppWordsLabel = document.querySelector('[data-pp-words-value]');
    const ppSepEl = document.getElementById('pp-sep');
    const ppCapEl = document.getElementById('pp-capitalize');
    const ppNumEl = document.getElementById('pp-number');

    let mode = 'random';

    function generate() {
        try {
            let pwd;
            if (mode === 'random') {
                pwd = generateRandom(parseInt(lengthEl.value, 10), {
                    upper: upperEl.checked,
                    lower: lowerEl.checked,
                    numbers: numbersEl.checked,
                    symbols: symbolsEl.checked,
                    noAmbig: noAmbigEl.checked,
                });
            } else {
                pwd = generatePassphrase(
                    parseInt(ppWordsEl.value, 10),
                    ppSepEl.value,
                    ppCapEl.checked,
                    ppNumEl.checked,
                );
            }
            result.textContent = pwd;
            const s = strengthOf(pwd);
            strengthFill.style.width = `${s.score}%`;
            strengthFill.style.background = s.color;
            strengthLevel.textContent = `${s.level} · ${s.score}/100`;
            strengthHint.textContent = s.hint;
        } catch (err) {
            result.textContent = `Erreur : ${err.message}`;
            strengthFill.style.width = '0%';
            strengthLevel.textContent = 'Aucun résultat';
            strengthHint.textContent = '';
        }
    }

    document.querySelectorAll('[data-mode-btn]').forEach((btn) => {
        btn.addEventListener('click', () => {
            mode = btn.dataset.modeBtn;
            document.querySelectorAll('[data-mode-btn]').forEach((b) => {
                const active = b.dataset.modeBtn === mode;
                b.classList.toggle('tool-btn--indigo', active);
                b.classList.toggle('tool-btn--ghost', !active);
                b.setAttribute('aria-selected', String(active));
            });
            document.querySelectorAll('[data-mode-panel]').forEach((p) => {
                p.hidden = p.dataset.modePanel !== mode;
            });
            generate();
        });
    });

    lengthEl.addEventListener('input', () => {
        lengthLabel.textContent = lengthEl.value;
        generate();
    });
    ppWordsEl.addEventListener('input', () => {
        ppWordsLabel.textContent = ppWordsEl.value;
        generate();
    });

    [upperEl, lowerEl, numbersEl, symbolsEl, noAmbigEl, ppSepEl, ppCapEl, ppNumEl].forEach((el) => {
        el.addEventListener('change', generate);
    });
    regenBtn.addEventListener('click', generate);

    generate();
})();
