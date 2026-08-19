/**
 * ==========================================================================
 * ACCESSPATH - MAIN APPLICATION CONTROLLER
 * Connects all platform modules: College Database, AI Advisor, Configurator,
 * Resources, Research Reports, Community Reviews, and Scholarship Finders.
 * ==========================================================================
 */

class AccessPathAppController {
  constructor() {
    this.currentProfile = {
      preset: 'blind-jaws',
      theme: 'high-contrast-dark',
      speechRate: 1.0,
      speechPitch: 1.0,
      fontScale: 1.0,
      fontFamily: 'base',
      dyslexicFont: false,
      contrastFocus: true,
      soundFlash: true,
      autoCaptions: true
    };

    this.initElements();
    this.initTabNavigation();
    this.initCollegeDatabase();
    this.initAiAssistant();
    this.initResourcesAndResearch();
    this.initFinders();
    this.initAccessibilityControls();
    this.initSandboxIframe();
  }

  initElements() {
    // Quick toolbar
    this.btnToggleSpeech = document.getElementById('btn-toggle-speech');
    this.btnToggleViewer = document.getElementById('btn-toggle-viewer');
    this.quickThemeSelect = document.getElementById('quick-theme-select');

    // Controls
    this.selectVoice = document.getElementById('select-voice');
    this.rangeSpeechRate = document.getElementById('range-speech-rate');
    this.valSpeechRate = document.getElementById('val-speech-rate');
    this.rangeFontScale = document.getElementById('range-font-scale');
    this.valFontScale = document.getElementById('val-font-scale');
    this.chkDyslexicFont = document.getElementById('chk-dyslexic-font');
    this.btnTestSoundAlert = document.getElementById('btn-test-sound-alert');

    // Sandbox Simulator
    this.sandboxIframe = document.getElementById('sandbox-iframe');
    this.btnRunDomRepair = document.getElementById('btn-run-dom-repair');
    this.repairLogPanel = document.getElementById('repair-log-panel');
    this.repairLogContent = document.getElementById('repair-log-content');
  }

  /**
   * Accessible Multi-Tab Navigation
   */
  initTabNavigation() {
    this.tabs = Array.from(document.querySelectorAll('.nav-link'));
    this.panels = Array.from(document.querySelectorAll('.section-panel'));

    this.tabs.forEach((tab, index) => {
      tab.addEventListener('click', (e) => {
        e.preventDefault();
        this.activateTab(index);
      });

      tab.addEventListener('keydown', (e) => {
        let nextIndex = null;
        if (e.key === 'ArrowRight') {
          nextIndex = index < this.tabs.length - 1 ? index + 1 : 0;
        } else if (e.key === 'ArrowLeft') {
          nextIndex = index > 0 ? index - 1 : this.tabs.length - 1;
        }

        if (nextIndex !== null) {
          e.preventDefault();
          this.tabs[nextIndex].focus();
          this.activateTab(nextIndex);
        }
      });
    });

    // Home Hero Action Triggers
    document.getElementById('hero-btn-colleges')?.addEventListener('click', () => this.activateTab(1));
    document.getElementById('hero-btn-ai')?.addEventListener('click', () => this.activateTab(3));
    document.getElementById('hero-btn-tools')?.addEventListener('click', () => this.activateTab(2));

    document.querySelectorAll('.btn-nav-trigger').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const targetIdx = parseInt(e.currentTarget.getAttribute('data-target'));
        if (!isNaN(targetIdx)) this.activateTab(targetIdx);
      });
    });
  }

  activateTab(activeIndex) {
    this.tabs.forEach((t, i) => {
      const isSelected = i === activeIndex;
      t.classList.toggle('active', isSelected);
      t.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      t.setAttribute('tabindex', isSelected ? '0' : '-1');

      if (this.panels[i]) {
        this.panels[i].style.display = isSelected ? 'block' : 'none';
      }
    });

    if (window.jawsEngine) {
      window.jawsEngine.speak(`Switched to ${this.tabs[activeIndex].innerText.replace(/^[^\w\s]+/, '').trim()}`);
    }
  }

  /**
   * Module 2: College Database Rendering & Search
   */
  initCollegeDatabase() {
    const searchInput = document.getElementById('input-search-college');
    const filterSelect = document.getElementById('select-filter-college');

    const updateTable = () => {
      const query = searchInput ? searchInput.value : '';
      const category = filterSelect ? filterSelect.value : 'all';
      const filtered = window.collegeDbEngine.filterColleges(query, category);
      window.collegeDbEngine.renderTable('college-table-container', filtered);
    };

    if (searchInput) searchInput.addEventListener('input', updateTable);
    if (filterSelect) filterSelect.addEventListener('change', updateTable);

    // Initial render
    updateTable();
  }

  /**
   * Module 4: AI Assistant Advisor Chat Logic
   */
  initAiAssistant() {
    const chatInput = document.getElementById('input-chat');
    const sendBtn = document.getElementById('btn-send-chat');
    const historyContainer = document.getElementById('chat-history');

    const appendBubble = (sender, text) => {
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ${sender}`;
      bubble.innerHTML = text;
      historyContainer.appendChild(bubble);
      historyContainer.scrollTop = historyContainer.scrollHeight;
    };

    const appendTypingIndicator = () => {
      const bubble = document.createElement('div');
      bubble.id = 'chat-typing-indicator';
      bubble.className = `chat-bubble ai`;
      bubble.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;
      historyContainer.appendChild(bubble);
      historyContainer.scrollTop = historyContainer.scrollHeight;
    };

    const removeTypingIndicator = () => {
      const indicator = document.getElementById('chat-typing-indicator');
      if (indicator) indicator.remove();
    };

    const appendSecurityPrompt = (data) => {
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ai security-halt-bubble`;
      bubble.innerHTML = `
        <div class="security-halt-card" style="border: 2px solid var(--danger-color); padding: 15px; border-radius: var(--border-radius); background: var(--bg-tertiary); margin-top: 10px;">
          <h4 style="color: var(--accent-secondary); margin-bottom: 8px; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
            <span aria-hidden="true">🛡️</span> Security Halt: Action Required
          </h4>
          <p style="margin-bottom: 10px; font-size: 0.95rem; color: var(--text-primary);">${data.reason}</p>
          <div class="command-preview" style="background: #000; border: 1px solid var(--border-color); padding: 10px; border-radius: 4px; margin-bottom: 12px; font-family: monospace; overflow-x: auto; color: #ff3366;">
            <code>${data.command}</code>
          </div>
          <div class="security-actions" style="display: flex; gap: 10px;">
            <button class="primary-btn btn-approve-command" type="button" style="padding: 8px 16px; font-size: 0.95rem; background: var(--accent-tertiary); color: #000; border: none; font-weight: bold; border-radius: 4px; cursor: pointer;">Approve</button>
            <button class="tool-btn btn-reject-command" type="button" style="padding: 8px 16px; font-size: 0.95rem; background: var(--danger-color); color: #fff; border: none; font-weight: bold; border-radius: 4px; cursor: pointer;">Reject</button>
          </div>
        </div>
      `;
      historyContainer.appendChild(bubble);
      historyContainer.scrollTop = historyContainer.scrollHeight;

      bubble.querySelector('.btn-approve-command').addEventListener('click', () => {
        bubble.querySelector('.security-actions').style.display = 'none';
        appendTypingIndicator();
        window.aiAssistantEngine.approveCommand(data.tool_call_id, data.command, appendBubble, removeTypingIndicator, appendSecurityPrompt);
      });

      bubble.querySelector('.btn-reject-command').addEventListener('click', () => {
        bubble.querySelector('.security-actions').style.display = 'none';
        appendTypingIndicator();
        window.aiAssistantEngine.rejectCommand(data.tool_call_id, appendBubble, removeTypingIndicator, appendSecurityPrompt);
      });
    };

    const handleSend = () => {
      const query = chatInput ? chatInput.value : '';
      if (!query.trim()) return;

      if (chatInput) chatInput.value = '';
      appendBubble('user', query);
      appendTypingIndicator();

      window.aiAssistantEngine.askQuestionAsync(query, appendBubble, removeTypingIndicator, appendSecurityPrompt);
    };

    if (sendBtn) sendBtn.addEventListener('click', () => handleSend());
    if (chatInput) {
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleSend();
        }
      });
    }

    // Prompt Chips
    document.querySelectorAll('.chip-btn').forEach(chip => {
      chip.addEventListener('click', (e) => {
        const prompt = e.currentTarget.getAttribute('data-prompt');
        if (chatInput) chatInput.value = prompt;
        handleSend();
      });
    });
  }

  /**
   * Modules 5, 6, 7: Resources, Research & Community
   */
  initResourcesAndResearch() {
    window.resourcesResearchEngine.renderResources('resources-container');
    window.resourcesResearchEngine.renderResearch('research-container');
    window.resourcesResearchEngine.renderCommunity('community-container');
  }

  /**
   * Module 8: Finders (Scholarships & Summer Programs)
   */
  initFinders() {
    const filterState = document.getElementById('filter-scholarship-state');
    const filterDisability = document.getElementById('filter-scholarship-disability');

    const updateFinders = () => {
      const state = filterState ? filterState.value : 'all';
      const disability = filterDisability ? filterDisability.value : 'all';

      const scholarships = window.findersEngine.filterScholarships(state, disability, 'all');
      window.findersEngine.renderScholarships('scholarships-results-container', scholarships);

      const summerPrograms = window.findersEngine.filterSummerPrograms(disability);
      window.findersEngine.renderSummerPrograms('summer-programs-results-container', summerPrograms);
    };

    if (filterState) filterState.addEventListener('change', updateFinders);
    if (filterDisability) filterDisability.addEventListener('change', updateFinders);

    updateFinders();
  }

  /**
   * Accessibility Controls & Preset Handlers
   */
  initAccessibilityControls() {
    this.btnToggleSpeech?.addEventListener('click', () => {
      const enabled = window.jawsEngine.toggleSpeech();
      this.btnToggleSpeech.setAttribute('aria-pressed', enabled ? 'true' : 'false');
      this.btnToggleSpeech.innerHTML = `<span aria-hidden="true">🔊</span> Speech Reader: <strong>${enabled ? 'ON' : 'MUTED'}</strong>`;
    });

    this.btnToggleViewer?.addEventListener('click', () => {
      const active = window.jawsEngine.toggleSpeechViewer();
      this.btnToggleViewer.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    document.getElementById('btn-close-speech-viewer')?.addEventListener('click', () => {
      window.jawsEngine.toggleSpeechViewer();
      this.btnToggleViewer?.setAttribute('aria-pressed', 'false');
    });

    this.quickThemeSelect?.addEventListener('change', (e) => {
      document.body.setAttribute('data-theme', e.target.value);
      if (window.jawsEngine) window.jawsEngine.speak(`Theme set to ${e.target.value.replace(/-/g, ' ')}`);
    });

    // Preset cards
    document.querySelectorAll('.preset-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('.preset-card').forEach(c => {
          c.classList.remove('active');
          c.setAttribute('aria-checked', 'false');
        });
        card.classList.add('active');
        card.setAttribute('aria-checked', 'true');

        const presetKey = card.getAttribute('data-preset');
        if (presetKey === 'blind-jaws') {
          document.body.setAttribute('data-theme', 'high-contrast-dark');
          if (window.jawsEngine) window.jawsEngine.speak('Blind and JAWS screen reader preset applied.');
        } else if (presetKey === 'deaf-hearing') {
          document.body.setAttribute('data-theme', 'high-contrast-light');
          if (window.jawsEngine) window.jawsEngine.speak('Deaf and Hard-of-Hearing preset applied with visual sound alerts.');
        } else if (presetKey === 'deafblind') {
          document.body.setAttribute('data-theme', 'deafblind-mono');
          if (window.jawsEngine) window.jawsEngine.speak('Deafblind Monochromatic preset applied.');
        } else if (presetKey === 'low-vision') {
          document.body.setAttribute('data-theme', 'yellow-on-black');
          if (window.jawsEngine) window.jawsEngine.speak('Low Vision 200% font scaling preset applied.');
        }
      });
    });

    this.rangeSpeechRate?.addEventListener('input', (e) => {
      const val = e.target.value;
      if (this.valSpeechRate) this.valSpeechRate.textContent = `${val}x`;
      if (window.jawsEngine) window.jawsEngine.setSpeechRate(val);
    });

    this.rangeFontScale?.addEventListener('input', (e) => {
      const val = e.target.value;
      const pct = Math.round(val * 100);
      if (this.valFontScale) this.valFontScale.textContent = `${pct}%`;
      document.documentElement.style.setProperty('--font-scale', val);
    });

    this.chkDyslexicFont?.addEventListener('change', (e) => {
      const checked = e.target.checked;
      document.documentElement.style.setProperty('--active-font', checked ? 'var(--font-family-dyslexic)' : 'var(--font-family-base)');
      if (window.jawsEngine) window.jawsEngine.speak(checked ? 'Dyslexic font enabled' : 'Standard font enabled');
    });

    this.btnTestSoundAlert?.addEventListener('click', () => {
      if (window.simulatorEngine) window.simulatorEngine.triggerVisualSoundAlert("Simulated Sound Event: 🔔 Alarm Chime");
    });

    this.btnRunDomRepair?.addEventListener('click', () => {
      if (!this.sandboxIframe) return;
      const iframeDoc = this.sandboxIframe.contentDocument || this.sandboxIframe.contentWindow.document;
      const result = window.simulatorEngine.repairInaccessibleDocument(iframeDoc);

      if (this.repairLogPanel) this.repairLogPanel.style.display = 'block';
      if (this.repairLogContent) {
        this.repairLogContent.textContent = `Scanned Sandbox Page:\n- Fixed ${result.repairedCount} accessibility violations.\n\nFix Log:\n` + result.fixes.map(f => ` • ${f}`).join('\n');
      }

      if (window.jawsEngine) window.jawsEngine.speak(`AI DOM Auto-Repair complete. Fixed ${result.repairedCount} items.`);
    });
  }

  initSandboxIframe() {
    if (!this.sandboxIframe) return;
    const iframeDoc = this.sandboxIframe.contentDocument || this.sandboxIframe.contentWindow.document;
    const htmlContent = window.simulatorEngine.getSampleInaccessibleHtml();

    iframeDoc.open();
    iframeDoc.write(htmlContent);
    iframeDoc.close();

    setTimeout(() => {
      const audio = iframeDoc.getElementById('demo-audio');
      if (audio && window.simulatorEngine) {
        window.simulatorEngine.attachMediaCaptionSimulator(audio);
      }
    }, 500);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.accessPathApp = new AccessPathAppController();
});
