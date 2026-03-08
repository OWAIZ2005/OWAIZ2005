<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Mohamed Basheer — Developer Portfolio</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg: #020408;
    --surface: #080f1a;
    --border: rgba(99,210,255,0.1);
    --glow: #63d2ff;
    --glow2: #a78bfa;
    --glow3: #34d399;
    --text: #e2eaf4;
    --muted: #4a6080;
    --card: rgba(8,20,40,0.8);
  }

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Space Grotesk', sans-serif;
    overflow-x: hidden;
    cursor: none;
  }

  /* CUSTOM CURSOR */
  .cursor {
    position: fixed;
    width: 8px; height: 8px;
    background: var(--glow);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    transition: transform 0.1s;
    box-shadow: 0 0 12px var(--glow), 0 0 24px var(--glow);
  }
  .cursor-ring {
    position: fixed;
    width: 32px; height: 32px;
    border: 1px solid rgba(99,210,255,0.4);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9998;
    transition: all 0.15s ease;
  }

  /* NOISE OVERLAY */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 1;
    opacity: 0.4;
  }

  /* AURORA BG */
  .aurora {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
  }
  .aurora span {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.12;
    animation: drift 20s infinite alternate ease-in-out;
  }
  .aurora span:nth-child(1) { width:600px;height:600px;background:#63d2ff;top:-100px;left:-100px;animation-delay:0s; }
  .aurora span:nth-child(2) { width:500px;height:500px;background:#a78bfa;top:40%;right:-100px;animation-delay:-7s; }
  .aurora span:nth-child(3) { width:400px;height:400px;background:#34d399;bottom:-100px;left:30%;animation-delay:-14s; }
  @keyframes drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,60px) scale(1.1)} }

  /* GRID LINES */
  .grid-overlay {
    position: fixed;
    inset: 0;
    z-index: 0;
    background-image:
      linear-gradient(rgba(99,210,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(99,210,255,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
  }

  /* LAYOUT */
  .container {
    position: relative;
    z-index: 2;
    max-width: 960px;
    margin: 0 auto;
    padding: 0 24px;
  }

  /* ── HERO ── */
  .hero {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px 0 60px;
  }

  .hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--glow);
    margin-bottom: 24px;
    opacity: 0;
    animation: fadeUp 0.8s 0.2s forwards;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .hero-eyebrow::before {
    content: '';
    width: 40px; height: 1px;
    background: var(--glow);
  }

  .hero-name {
    font-family: 'Syne', sans-serif;
    font-size: clamp(56px, 10vw, 96px);
    font-weight: 800;
    line-height: 0.95;
    letter-spacing: -3px;
    opacity: 0;
    animation: fadeUp 0.8s 0.4s forwards;
  }
  .hero-name .line1 { display: block; color: var(--text); }
  .hero-name .line2 {
    display: block;
    background: linear-gradient(135deg, var(--glow) 0%, var(--glow2) 50%, var(--glow3) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .hero-desc {
    margin-top: 32px;
    font-size: 18px;
    color: var(--muted);
    max-width: 520px;
    line-height: 1.7;
    font-weight: 300;
    opacity: 0;
    animation: fadeUp 0.8s 0.6s forwards;
  }
  .hero-desc strong { color: var(--text); font-weight: 500; }

  .hero-tags {
    margin-top: 40px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    opacity: 0;
    animation: fadeUp 0.8s 0.8s forwards;
  }
  .tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: 6px 14px;
    border: 1px solid var(--border);
    border-radius: 100px;
    color: var(--muted);
    letter-spacing: 1px;
    transition: all 0.3s;
  }
  .tag:hover {
    border-color: var(--glow);
    color: var(--glow);
    background: rgba(99,210,255,0.05);
  }

  .hero-stats {
    margin-top: 64px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    opacity: 0;
    animation: fadeUp 0.8s 1s forwards;
  }
  .stat-item {
    background: var(--card);
    padding: 28px 20px;
    text-align: center;
    transition: background 0.3s;
  }
  .stat-item:hover { background: rgba(99,210,255,0.04); }
  .stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--glow), var(--glow2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .stat-label {
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 1px;
    margin-top: 4px;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ── SECTION ── */
  section { padding: 100px 0; }

  .section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--glow);
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .section-label::after { content:''; flex:1; height:1px; background:var(--border); }

  .section-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(32px, 5vw, 48px);
    font-weight: 700;
    letter-spacing: -1.5px;
    margin-bottom: 48px;
    line-height: 1.1;
  }

  /* ── PROJECTS ── */
  .projects-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  .project-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 32px 28px;
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.23,1,0.32,1);
    cursor: default;
  }
  .project-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at var(--mx,50%) var(--my,50%), rgba(99,210,255,0.06), transparent 60%);
    opacity: 0;
    transition: opacity 0.3s;
  }
  .project-card:hover::before { opacity: 1; }
  .project-card:hover {
    border-color: rgba(99,210,255,0.25);
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(99,210,255,0.1);
  }

  .project-card.featured {
    grid-column: span 2;
    background: linear-gradient(135deg, rgba(8,20,40,0.9), rgba(20,10,40,0.9));
  }

  .project-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 2px;
    margin-bottom: 20px;
  }
  .project-icon {
    font-size: 28px;
    margin-bottom: 16px;
    display: block;
  }
  .project-name {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
  }
  .project-desc {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.6;
    margin-bottom: 20px;
  }
  .project-stack {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .stack-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    padding: 4px 10px;
    background: rgba(99,210,255,0.06);
    border: 1px solid rgba(99,210,255,0.12);
    border-radius: 100px;
    color: var(--glow);
    letter-spacing: 0.5px;
  }
  .project-status {
    position: absolute;
    top: 20px;
    right: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    padding: 4px 10px;
    border-radius: 100px;
    letter-spacing: 1px;
  }
  .status-live { background: rgba(52,211,153,0.1); color: var(--glow3); border: 1px solid rgba(52,211,153,0.2); }
  .status-wip { background: rgba(167,139,250,0.1); color: var(--glow2); border: 1px solid rgba(167,139,250,0.2); }

  /* ── SKILLS ── */
  .skills-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
    align-items: start;
  }

  .skill-group-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 20px;
  }
  .skill-bar-item { margin-bottom: 16px; }
  .skill-bar-top {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 8px;
    font-weight: 500;
  }
  .skill-bar-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
  }
  .skill-bar-track {
    height: 3px;
    background: rgba(99,210,255,0.08);
    border-radius: 100px;
    overflow: hidden;
  }
  .skill-bar-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, var(--glow), var(--glow2));
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 1.2s cubic-bezier(0.23,1,0.32,1);
  }
  .skill-bar-fill.animated { transform: scaleX(1); }

  .tools-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .tool-chip {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 12px;
    text-align: center;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
  }
  .tool-chip:hover {
    border-color: rgba(99,210,255,0.3);
    background: rgba(99,210,255,0.04);
    transform: translateY(-2px);
  }
  .tool-chip .tool-icon { font-size: 20px; display: block; margin-bottom: 6px; }

  /* ── ACHIEVEMENTS ── */
  .timeline {
    position: relative;
    padding-left: 32px;
  }
  .timeline::before {
    content: '';
    position: absolute;
    left: 0; top: 8px; bottom: 8px;
    width: 1px;
    background: linear-gradient(to bottom, var(--glow), var(--glow2), transparent);
  }
  .timeline-item {
    position: relative;
    padding: 0 0 40px 32px;
    opacity: 0;
    transform: translateX(-10px);
    transition: all 0.6s ease;
  }
  .timeline-item.visible { opacity: 1; transform: translateX(0); }
  .timeline-dot {
    position: absolute;
    left: -4px; top: 4px;
    width: 9px; height: 9px;
    border-radius: 50%;
    background: var(--glow);
    box-shadow: 0 0 12px var(--glow);
  }
  .timeline-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--glow);
    letter-spacing: 2px;
    margin-bottom: 8px;
  }
  .timeline-title {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 6px;
  }
  .timeline-sub { font-size: 14px; color: var(--muted); line-height: 1.6; }

  /* ── FOOTER ── */
  .footer {
    border-top: 1px solid var(--border);
    padding: 60px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: gap;
  }
  .footer-name {
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--glow), var(--glow2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .footer-links { display: flex; gap: 24px; flex-wrap: wrap; }
  .footer-link {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    text-decoration: none;
    letter-spacing: 1px;
    transition: color 0.3s;
  }
  .footer-link:hover { color: var(--glow); }

  /* ANIMATIONS */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: all 0.7s cubic-bezier(0.23,1,0.32,1);
  }
  .reveal.visible {
    opacity: 1;
    transform: translateY(0);
  }

  /* SCROLLBAR */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: rgba(99,210,255,0.2); border-radius: 100px; }

  /* GLOW LINE DIVIDER */
  .glow-line {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--glow), transparent);
    opacity: 0.3;
    margin: 0;
  }

  @media (max-width: 700px) {
    .projects-grid { grid-template-columns: 1fr; }
    .project-card.featured { grid-column: span 1; }
    .skills-container { grid-template-columns: 1fr; }
    .hero-stats { grid-template-columns: repeat(2,1fr); }
    .footer { flex-direction: column; gap: 24px; text-align: center; }
  }
</style>
</head>
<body>

<div class="cursor" id="cursor"></div>
<div class="cursor-ring" id="cursorRing"></div>

<div class="aurora">
  <span></span><span></span><span></span>
</div>
<div class="grid-overlay"></div>

<div class="container">

  <!-- ═══ HERO ═══ -->
  <section class="hero">
    <div class="hero-eyebrow">Software Engineer & App Developer</div>
    <h1 class="hero-name">
      <span class="line1">Mohamed</span>
      <span class="line2">Basheer</span>
    </h1>
    <p class="hero-desc">
      I build <strong>Flutter apps</strong> that feel alive — cross-platform, bilingual, pixel-perfect.
      CS undergrad at <strong>SRM IST</strong> obsessed with clean architecture,
      real-world impact, and writing code that scales.
    </p>
    <div class="hero-tags">
      <span class="tag">Flutter</span>
      <span class="tag">Firebase</span>
      <span class="tag">GetX</span>
      <span class="tag">DSA · LeetCode</span>
      <span class="tag">IEEE TEMS Secretary</span>
      <span class="tag">Hackathon Winner</span>
      <span class="tag">FAANG-bound</span>
    </div>
    <div class="hero-stats">
      <div class="stat-item">
        <div class="stat-num">9.20</div>
        <div class="stat-label">CGPA</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">3+</div>
        <div class="stat-label">Apps Shipped</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">🥉</div>
        <div class="stat-label">HackDroid 2025</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">500+</div>
        <div class="stat-label">Event Attendees</div>
      </div>
    </div>
  </section>

  <div class="glow-line"></div>

  <!-- ═══ PROJECTS ═══ -->
  <section>
    <div class="section-label reveal">Selected Work</div>
    <h2 class="section-title reveal">Things I've<br/>Actually Built</h2>
    <div class="projects-grid reveal">

      <div class="project-card featured" id="card1">
        <span class="project-status status-wip">WIP</span>
        <div class="project-num">01 — FEATURED</div>
        <span class="project-icon">🌐</span>
        <div class="project-name">Webtree</div>
        <p class="project-desc">Enterprise rewards & gift card platform for NAD Group. Full bilingual support (English + Arabic) with RTL layout, employee & customer interfaces, and complex API integrations. Real product. Real users.</p>
        <div class="project-stack">
          <span class="stack-pill">Flutter</span>
          <span class="stack-pill">REST APIs</span>
          <span class="stack-pill">GetX</span>
          <span class="stack-pill">EN / AR</span>
          <span class="stack-pill">RTL</span>
          <span class="stack-pill">flutter_screenutil</span>
        </div>
      </div>

      <div class="project-card" id="card2">
        <span class="project-status status-live">LIVE</span>
        <div class="project-num">02</div>
        <span class="project-icon">📅</span>
        <div class="project-name">SlotBook</div>
        <p class="project-desc">Smart slot-booking app for university campuses. Real-time availability, Firebase-backed scheduling.</p>
        <div class="project-stack">
          <span class="stack-pill">Flutter</span>
          <span class="stack-pill">Firebase</span>
          <span class="stack-pill">Real-time DB</span>
        </div>
      </div>

      <div class="project-card" id="card3">
        <span class="project-status status-live">LIVE</span>
        <div class="project-num">03</div>
        <span class="project-icon">📋</span>
        <div class="project-name">ScheduleUp</div>
        <p class="project-desc">All-in-one planner for students and campus clubs. Built for everyday chaos.</p>
        <div class="project-stack">
          <span class="stack-pill">Flutter</span>
          <span class="stack-pill">Firebase</span>
          <span class="stack-pill">GetX</span>
        </div>
      </div>

      <div class="project-card" id="card4">
        <span class="project-status status-live">RESEARCH</span>
        <div class="project-num">04</div>
        <span class="project-icon">🧠</span>
        <div class="project-name">Alzheimer's Detection</div>
        <p class="project-desc">ML-powered early-stage Alzheimer's detection system. Applied AI to healthcare — because software can save lives.</p>
        <div class="project-stack">
          <span class="stack-pill">Python</span>
          <span class="stack-pill">ML</span>
          <span class="stack-pill">Research</span>
        </div>
      </div>

    </div>
  </section>

  <div class="glow-line"></div>

  <!-- ═══ SKILLS ═══ -->
  <section>
    <div class="section-label reveal">Arsenal</div>
    <h2 class="section-title reveal">Tech I Live In</h2>
    <div class="skills-container">
      <div class="reveal">
        <div class="skill-group-title">Core Proficiency</div>
        <div class="skill-bar-item">
          <div class="skill-bar-top"><span>Flutter / Dart</span><span class="skill-bar-pct">92%</span></div>
          <div class="skill-bar-track"><div class="skill-bar-fill" data-pct="0.92"></div></div>
        </div>
        <div class="skill-bar-item">
          <div class="skill-bar-top"><span>Firebase</span><span class="skill-bar-pct">85%</span></div>
          <div class="skill-bar-track"><div class="skill-bar-fill" data-pct="0.85"></div></div>
        </div>
        <div class="skill-bar-item">
          <div class="skill-bar-top"><span>C++ / DSA</span><span class="skill-bar-pct">80%</span></div>
          <div class="skill-bar-track"><div class="skill-bar-fill" data-pct="0.80"></div></div>
        </div>
        <div class="skill-bar-item">
          <div class="skill-bar-top"><span>Python</span><span class="skill-bar-pct">75%</span></div>
          <div class="skill-bar-track"><div class="skill-bar-fill" data-pct="0.75"></div></div>
        </div>
        <div class="skill-bar-item">
          <div class="skill-bar-top"><span>JavaScript</span><span class="skill-bar-pct">65%</span></div>
          <div class="skill-bar-track"><div class="skill-bar-fill" data-pct="0.65"></div></div>
        </div>
      </div>

      <div class="reveal">
        <div class="skill-group-title">Tools & Ecosystem</div>
        <div class="tools-grid">
          <div class="tool-chip"><span class="tool-icon">🐦</span>GetX</div>
          <div class="tool-chip"><span class="tool-icon">🎨</span>Figma</div>
          <div class="tool-chip"><span class="tool-icon">📬</span>Postman</div>
          <div class="tool-chip"><span class="tool-icon">🔧</span>Git</div>
          <div class="tool-chip"><span class="tool-icon">🐙</span>GitHub</div>
          <div class="tool-chip"><span class="tool-icon">📐</span>screenutil</div>
          <div class="tool-chip"><span class="tool-icon">🔒</span>Auth APIs</div>
          <div class="tool-chip"><span class="tool-icon">🌍</span>REST</div>
          <div class="tool-chip"><span class="tool-icon">🧪</span>Testing</div>
        </div>
      </div>
    </div>
  </section>

  <div class="glow-line"></div>

  <!-- ═══ TIMELINE ═══ -->
  <section>
    <div class="section-label reveal">Journey</div>
    <h2 class="section-title reveal">How I Got Here</h2>
    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-date">2025</div>
        <div class="timeline-title">🥉 HackDroid 2025 — 3rd Place</div>
        <p class="timeline-sub">Competed against top dev teams. Placed. Shipped. Learned.</p>
      </div>
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-date">2024–2025</div>
        <div class="timeline-title">💼 Software Dev Intern · CloudTrek Technologies</div>
        <p class="timeline-sub">Built real features for real products. Flutter, APIs, clean code in production.</p>
      </div>
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-date">2024</div>
        <div class="timeline-title">📡 Elected IEEE TEMS Secretary</div>
        <p class="timeline-sub">Organized Pitch Perfect 2024 — 500+ attendees. Led a chapter that actually moves.</p>
      </div>
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-date">2023 →</div>
        <div class="timeline-title">🎓 CS Engineering · SRM IST · CGPA 9.20</div>
        <p class="timeline-sub">Building, competing, learning. Every single day.</p>
      </div>
    </div>
  </section>

  <div class="glow-line"></div>

  <!-- ═══ FOOTER ═══ -->
  <footer class="footer reveal">
    <div class="footer-name">M. Basheer</div>
    <div class="footer-links">
      <a href="https://github.com/OWAIZ2005" class="footer-link">GitHub ↗</a>
      <a href="https://leetcode.com/Basheer2005" class="footer-link">LeetCode ↗</a>
      <a href="https://linkedin.com" class="footer-link">LinkedIn ↗</a>
    </div>
  </footer>

</div>

<script>
  // Custom cursor
  const cursor = document.getElementById('cursor');
  const ring = document.getElementById('cursorRing');
  let mx = window.innerWidth/2, my = window.innerHeight/2;
  let rx = mx, ry = my;

  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    cursor.style.left = mx - 4 + 'px';
    cursor.style.top  = my - 4 + 'px';
  });

  function animRing() {
    rx += (mx - rx) * 0.15;
    ry += (my - ry) * 0.15;
    ring.style.left = rx - 16 + 'px';
    ring.style.top  = ry - 16 + 'px';
    requestAnimationFrame(animRing);
  }
  animRing();

  // Card magnetic mouse effect
  document.querySelectorAll('.project-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width * 100).toFixed(1);
      const y = ((e.clientY - r.top)  / r.height * 100).toFixed(1);
      card.style.setProperty('--mx', x + '%');
      card.style.setProperty('--my', y + '%');
    });
  });

  // Scroll reveal
  const observer = new IntersectionObserver(entries => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 80);
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.reveal, .timeline-item').forEach(el => observer.observe(el));

  // Skill bar animation
  const barObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.skill-bar-fill').forEach(bar => {
          bar.style.transform = `scaleX(${bar.dataset.pct})`;
          bar.classList.add('animated');
        });
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.skills-container').forEach(el => barObserver.observe(el));
</script>
</body>
</html>
