/**
 * Helpers partagés par tous les outils essentials.
 * Expose `window.ToolUtils` pour éviter les imports ES modules côté static.
 */
(function () {
    'use strict';

    function debounce(fn, wait = 200) {
        let timer;
        return function debounced(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), wait);
        };
    }

    async function copyToClipboard(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            }
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            return true;
        } catch (err) {
            console.error('Copy failed:', err);
            return false;
        }
    }

    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    function downloadText(text, filename, mime = 'text/plain') {
        downloadBlob(new Blob([text], { type: mime }), filename);
    }

    function notify(message, type = 'info', duration = 2500) {
        const container = document.getElementById('notifications');
        if (!container) {
            return;
        }
        const toast = document.createElement('div');
        toast.className = `tool-toast tool-toast--${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('is-visible'));
        setTimeout(() => {
            toast.classList.remove('is-visible');
            setTimeout(() => toast.remove(), 200);
        }, duration);
    }

    /**
     * Branche un bouton "copier" sur une cible (input/textarea/élément texte).
     * Usage : <button data-copy-target="#outputField">Copier</button>
     */
    function bindCopyButtons(root = document) {
        root.querySelectorAll('[data-copy-target]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const selector = btn.getAttribute('data-copy-target');
                const target = document.querySelector(selector);
                if (!target) return;
                const text = 'value' in target ? target.value : target.textContent;
                const ok = await copyToClipboard(text || '');
                notify(ok ? 'Copié !' : 'Impossible de copier', ok ? 'success' : 'error');
            });
        });
    }

    /**
     * Relie un input (avec [data-tool-source]) à une fonction de calcul et écrit
     * le résultat dans [data-tool-sink]. Debounced à 200ms.
     */
    function wireInstantTool({ source, sink, compute, onError, wait = 200, trigger = 'input' }) {
        const sourceEl = typeof source === 'string' ? document.querySelector(source) : source;
        const sinkEl = typeof sink === 'string' ? document.querySelector(sink) : sink;
        if (!sourceEl || !sinkEl) {
            console.warn('wireInstantTool: source/sink manquant', { source, sink });
            return;
        }

        const run = async () => {
            try {
                const result = await compute(sourceEl.value, { source: sourceEl, sink: sinkEl });
                if (result !== undefined) {
                    if ('value' in sinkEl) {
                        sinkEl.value = result;
                    } else {
                        sinkEl.textContent = result;
                    }
                }
            } catch (err) {
                if (onError) {
                    onError(err, { source: sourceEl, sink: sinkEl });
                } else {
                    console.error(err);
                }
            }
        };

        const debounced = debounce(run, wait);
        sourceEl.addEventListener(trigger, debounced);
        return run;
    }

    function bytesToHex(bytes) {
        return Array.from(bytes)
            .map((b) => b.toString(16).padStart(2, '0'))
            .join('');
    }

    function hexToBytes(hex) {
        const clean = hex.replace(/[^0-9a-fA-F]/g, '');
        const out = new Uint8Array(clean.length / 2);
        for (let i = 0; i < out.length; i += 1) {
            out[i] = parseInt(clean.substr(i * 2, 2), 16);
        }
        return out;
    }

    function base64Encode(str) {
        const bytes = new TextEncoder().encode(str);
        let binary = '';
        bytes.forEach((b) => {
            binary += String.fromCharCode(b);
        });
        return btoa(binary);
    }

    function base64Decode(b64) {
        const binary = atob(b64.replace(/\s/g, ''));
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i += 1) {
            bytes[i] = binary.charCodeAt(i);
        }
        return new TextDecoder().decode(bytes);
    }

    function base64UrlDecode(b64url) {
        const pad = '='.repeat((4 - (b64url.length % 4)) % 4);
        return base64Decode(b64url.replace(/-/g, '+').replace(/_/g, '/') + pad);
    }

    document.addEventListener('DOMContentLoaded', () => bindCopyButtons(document));

    window.ToolUtils = {
        debounce,
        copyToClipboard,
        downloadBlob,
        downloadText,
        notify,
        bindCopyButtons,
        wireInstantTool,
        bytesToHex,
        hexToBytes,
        base64Encode,
        base64Decode,
        base64UrlDecode,
    };
})();
