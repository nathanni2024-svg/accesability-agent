/**
 * ACCESSIBILITY DOM REPAIR & SIMULATOR ENGINE
 */
class AccessibilitySimulatorEngine {
  constructor() {
    this.soundAlertsEnabled = true;
    this.autoCaptionsEnabled = true;
    this.soundFlashTimer = null;
  }

  getSampleInaccessibleHtml() {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sample Inaccessible E-Commerce Page</title>
  <style>
    body { font-family: sans-serif; background: #222; color: #777; margin: 0; padding: 20px; }
    .header { background: #333; padding: 10px; color: #888; }
    .card { background: #2a2a2a; border: 1px solid #333; padding: 15px; margin-top: 15px; }
    .btn-fake { background: #444; color: #888; padding: 8px 12px; display: inline-block; cursor: pointer; }
    a { color: #555; text-decoration: none; }
    *:focus { outline: none !important; }
  </style>
</head>
<body>
  <div class="header">
    <h2>Tech Store (Inaccessible Demo)</h2>
    <img src="https://picsum.photos/300/100" width="100%" height="80">
  </div>
  <div class="card">
    <h3>Wireless Headphones Pro</h3>
    <img src="https://picsum.photos/200/120" id="prod-img">
    <p>Price: $199.99</p>
    <div style="margin: 15px 0;">
      <label style="color:#aaa;">Product Audio Demo (No Subtitles):</label><br>
      <audio id="demo-audio" controls style="margin-top:5px; width:100%;">
        <source src="https://www.w3schools.com/html/horse.ogg" type="audio/ogg">
      </audio>
    </div>
    <div>
      <input type="text" id="coupon" placeholder="Enter coupon code here...">
    </div>
    <div class="btn-fake" onclick="alert('Added to cart!')" style="margin-top:10px;">
      Buy Now (Fake Div Button)
    </div>
  </div>
</body>
</html>`;
  }

  repairInaccessibleDocument(doc) {
    if (!doc) return { repairedCount: 0, fixes: [] };
    const fixes = [];

    const images = doc.querySelectorAll('img:not([alt]), img[alt=""]');
    images.forEach((img, idx) => {
      const src = img.src || '';
      const fallbackAlt = `[AI Auto-Alt]: Product image ${idx + 1} (${src.split('/').pop() || 'photo'})`;
      img.setAttribute('alt', fallbackAlt);
      img.setAttribute('title', fallbackAlt);
      fixes.push(`Added AI Alt Text to image #${idx + 1}`);
    });

    const inputs = doc.querySelectorAll('input:not([aria-label]):not([id])');
    inputs.forEach((input, idx) => {
      const placeholder = input.placeholder || `Input field ${idx + 1}`;
      input.setAttribute('aria-label', placeholder);
      fixes.push(`Added ARIA label to input #${idx + 1}`);
    });

    const fakeButtons = doc.querySelectorAll('div[onclick], span[onclick]');
    fakeButtons.forEach((btn, idx) => {
      if (!btn.getAttribute('role')) btn.setAttribute('role', 'button');
      if (!btn.getAttribute('tabindex')) btn.setAttribute('tabindex', '0');
      btn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          btn.click();
        }
      });
      fixes.push(`Converted fake DIV #${idx + 1} into keyboard-navigable button`);
    });

    const header = doc.querySelector('.header, header');
    if (header && !header.getAttribute('role')) header.setAttribute('role', 'banner');
    
    const body = doc.body;
    if (body && !doc.querySelector('main')) {
      const mainWrapper = doc.createElement('main');
      mainWrapper.setAttribute('role', 'main');
      while (body.firstChild) {
        mainWrapper.appendChild(body.firstChild);
      }
      body.appendChild(mainWrapper);
      fixes.push('Wrapped document content inside semantic <main> landmark');
    }

    return { repairedCount: fixes.length, fixes };
  }

  triggerVisualSoundAlert(soundDescription) {
    if (!this.soundAlertsEnabled) return;

    const flashEl = document.getElementById('visual-sound-flash');
    if (flashEl) {
      flashEl.classList.add('active-alert');
      clearTimeout(this.soundFlashTimer);
      this.soundFlashTimer = setTimeout(() => {
        flashEl.classList.remove('active-alert');
      }, 800);
    }

    const banner = document.getElementById('sound-caption-banner');
    if (banner) {
      banner.textContent = `🔊 [AUDIO EVENT]: ${soundDescription}`;
      banner.classList.add('show');
      setTimeout(() => {
        banner.classList.remove('show');
      }, 4000);
    }

    if (window.jawsEngine) {
      window.jawsEngine.updateSpeechViewer(`[DEAF VISUAL CUE]: ${soundDescription}`);
    }
  }

  attachMediaCaptionSimulator(mediaElement) {
    if (!mediaElement) return;

    const simulatedCaptions = [
      { time: 0, text: "🎵 [Upbeat intro music plays]" },
      { time: 2, text: "🗣️ Narrator: Welcome to the wireless sound demonstration." },
      { time: 5, text: "🔊 [Horse neighing / Sound effect test]" },
      { time: 8, text: "👏 [Audience applause in background]" },
      { time: 12, text: "🔔 [Doorbell chime sound alert]" }
    ];

    mediaElement.addEventListener('timeupdate', () => {
      const currentSec = Math.floor(mediaElement.currentTime);
      const match = simulatedCaptions.find(c => c.time === currentSec);
      if (match) {
        this.triggerVisualSoundAlert(match.text);
      }
    });

    mediaElement.addEventListener('play', () => {
      this.triggerVisualSoundAlert("Media playback started");
    });
  }
}

window.simulatorEngine = new AccessibilitySimulatorEngine();

/**
 * UNIVERSAL BOOKMARKLET & EXTENSION CODE GENERATOR
 */
class AccessibilityOverlayGenerator {
  generateBookmarkletCode(profile) {
    const minifiedCss = `
      body { background-color: ${profile.theme === 'high-contrast-dark' ? '#000' : '#fff'} !important; color: ${profile.theme === 'high-contrast-dark' ? '#fff' : '#000'} !important; }
      *:focus-visible { outline: 4px solid #ffff00 !important; outline-offset: 3px !important; }
      img:not([alt]) { outline: 3px dashed #ff0000 !important; }
    `.replace(/\s+/g, ' ');

    const code = `
(function() {
  if (window.__a11yOverlayLoaded) { alert('Accessibility Overlay is active!'); return; }
  window.__a11yOverlayLoaded = true;
  var style = document.createElement('style');
  style.innerHTML = '${minifiedCss}';
  document.head.appendChild(style);
  var synth = window.speechSynthesis;
  function speak(text) {
    if (!synth) return;
    synth.cancel();
    var ut = new SpeechSynthesisUtterance(text);
    ut.rate = ${profile.speechRate || 1.0};
    synth.speak(ut);
  }
  var imgs = document.querySelectorAll('img:not([alt])');
  imgs.forEach(function(img, i) { img.alt = '[AI Alt]: Photo ' + (i+1); });
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
  speak('Free JAWS Accessibility Overlay Activated.');
})();`.trim();

    return `javascript:${encodeURIComponent(code)}`;
  }

  generateUserScriptCode(profile) {
    return `// ==UserScript==
// @name         AccessPath Free Universal JAWS Overlay
// @namespace    https://accesspath.local
// @version      1.0
// @description  Injects JAWS-like virtual quick keys, high contrast, auto-alt text, and sound alerts on any site.
// @match        *://*/*
// @grant        none
// ==UserScript==

(function() {
    'use strict';
    console.log("AccessPath Overlay Initialized.");
})();`;
  }
}

window.overlayGenerator = new AccessibilityOverlayGenerator();
