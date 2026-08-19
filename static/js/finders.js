/**
 * ==========================================================================
 * ACCESSPATH - SCHOLARSHIP & SUMMER PROGRAM FINDER ENGINE
 * Interactive search engines for disability scholarships, state tuition waivers,
 * and high school pre-college summer programs.
 * ==========================================================================
 */

const SCHOLARSHIPS_DATABASE = [
  {
    title: "Texas Vocational Rehabilitation Tuition Waiver",
    amount: "100% Tuition & Fees",
    state: "Texas",
    disability: "blind",
    major: "all",
    description: "Covers full tuition, mandatory fees, and textbook allowances at state universities in Texas (including UT Dallas, UT Austin, A&M)."
  },
  {
    title: "NFB (National Federation of the Blind) Scholarship",
    amount: "$3,000 - $12,000",
    state: "All",
    disability: "blind",
    major: "all",
    description: "Annual national scholarships awarded to legally blind high school seniors and college students based on academic merit and community leadership."
  },
  {
    title: "Alexander Graham Bell Association Scholarship",
    amount: "$2,500 - $10,000",
    state: "All",
    disability: "deaf",
    major: "all",
    description: "Scholarships for deaf and hard-of-hearing students pursuing undergraduate or graduate degrees."
  },
  {
    title: "AFB (American Foundation for the Blind) STEM Scholarship",
    amount: "$5,000",
    state: "All",
    disability: "low-vision",
    major: "stem",
    description: "Dedicated scholarship for blind or low-vision students majoring in Computer Science, Engineering, Math, or Natural Sciences."
  }
];

const SUMMER_PROGRAMS_DATABASE = [
  {
    title: "NASA STEM Internship Program for Disabled High Schoolers",
    location: "Virtual & On-Site",
    disability: "all",
    focus: "STEM / Space",
    description: "Paid summer internships providing mentorship, accessible lab setups, and hands-on space science research."
  },
  {
    title: "NFB STEM Academy for Blind High School Students",
    location: "Baltimore, MD",
    disability: "blind",
    focus: "Engineering / Robotics",
    description: "1-week immersive engineering and computer programming summer camp utilizing tactile graphics and non-visual techniques."
  },
  {
    title: "Gallaudet Pre-College Summer Academy",
    location: "Washington, D.C.",
    disability: "deaf",
    focus: "Leadership & Tech",
    description: "Summer enrichment program for deaf and hard-of-hearing high schoolers exploring computer science and deaf leadership."
  }
];

class FindersEngine {
  filterScholarships(state = 'all', disability = 'all', major = 'all') {
    return SCHOLARSHIPS_DATABASE.filter(s => {
      const matchState = state === 'all' || s.state.toLowerCase() === state.toLowerCase();
      const matchDisability = disability === 'all' || s.disability === 'all' || s.disability === disability;
      const matchMajor = major === 'all' || s.major === 'all' || s.major === major;
      return matchState && matchDisability && matchMajor;
    });
  }

  filterSummerPrograms(disability = 'all') {
    return SUMMER_PROGRAMS_DATABASE.filter(p => {
      return disability === 'all' || p.disability === 'all' || p.disability === disability;
    });
  }

  renderScholarships(containerId, list) {
    const el = document.getElementById(containerId);
    if (!el) return;

    if (list.length === 0) {
      el.innerHTML = `<p style="padding: 1rem; color: var(--text-secondary);">No scholarships matched your filters.</p>`;
      return;
    }

    el.innerHTML = list.map(s => `
      <div class="control-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap;">
          <div>
            <h4>${s.title}</h4>
            <span style="color: var(--accent-secondary); font-weight: bold;">State: ${s.state} | Targeted Disability: ${s.disability.toUpperCase()}</span>
          </div>
          <span class="score-pill" style="font-size: 1.1rem; background: var(--accent-color);">${s.amount}</span>
        </div>
        <p style="color: var(--text-secondary); margin-top: 0.75rem; line-height: 1.5;">${s.description}</p>
      </div>
    `).join('');
  }

  renderSummerPrograms(containerId, list) {
    const el = document.getElementById(containerId);
    if (!el) return;

    el.innerHTML = list.map(p => `
      <div class="control-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap;">
          <div>
            <h4>${p.title}</h4>
            <span style="color: var(--accent-tertiary); font-weight: bold;">📍 Location: ${p.location} | Focus: ${p.focus}</span>
          </div>
          <span class="preset-badge">Pre-College</span>
        </div>
        <p style="color: var(--text-secondary); margin-top: 0.75rem; line-height: 1.5;">${p.description}</p>
      </div>
    `).join('');
  }
}

window.findersEngine = new FindersEngine();
