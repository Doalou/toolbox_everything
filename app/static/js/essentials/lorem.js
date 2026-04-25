(function () {
    'use strict';

    const WORDS = ('lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor ' +
        'incididunt ut labore et dolore magna aliqua enim ad minim veniam quis nostrud ' +
        'exercitation ullamco laboris nisi aliquip ex ea commodo consequat duis aute irure ' +
        'in reprehenderit voluptate velit esse cillum fugiat nulla pariatur excepteur sint ' +
        'occaecat cupidatat non proident sunt culpa qui officia deserunt mollit anim id est ' +
        'laborum neque porro quisquam dolorem adipisci numquam eius modi tempora magnam').split(' ');

    const countEl = document.getElementById('lorem-count');
    const countLabel = document.querySelector('[data-lorem-count]');
    const classicEl = document.getElementById('lorem-classic');
    const regenBtn = document.getElementById('lorem-regen');
    const outputEl = document.getElementById('lorem-output');
    let unit = 'paragraphs';

    function pickWord() {
        const buf = new Uint32Array(1);
        crypto.getRandomValues(buf);
        return WORDS[buf[0] % WORDS.length];
    }

    function makeSentence(wordCount) {
        const words = Array.from({ length: wordCount }, pickWord);
        words[0] = words[0].charAt(0).toUpperCase() + words[0].slice(1);
        return `${words.join(' ')}.`;
    }

    function randomInt(min, max) {
        const buf = new Uint32Array(1);
        crypto.getRandomValues(buf);
        return min + (buf[0] % (max - min + 1));
    }

    function generate() {
        const count = parseInt(countEl.value, 10);
        countLabel.textContent = count;
        let out = '';

        if (unit === 'words') {
            const words = Array.from({ length: count }, pickWord);
            if (classicEl.checked) {
                words.splice(0, Math.min(2, count), 'Lorem', 'ipsum');
            }
            out = words.join(' ');
        } else if (unit === 'sentences') {
            const sentences = Array.from({ length: count }, () => makeSentence(randomInt(5, 14)));
            if (classicEl.checked && sentences.length) {
                sentences[0] = `Lorem ipsum dolor sit amet, ${sentences[0].toLowerCase()}`;
            }
            out = sentences.join(' ');
        } else {
            const paragraphs = Array.from({ length: count }, () => {
                const n = randomInt(3, 6);
                return Array.from({ length: n }, () => makeSentence(randomInt(5, 14))).join(' ');
            });
            if (classicEl.checked && paragraphs.length) {
                paragraphs[0] = `Lorem ipsum dolor sit amet, consectetur adipiscing elit. ${paragraphs[0]}`;
            }
            out = paragraphs.join('\n\n');
        }
        outputEl.textContent = out;
    }

    document.querySelectorAll('[data-lorem-unit]').forEach((btn) => {
        btn.addEventListener('click', () => {
            unit = btn.dataset.loremUnit;
            document.querySelectorAll('[data-lorem-unit]').forEach((b) => {
                const active = b.dataset.loremUnit === unit;
                b.classList.toggle('tool-btn--indigo', active);
                b.classList.toggle('tool-btn--ghost', !active);
                b.setAttribute('aria-selected', String(active));
            });
            generate();
        });
    });

    countEl.addEventListener('input', generate);
    classicEl.addEventListener('change', generate);
    regenBtn.addEventListener('click', generate);
    generate();
})();
