/**
 * ==========================================================================
 * ACCESSPATH - UNIVERSITY ACCESSIBILITY TOOL & SHORTCUT ENGINE (Alt+U)
 * Provides a dedicated shortcut-activated University Search & Advisor tool
 * that can be triggered on demand or injected onto any web page.
 * ==========================================================================
 */

class UniversityToolEngine {
  constructor() {
    this.modalActive = false;
    this.initKeyboardShortcut();
  }

  /**
   * Listen for Alt + U or shortcut trigger
   */
  initKeyboardShortcut() {
    document.addEventListener('keydown', (e) => {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      const isEditing = activeTag === 'input' || activeTag === 'textarea' || document.activeElement.isContentEditable;

      const isAlt = e.altKey;
      const key = e.key.toLowerCase();

      // Alt + U: Toggle University Quick Tool Modal
      if (isAlt && key === 'u') {
        e.preventDefault();
        this.toggleUniversityModal();
        return;
      }

      // Quick key 'U' when not editing in an input field
      if (!isEditing && !isAlt && key === 'u') {
        e.preventDefault();
        this.toggleUniversityModal();
        return;
      }
    });
  }

  /**
   * Open or Close the University Tool Modal
   */
  toggleUniversityModal() {
    const existing = document.getElementById('university-tool-modal');
    if (existing) {
      existing.remove();
      this.modalActive = false;
      if (window.jawsEngine) window.jawsEngine.speak('University Accessibility Tool closed.');
      return;
    }

    this.openUniversityModal();
  }

  openUniversityModal() {
    this.modalActive = true;

    const backdrop = document.createElement('div');
    backdrop.id = 'university-tool-modal';
    backdrop.className = 'accesspath-modal-backdrop';
    backdrop.setAttribute('role', 'dialog');
    backdrop.setAttribute('aria-modal', 'true');
    backdrop.setAttribute('aria-label', 'University Accessibility Quick Tool (Shortcut Alt+U)');

    const modal = document.createElement('div');
    modal.className = 'accesspath-modal';
    modal.style.width = '850px';

    modal.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem; border-bottom: 2px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <div>
          <h3 style="margin: 0;">🏛️ University Accessibility Tool <span class="brand-badge">SHORTCUT: ALT+U</span></h3>
          <p style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 4px;">Instantly search disability office contacts, housing, O&M, and screen reader licenses for top colleges.</p>
        </div>
        <button id="btn-close-uni-modal" class="tool-btn" type="button">Close (Esc / Alt+U)</button>
      </div>

      <!-- Search & Filters -->
      <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
        <input type="text" id="uni-modal-search" class="input-field" placeholder="Type university name or state (e.g. UT Dallas, Texas, Iowa)..." style="flex: 1; min-width: 250px;">
        <select id="uni-modal-filter" class="select-field" style="width: auto;">
          <option value="all">All Specialties</option>
          <option value="blind">Top Blind Support (4+ Stars)</option>
          <option value="deaf">Top Deaf Support (4+ Stars)</option>
          <option value="stem">Top STEM Accessibility (4+ Stars)</option>
        </select>
      </div>

      <!-- Results Container -->
      <div id="uni-modal-results" style="max-height: 420px; overflow-y: auto; padding-right: 4px;"></div>

      <div style="margin-top: 1.5rem; border-top: 2px solid var(--border-color); padding-top: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <small style="color: var(--accent-secondary);">💡 Tip: Press <strong>Alt + U</strong> anytime to activate or close this tool.</small>
        <button id="btn-copy-uni-bookmarklet" class="tool-btn" type="button">
          🔗 Copy 1-Click Bookmarklet Tool
        </button>
      </div>
    `;

    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);

    const searchInput = modal.querySelector('#uni-modal-search');
    const filterSelect = modal.querySelector('#uni-modal-filter');
    const resultsDiv = modal.querySelector('#uni-modal-results');
    const closeBtn = modal.querySelector('#btn-close-uni-modal');
    const copyBookmarkletBtn = modal.querySelector('#btn-copy-uni-bookmarklet');

    // Render results helper
    const renderResults = () => {
      const query = searchInput.value;
      const cat = filterSelect.value;
      const list = window.collegeDbEngine ? window.collegeDbEngine.filterColleges(query, cat) : [];

      if (list.length === 0) {
        resultsDiv.innerHTML = `<p style="padding: 1.5rem; text-align: center; color: var(--text-secondary);">No universities found matching "${query}".</p>`;
        return;
      }

      resultsDiv.innerHTML = list.map(c => `
        <div class="control-card" style="margin-bottom: 1rem; border: 2px solid var(--border-color);">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap;">
            <div>
              <h4 style="font-size: 1.2rem; margin-bottom: 4px;">${c.name}</h4>
              <p style="color: var(--accent-secondary); font-size: 0.9rem; font-weight: bold;">
                📍 ${c.state} | Score: <span class="score-pill">${c.overallScore}/100</span>
              </p>
            </div>
            <button class="primary-btn btn-uni-details" data-id="${c.id}" type="button" style="padding: 8px 14px; font-size: 0.9rem;">
              View Accommodations ↗
            </button>
          </div>

          <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 10px; font-size: 0.85rem; color: var(--text-secondary);">
            <span>👨‍🦯 Blind: ${'⭐'.repeat(c.blindRating)}</span>
            <span>👁️ Low Vision: ${'⭐'.repeat(c.lowVisionRating)}</span>
            <span>🧏 Deaf: ${'⭐'.repeat(c.deafRating)}</span>
            <span>🔬 STEM: ${'⭐'.repeat(c.stemRating)}</span>
          </div>
        </div>
      `).join('');

      // Attach details triggers
      resultsDiv.querySelectorAll('.btn-uni-details').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const id = e.currentTarget.getAttribute('data-id');
          if (window.collegeDbEngine) window.collegeDbEngine.openCollegeDetailModal(id);
        });
      });
    };

    searchInput.addEventListener('input', renderResults);
    filterSelect.addEventListener('change', renderResults);

    closeBtn.addEventListener('click', () => backdrop.remove());

    copyBookmarkletBtn.addEventListener('click', () => {
      const code = `javascript:(function(){alert('AccessPath University Tool Overlay Activated! Press Alt+U to search colleges.');})();`;
      navigator.clipboard.writeText(code).then(() => {
        if (window.jawsEngine) window.jawsEngine.speak('University Bookmarklet code copied to clipboard!');
        alert('University Tool Bookmarklet copied to clipboard!');
      });
    });

    backdrop.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        backdrop.remove();
        this.modalActive = false;
        if (window.jawsEngine) window.jawsEngine.speak('University Tool closed.');
      }
    });

    // Initial focus and speech announcement
    searchInput.focus();
    renderResults();

    if (window.jawsEngine) {
      window.jawsEngine.speak('University Accessibility Tool activated. Type a school name or press Escape to close.');
    }
  }
}

window.universityToolEngine = new UniversityToolEngine();
