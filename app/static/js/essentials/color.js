(function () {
    'use strict';
    const { debounce, copyToClipboard, notify } = window.ToolUtils;

    const colorEl = document.getElementById('color-base');
    const hexEl = document.getElementById('color-hex');
    const typeEl = document.getElementById('color-type');
    const countEl = document.getElementById('color-count');
    const countLabel = document.querySelector('[data-color-count]');
    const resultsEl = document.getElementById('color-results');

    function hexToRgb(hex) {
        const c = hex.replace('#', '');
        return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)];
    }

    function rgbToHex([r, g, b]) {
        const h = (n) => Math.round(Math.max(0, Math.min(255, n))).toString(16).padStart(2, '0');
        return `#${h(r)}${h(g)}${h(b)}`.toUpperCase();
    }

    function rgbToHsv([r, g, b]) {
        r /= 255; g /= 255; b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        const d = max - min;
        let h = 0;
        if (d) {
            if (max === r) h = ((g - b) / d) % 6;
            else if (max === g) h = (b - r) / d + 2;
            else h = (r - g) / d + 4;
            h = (h * 60 + 360) % 360;
        }
        return [h / 360, max ? d / max : 0, max];
    }

    function hsvToRgb([h, s, v]) {
        const hh = h * 6;
        const i = Math.floor(hh);
        const f = hh - i;
        const p = v * (1 - s);
        const q = v * (1 - f * s);
        const t = v * (1 - (1 - f) * s);
        const cases = [
            [v, t, p], [q, v, p], [p, v, t], [p, q, v], [t, p, v], [v, p, q],
        ];
        return cases[i % 6].map((c) => c * 255);
    }

    function clamp01(n) { return Math.max(0.02, Math.min(1, n)); }

    function monochromatic(hsv, count) {
        const [h, s, v] = hsv;
        const out = [];
        for (let i = 0; i < count; i += 1) {
            const ratio = count === 1 ? 0 : (i - (count - 1) / 2) / count;
            out.push([h, clamp01(s + ratio * 0.4), clamp01(v + ratio * 0.3)]);
        }
        return out;
    }

    function analogous(hsv, count) {
        const [h, s, v] = hsv;
        const out = [];
        for (let i = 0; i < count; i += 1) {
            const dh = (i - (count - 1) / 2) * (30 / 360);
            out.push([(h + dh + 1) % 1, s, v]);
        }
        return out;
    }

    function complementary(hsv, count) {
        const [h, s, v] = hsv;
        const out = [[h, s, v], [(h + 0.5) % 1, s, v]];
        while (out.length < count) {
            const variant = out.length % 2 === 0 ? h : (h + 0.5) % 1;
            out.push([
                variant,
                clamp01(s - 0.15 * Math.floor(out.length / 2)),
                clamp01(v - 0.08 * Math.floor(out.length / 2)),
            ]);
        }
        return out.slice(0, count);
    }

    function polyadic(hsv, count, n) {
        const [h, s, v] = hsv;
        const step = 1 / n;
        const out = [];
        for (let i = 0; i < count; i += 1) {
            const base = (h + step * (i % n)) % 1;
            const tier = Math.floor(i / n);
            out.push([base, clamp01(s + tier * 0.08), clamp01(v - tier * 0.07)]);
        }
        return out;
    }

    function render() {
        const hex = hexEl.value.trim();
        if (!/^#?[0-9a-fA-F]{6}$/.test(hex)) {
            resultsEl.innerHTML = '<div class="tool-output__placeholder"><span>Couleur hex invalide (#RRGGBB).</span></div>';
            return;
        }
        const base = hex.startsWith('#') ? hex : `#${hex}`;
        colorEl.value = base;
        hexEl.value = base.toUpperCase();

        const rgb = hexToRgb(base);
        const hsv = rgbToHsv(rgb);
        const count = parseInt(countEl.value, 10);
        countLabel.textContent = count;

        let palette;
        switch (typeEl.value) {
            case 'monochromatic': palette = monochromatic(hsv, count); break;
            case 'analogous':     palette = analogous(hsv, count); break;
            case 'complementary': palette = complementary(hsv, count); break;
            case 'triadic':       palette = polyadic(hsv, count, 3); break;
            case 'tetradic':      palette = polyadic(hsv, count, 4); break;
            default:              palette = complementary(hsv, count);
        }

        resultsEl.innerHTML = palette.map((h) => {
            const rgb = hsvToRgb(h);
            const hex = rgbToHex(rgb);
            return `
                <div class="tool-swatch">
                    <div class="tool-swatch__color" style="background:${hex};"></div>
                    <div class="tool-swatch__hex">${hex}<br><span class="tool-field__hint">rgb(${rgb.map((c) => Math.round(c)).join(', ')})</span></div>
                    <button class="tool-btn tool-btn--sm tool-btn--ghost" data-copy-hex="${hex}" aria-label="Copier ${hex}">
                        <i class="fas fa-copy text-xs"></i>
                    </button>
                </div>
            `;
        }).join('');

        resultsEl.querySelectorAll('[data-copy-hex]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const ok = await copyToClipboard(btn.dataset.copyHex);
                notify(ok ? `${btn.dataset.copyHex} copié` : 'Erreur', ok ? 'success' : 'error');
            });
        });
    }

    const debounced = debounce(render, 120);
    colorEl.addEventListener('input', () => { hexEl.value = colorEl.value.toUpperCase(); debounced(); });
    hexEl.addEventListener('input', debounced);
    typeEl.addEventListener('change', render);
    countEl.addEventListener('input', render);

    render();
})();
