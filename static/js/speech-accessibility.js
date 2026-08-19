/**
 * ==========================================================================
 * FREE IN-BROWSER JAWS-LIKE SCREEN READER & SPEECH ENGINE
 * Provides Virtual Buffer Navigation (H, L, B, F, T, D), Speech Synthesis,
 * Visual Speech Viewer Transcript, and JAWS Element List Dialogs.
 * ==========================================================================
 */

class JawsScreenReaderEngine {
  constructor() {
    this.speechSynth = window.speechSynthesis;
    this.enabled = true;
    this.virtualCursorEnabled = true;
    this.rate = 1.0;
    this.pitch = 1.0;
    this.volume = 1.0;
    this.voice = null;
    this.verbosity = 'intermediate';
    this.speechViewerActive = true;
    this.lastSpokenText = '';
    this.activeDocument = document;
    this.currentNavIndex = -1;
    this.navElements = [];
    this.activeCategory = null;

    this.initVoices();
    this.initListeners();
    this.initAriaLiveRegion();
  }

  initVoices() {
    if (!this.speechSynth) return;
    const loadVoices = () => {
      const voices = this.speechSynth.getVoices();
      if (voices.length > 0) {
        this.voice = voices.find(v => v.lang.startsWith('en') && v.default) || voices[0];
      }
    };
    loadVoices();
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices;
    }
  }

  initAriaLiveRegion() {
    let liveRegion = document.getElementById('jaws-live-announcer');
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.id = 'jaws-live-announcer';
      liveRegion.className = 'sr-only';
      liveRegion.setAttribute('aria-live', 'assertive');
      liveRegion.setAttribute('aria-atomic', 'true');
      document.body.appendChild(liveRegion);
    }
    this.liveRegion = liveRegion;
  }

  setSpeechRate(rate) {
    this.rate = parseFloat(rate);
    this.announce(`Speech rate set to ${this.rate}x`);
  }

  setSpeechPitch(pitch) {
    this.pitch = parseFloat(pitch);
    this.announce(`Speech pitch set to ${this.pitch}`);
  }

  setVoice(voiceName) {
    const voices = this.speechSynth.getVoices();
    const found = voices.find(v => v.name === voiceName);
    if (found) {
      this.voice = found;
      this.announce(`Voice changed to ${found.name}`);
    }
  }

  toggleSpeech() {
    this.enabled = !this.enabled;
    if (!this.enabled && this.speechSynth) {
      this.speechSynth.cancel();
    }
    const status = this.enabled ? 'Screen reader audio enabled' : 'Screen reader audio muted';
    this.updateSpeechViewer(`[SYSTEM] ${status}`);
    this.announce(status);
    return this.enabled;
  }

  toggleSpeechViewer() {
    this.speechViewerActive = !this.speechViewerActive;
    const panel = document.getElementById('jaws-speech-viewer');
    if (panel) {
      panel.style.display = this.speechViewerActive ? 'flex' : 'none';
    }
    this.announce(this.speechViewerActive ? 'Speech viewer visible' : 'Speech viewer hidden');
    return this.speechViewerActive;
  }

  speak(text, interrupt = true) {
    if (!text) return;
    this.lastSpokenText = text;
    this.updateSpeechViewer(text);

    if (this.liveRegion) {
      this.liveRegion.textContent = text;
    }

    if (!this.enabled || !this.speechSynth) return;

    if (interrupt) {
      this.speechSynth.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = this.rate;
    utterance.pitch = this.pitch;
    utterance.volume = this.volume;
    if (this.voice) {
      utterance.voice = this.voice;
    }

    this.speechSynth.speak(utterance);
  }

  announce(text) {
    this.speak(text, true);
  }

  updateSpeechViewer(text) {
    const content = document.getElementById('jaws-speech-content');
    if (content) {
      const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const entry = document.createElement('div');
      entry.textContent = `[${timestamp}] ${text}`;
      content.appendChild(entry);
      content.scrollTop = content.scrollHeight;
    }
  }

  announceElement(el) {
    if (!el || el === document.body) return;

    let text = '';
    const tagName = el.tagName.toLowerCase();
    const role = el.getAttribute('role') || tagName;
    const label = el.getAttribute('aria-label') || el.innerText || el.title || el.alt || el.placeholder || '';
    const state = el.getAttribute('aria-pressed') === 'true' ? 'pressed' : 
                  el.getAttribute('aria-expanded') === 'true' ? 'expanded' : 
                  el.disabled ? 'disabled' : '';

    if (tagName.match(/^h[1-6]$/)) {
      const level = tagName.replace('h', '');
      text = `Heading level ${level}, ${label}`;
    } else if (tagName === 'a') {
      text = `Link, ${label}`;
    } else if (tagName === 'button' || role === 'button') {
      text = `Button, ${label} ${state}`;
    } else if (tagName === 'input') {
      const type = el.type || 'text';
      if (type === 'checkbox') {
        text = `Checkbox ${el.checked ? 'checked' : 'not checked'}, ${label}`;
      } else if (type === 'range') {
        text = `Slider ${label}, value ${el.value}`;
      } else {
        text = `Edit text ${label}, ${el.value}`;
      }
    } else if (tagName === 'select') {
      const selectedOption = el.options[el.selectedIndex]?.text || '';
      text = `Combo box ${label}, selected ${selectedOption}`;
    } else {
      text = `${role}, ${label}`;
    }

    if (this.verbosity === 'beginner' && el.getAttribute('title')) {
      text += `. Hint: ${el.getAttribute('title')}`;
    }

    this.speak(text);
  }

  navigateCategory(category, reverse = false, targetDoc = document) {
    let selector = '';
    switch (category) {
      case 'heading': selector = 'h1, h2, h3, h4, h5, h6, [role="heading"]'; break;
      case 'link': selector = 'a[href], [role="link"]'; break;
      case 'button': selector = 'button, input[type="button"], input[type="submit"], [role="button"]'; break;
      case 'field': selector = 'input, select, textarea, [role="textbox"], [role="slider"]'; break;
      case 'table': selector = 'table, [role="table"]'; break;
      case 'landmark': selector = 'main, nav, header, footer, section, aside, [role="main"], [role="navigation"], [role="banner"]'; break;
      default: return;
    }

    const items = Array.from(targetDoc.querySelectorAll(selector)).filter(el => {
      return el.offsetWidth > 0 && el.offsetHeight > 0 && getComputedStyle(el).visibility !== 'hidden';
    });

    if (items.length === 0) {
      this.speak(`No ${category}s found on page`);
      return;
    }

    const activeEl = targetDoc.activeElement;
    let currentIndex = items.indexOf(activeEl);

    if (reverse) {
      currentIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
    } else {
      currentIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
    }

    const nextEl = items[currentIndex];
    nextEl.focus();
    this.announceElement(nextEl);
  }

  openElementListModal(category, targetDoc = document) {
    let selector = '';
    let title = '';
    switch (category) {
      case 'heading': selector = 'h1, h2, h3, h4, h5, h6'; title = 'JAWS Headings List (Alt+H)'; break;
      case 'link': selector = 'a[href]'; title = 'JAWS Links List (Alt+K)'; break;
      case 'button': selector = 'button, input[type="button"], [role="button"]'; title = 'JAWS Buttons List (Alt+B)'; break;
    }

    const items = Array.from(targetDoc.querySelectorAll(selector));
    if (items.length === 0) {
      this.speak(`No ${category} elements to list.`);
      return;
    }

    const existing = document.getElementById('jaws-element-modal');
    if (existing) existing.remove();

    const backdrop = document.createElement('div');
    backdrop.id = 'jaws-element-modal';
    backdrop.className = 'jaws-modal-backdrop';
    backdrop.setAttribute('role', 'dialog');
    backdrop.setAttribute('aria-modal', 'true');
    backdrop.setAttribute('aria-label', title);

    const modal = document.createElement('div');
    modal.className = 'jaws-modal';

    const h3 = document.createElement('h3');
    h3.textContent = title;

    const ul = document.createElement('ul');
    ul.className = 'jaws-element-list';
    ul.setAttribute('tabindex', '0');

    items.forEach((item, idx) => {
      const li = document.createElement('li');
      li.className = 'jaws-element-item';
      li.setAttribute('tabindex', '0');
      li.textContent = `${idx + 1}. ${item.innerText || item.getAttribute('aria-label') || item.title || 'Unlabeled Element'}`;
      
      const activate = () => {
        backdrop.remove();
        item.focus();
        this.announceElement(item);
      };

      li.addEventListener('click', activate);
      li.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          activate();
        }
      });
      ul.appendChild(li);
    });

    const closeBtn = document.createElement('button');
    closeBtn.className = 'tool-btn';
    closeBtn.textContent = 'Close Dialog (Esc)';
    closeBtn.addEventListener('click', () => backdrop.remove());

    modal.appendChild(h3);
    modal.appendChild(ul);
    modal.appendChild(closeBtn);
    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);

    ul.firstElementChild.focus();
    this.speak(`${title}. Use up and down arrows or Tab to select, Enter to move to element.`);

    backdrop.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        backdrop.remove();
        this.speak('Dialog closed.');
      }
    });
  }

  initListeners() {
    document.addEventListener('focusin', (e) => {
      this.announceElement(e.target);
    });

    document.addEventListener('keydown', (e) => {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      const isEditing = activeTag === 'input' || activeTag === 'textarea' || document.activeElement.isContentEditable;

      if (isEditing) return;

      const isShift = e.shiftKey;
      const isAlt = e.altKey;

      if (isAlt && e.key.toLowerCase() === 'h') { e.preventDefault(); this.openElementListModal('heading'); return; }
      if (isAlt && e.key.toLowerCase() === 'k') { e.preventDefault(); this.openElementListModal('link'); return; }
      if (isAlt && e.key.toLowerCase() === 'b') { e.preventDefault(); this.openElementListModal('button'); return; }
      if (isAlt && e.key.toLowerCase() === 'v') { e.preventDefault(); this.toggleSpeechViewer(); return; }

      switch (e.key.toLowerCase()) {
        case 'h': e.preventDefault(); this.navigateCategory('heading', isShift); break;
        case 'l': e.preventDefault(); this.navigateCategory('link', isShift); break;
        case 'b': e.preventDefault(); this.navigateCategory('button', isShift); break;
        case 'f': e.preventDefault(); this.navigateCategory('field', isShift); break;
        case 't': e.preventDefault(); this.navigateCategory('table', isShift); break;
        case 'd': e.preventDefault(); this.navigateCategory('landmark', isShift); break;
      }
    });
  }
}

window.jawsEngine = new JawsScreenReaderEngine();
