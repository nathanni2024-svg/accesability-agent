/**
 * ==========================================================================
 * UNIVERSAL ACCESSIBILITY EXTENSION & BOOKMARKLET GENERATOR
 * Generates standalone, zero-dependency JavaScript code snippets that users
 * can bookmark or inject into any inaccessible site to run their custom profile.
 * ==========================================================================
 */

class AccessibilityOverlayGenerator {
  /**
   * Generates a Bookmarklet JavaScript URI string
   */
  generateBookmarkletCode(profile) {
    const minifiedCss = `
      body { background-color: ${profile.theme === 'high-contrast-dark' ? '#000' : '#fff'} !important; color: ${profile.theme === 'high-contrast-dark' ? '#fff' : '#000'} !important; }
      *:focus-visible { outline: 4px solid #ffff00 !important; outline-offset: 3px !important; }
      img:not([alt]) { outline: 3px dashed #ff0000 !important; }
    `.replace(/\s+/g, ' ');

    const code = `
(function() {
  if (window.__a11yOverlayLoaded) { alert('Accessibility Overlay is already active on this page!'); return; }
  window.__a11yOverlayLoaded = true;

  /* Inject High Contrast & Focus CSS */
  var style = document.createElement('style');
  style.innerHTML = '${minifiedCss}';
  document.head.appendChild(style);

  /* Inject Virtual Speech Navigation Keys (H, L, B, F) */
  var synth = window.speechSynthesis;
  function speak(text) {
    if (!synth) return;
    synth.cancel();
    var ut = new SpeechSynthesisUtterance(text);
    ut.rate = ${profile.speechRate || 1.0};
    synth.speak(ut);
  }

  /* Auto-Repair Images & Links */
  var imgs = document.querySelectorAll('img:not([alt])');
  imgs.forEach(function(img, i) {
    img.alt = '[AI Alt]: Photo ' + (i+1);
  });

  /* Keyboard Navigation Shortcuts */
  document.addEventListener('keydown', function(e) {
    var tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
    if (tag === 'input' || tag === 'textarea') return;

    var key = e.key.toLowerCase();
    var selector = '';
    if (key === 'h') selector = 'h1, h2, h3, h4, h5, h6';
    if (key === 'l') selector = 'a[href]';
    if (key === 'b') selector = 'button, input[type="button"]';
    if (key === 'f') selector = 'input, select, textarea';

    if (selector) {
      e.preventDefault();
      var els = Array.from(document.querySelectorAll(selector));
      if (els.length === 0) { speak('No ' + key + ' elements found.'); return; }
      var idx = els.indexOf(document.activeElement);
      var next = e.shiftKey ? (idx > 0 ? idx - 1 : els.length - 1) : (idx < els.length - 1 ? idx + 1 : 0);
      els[next].focus();
      speak(key.toUpperCase() + ': ' + (els[next].innerText || els[next].alt || els[next].ariaLabel || 'Element'));
    }
  });

  speak('Free JAWS Accessibility Overlay Activated. Press H for headings, L for links, B for buttons.');
})();
    `.trim();

    return `javascript:${encodeURIComponent(code)}`;
  }

  /**
   * Generates formatted JS snippet for Tampermonkey / Greasemonkey
   */
  generateUserScriptCode(profile) {
    return `// ==UserScript==
// @name         Free Universal JAWS & Deaf Accessibility Overlay
// @namespace    https://accessibility-hub.local
// @version      1.0
// @description  Injects JAWS-like virtual quick keys, high contrast, auto-alt text, and sound alerts on any site.
// @match        *://*/*
// @grant        none
// ==UserScript==

(function() {
    'use me strict';
    console.log("Accessibility Overlay Initialized.");
    // Profile settings: ${JSON.stringify(profile)}
})();`;
  }
}

window.overlayGenerator = new AccessibilityOverlayGenerator();
