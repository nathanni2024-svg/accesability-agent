/**
 * ==========================================================================
 * ACCESSPATH - COLLEGE ACCESSIBILITY DATABASE ENGINE
 * Authoritative rating database and detailed accommodation profiles for
 * top universities supporting blind, low-vision, and deaf students.
 * ==========================================================================
 */

const COLLEGE_DATABASE = [
  {
    id: "ut-dallas",
    name: "UT Dallas (University of Texas at Dallas)",
    state: "Texas",
    overallScore: 96,
    blindRating: 5,
    lowVisionRating: 4,
    deafRating: 4,
    stemRating: 5,
    scholarshipRating: 4,
    website: "https://www.utdallas.edu",
    office: {
      name: "Access University Office (ARC)",
      contact: "studentaccess@utdallas.edu | (972) 883-2098",
      website: "https://access.utdallas.edu"
    },
    housing: "Single-occupancy rooms available with automatic door openers, strobe-light smoke alarms, and dedicated service animal relief zones.",
    om: "Comprehensive Orientation & Mobility training provided before freshman week; campus features tactile paving and audio crosswalks.",
    screenReader: "Full site licenses for JAWS, NVDA, and ZoomText across all computer labs; high-speed Tactile Braille Embossers in main library.",
    noteTaking: "Complimentary Glean AI note-taking software licenses, CART live captioning for deaf STEM lectures, and quiet testing centers.",
    testing: "Extended time (1.5x - 2.0x), private testing booths, screen reader compatible computer stations."
  },
  {
    id: "grinnell",
    name: "Grinnell College",
    state: "Iowa",
    overallScore: 98,
    blindRating: 5,
    lowVisionRating: 5,
    deafRating: 4,
    stemRating: 4,
    scholarshipRating: 5,
    website: "https://www.grinnell.edu",
    office: {
      name: "Academic Advising & Disability Resources",
      contact: "autrykatie@grinnell.edu | (641) 269-3702",
      website: "https://www.grinnell.edu/academics/resources/disability"
    },
    housing: "100% accessible residence halls with Braille room numbers, customizable desk heights, and visual alert systems.",
    om: "Compact 120-acre walkable campus with 1-on-1 O&M specialist guidance during orientation week.",
    screenReader: "Dedicated Assistive Tech Lab with VoiceOver, JAWS, and Duxbury Braille Translator. Tactile graphics hardware for math and science diagrams.",
    noteTaking: "Peer note-takers, Otter.ai premium transcription, and full digital audio recording allowances.",
    testing: "Scribe assistance, tactile exam diagrams, enlarged 24pt print exams, and flexible scheduling."
  },
  {
    id: "swarthmore",
    name: "Swarthmore College",
    state: "Pennsylvania",
    overallScore: 94,
    blindRating: 4,
    lowVisionRating: 4,
    deafRating: 4,
    stemRating: 5,
    scholarshipRating: 4,
    website: "https://www.swarthmore.edu",
    office: {
      name: "Student Disability Services",
      contact: "studentdisability@swarthmore.edu | (610) 328-8356",
      website: "https://www.swarthmore.edu/student-disability-services"
    },
    housing: "Accessible dorm suites with roll-in showers, visual doorbell alerts, and electronic keyless entry.",
    om: "Guided mobility training for navigate historical stone pathways; audio navigation beacon beacons installed on main quad.",
    screenReader: "Kurzweil 3000, JAWS, Read&Write Gold, and 3D tactile graphics printer for STEM calculus and biology.",
    noteTaking: "Professional CART captioners for deaf students and peer note-taking support.",
    testing: "Reduced distraction testing environment, screen reader testing laptops."
  },
  {
    id: "uc-berkeley",
    name: "UC Berkeley",
    state: "California",
    overallScore: 95,
    blindRating: 5,
    lowVisionRating: 4,
    deafRating: 5,
    stemRating: 5,
    scholarshipRating: 4,
    website: "https://www.berkeley.edu",
    office: {
      name: "Disabled Students' Program (DSP)",
      contact: "dsp@berkeley.edu | (510) 642-0518",
      website: "https://dsp.berkeley.edu"
    },
    housing: "Accessible campus apartments with ASL-fluent resident assistants and tactile building layouts.",
    om: "On-demand wheelchair and O&M campus golf cart transportation service.",
    screenReader: "Print Displacement Center translating all textbooks into accessible Braille and audio formats in under 48 hours.",
    noteTaking: "Real-time remote captioning (TypeWell), ASL interpreters, and AI audio transcription.",
    testing: "Proctored testing center with high-contrast screen magnification monitors."
  },
  {
    id: "gallaudet",
    name: "Gallaudet University",
    state: "Washington, D.C.",
    overallScore: 99,
    blindRating: 4,
    lowVisionRating: 5,
    deafRating: 5,
    stemRating: 4,
    scholarshipRating: 5,
    website: "https://gallaudet.edu",
    office: {
      name: "Office for Students with Disabilities (OSWD)",
      contact: "oswd@gallaudet.edu | (202) 651-5256",
      website: "https://gallaudet.edu/disability-services"
    },
    housing: "DeafSpace architecture designed specifically for visual communication: wide hallways, visual doorbells, 360-degree light sightlines.",
    om: "Fully visual and tactile campus layout with tactile pavement paths.",
    screenReader: "DeafBlind accessibility workstations equipped with refreshable Braille displays and tactile graphics.",
    noteTaking: "Complete bilingual ASL/English note-taking and visual recording infrastructure.",
    testing: "Flexible bilingual visual and tactile testing accommodations."
  }
];

class CollegeDatabaseEngine {
  constructor() {
    this.colleges = COLLEGE_DATABASE;
  }

  filterColleges(query = '', category = 'all') {
    const q = query.toLowerCase().trim();
    return this.colleges.filter(c => {
      const matchName = c.name.toLowerCase().includes(q) || c.state.toLowerCase().includes(q);
      if (!matchName) return false;

      if (category === 'blind') return c.blindRating >= 4;
      if (category === 'deaf') return c.deafRating >= 4;
      if (category === 'stem') return c.stemRating >= 4;
      return true;
    });
  }

  getStarRating(rating) {
    return '⭐'.repeat(rating);
  }

  openCollegeDetailModal(collegeId) {
    const college = this.colleges.find(c => c.id === collegeId);
    if (!college) return;

    const existing = document.getElementById('college-detail-modal');
    if (existing) existing.remove();

    const backdrop = document.createElement('div');
    backdrop.id = 'college-detail-modal';
    backdrop.className = 'accesspath-modal-backdrop';
    backdrop.setAttribute('role', 'dialog');
    backdrop.setAttribute('aria-modal', 'true');
    backdrop.setAttribute('aria-label', `${college.name} Disability & Accessibility Support`);

    const modal = document.createElement('div');
    modal.className = 'accesspath-modal';

    modal.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
        <div>
          <h3>${college.name}</h3>
          <p style="color: var(--accent-secondary); font-weight: bold;">📍 Location: ${college.state} | Overall Accessibility Score: <span class="score-pill">${college.overallScore}/100</span></p>
        </div>
        <button id="btn-close-modal" class="tool-btn" type="button">Close (Esc)</button>
      </div>

      <div style="margin: 1.5rem 0; border-top: 2px solid var(--border-color); border-bottom: 2px solid var(--border-color); padding: 1rem 0;">
        <p><strong>Ratings Breakdown:</strong></p>
        <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 8px;">
          <span>👨‍🦯 Blind Support: ${this.getStarRating(college.blindRating)}</span>
          <span>👁️ Low Vision: ${this.getStarRating(college.lowVisionRating)}</span>
          <span>🧏 Deaf Support: ${this.getStarRating(college.deafRating)}</span>
          <span>🔬 STEM Accessibility: ${this.getStarRating(college.stemRating)}</span>
        </div>
      </div>

      <div class="modal-grid">
        <div class="modal-card">
          <h4>🏢 Accessibility Office</h4>
          <p><strong>Office:</strong> ${college.office.name}</p>
          <p><strong>Contact:</strong> ${college.office.contact}</p>
          <p><a href="${college.office.website}" target="_blank" style="color: var(--accent-color);">Visit Disability Office Website ↗</a></p>
        </div>

        <div class="modal-card">
          <h4>🏠 Housing Accommodations</h4>
          <p>${college.housing}</p>
        </div>

        <div class="modal-card">
          <h4>👨‍🦯 Orientation & Mobility (O&M)</h4>
          <p>${college.om}</p>
        </div>

        <div class="modal-card">
          <h4>🖥️ Screen Reader & Tech Licenses</h4>
          <p>${college.screenReader}</p>
        </div>

        <div class="modal-card">
          <h4>📝 Note-Taking & Captions</h4>
          <p>${college.noteTaking}</p>
        </div>

        <div class="modal-card">
          <h4>⏱️ Testing Accommodations</h4>
          <p>${college.testing}</p>
        </div>
      </div>
    `;

    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);

    const closeBtn = modal.querySelector('#btn-close-modal');
    closeBtn.focus();
    closeBtn.addEventListener('click', () => backdrop.remove());

    backdrop.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        backdrop.remove();
        if (window.jawsEngine) window.jawsEngine.speak('College details dialog closed.');
      }
    });

    if (window.jawsEngine) {
      window.jawsEngine.speak(`Loaded accessibility details for ${college.name}.`);
    }
  }

  renderTable(targetElementId, collegesList) {
    const container = document.getElementById(targetElementId);
    if (!container) return;

    if (collegesList.length === 0) {
      container.innerHTML = `<p style="padding: 1.5rem; text-align: center; color: var(--text-secondary);">No colleges matched your search filter.</p>`;
      return;
    }

    let rowsHtml = collegesList.map(c => `
      <tr>
        <td style="font-weight: bold;">
          <button class="tool-btn btn-view-college" data-id="${c.id}" type="button" style="text-align: left; background: none; border: none; padding: 0; color: var(--accent-color); text-decoration: underline;">
            ${c.name}
          </button>
          <br><small style="color: var(--text-secondary);">${c.state}</small>
        </td>
        <td><span class="score-pill">${c.overallScore}</span></td>
        <td>${this.getStarRating(c.blindRating)}</td>
        <td>${this.getStarRating(c.lowVisionRating)}</td>
        <td>${this.getStarRating(c.deafRating)}</td>
        <td>${this.getStarRating(c.stemRating)}</td>
        <td>
          <button class="primary-btn btn-view-college" data-id="${c.id}" type="button" style="padding: 6px 12px; font-size: 0.85rem;">
            View Office & Housing
          </button>
        </td>
      </tr>
    `).join('');

    container.innerHTML = `
      <div class="table-responsive">
        <table class="data-table" aria-label="College Accessibility Ratings Comparison Table">
          <thead>
            <tr>
              <th>School / University</th>
              <th>Overall Score</th>
              <th>Blind</th>
              <th>Low Vision</th>
              <th>Deaf</th>
              <th>STEM</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      </div>
    `;

    // Attach click handlers
    container.querySelectorAll('.btn-view-college').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        this.openCollegeDetailModal(id);
      });
    });
  }
}

window.collegeDbEngine = new CollegeDatabaseEngine();
