document.addEventListener('DOMContentLoaded', () => {
  // Inicializaciones
  initScrollProgress();
  initMobileNav();
  initCopyEmail();
  initTiltCards();
  initTerminalCLI();
  initProjectFiltering();
  initContactForm();
  initThreeBackground();

  const yearSpan = document.getElementById('current-year');
  if (yearSpan) yearSpan.textContent = String(new Date().getFullYear());
});

/* ==========================================================================
   1. Scroll Progress & Mobile Navigation
   ========================================================================== */
function initScrollProgress() {
  const progressBar = document.getElementById('scroll-progress');
  if (!progressBar) return;

  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = totalHeight > 0 ? (window.scrollY / totalHeight) * 100 : 0;
    progressBar.style.width = `${progress}%`;
  }, { passive: true });
}

function initMobileNav() {
  const menuBtn = document.getElementById('menu-toggle');
  const navMenu = document.getElementById('nav-menu');
  if (!menuBtn || !navMenu) return;

  menuBtn.addEventListener('click', () => {
    const isOpen = navMenu.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', String(isOpen));
  });

  navMenu.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('open');
      menuBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

/* ==========================================================================
   2. Copy Email to Clipboard
   ========================================================================== */
function initCopyEmail() {
  const copyBtn = document.getElementById('btn-copy-email');
  const emailTextElem = document.getElementById('email-text');
  const copyTextElem = document.getElementById('copy-text');
  if (!copyBtn || !emailTextElem) return;

  const emailToCopy = emailTextElem.textContent.trim();

  copyBtn.addEventListener('click', async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(emailToCopy);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = emailToCopy;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }

      copyBtn.classList.add('copied');
      if (copyTextElem) copyTextElem.textContent = '¡Copiado!';

      setTimeout(() => {
        copyBtn.classList.remove('copied');
        if (copyTextElem) copyTextElem.textContent = 'Copiar';
      }, 2500);
    } catch (_err) {
      if (copyTextElem) copyTextElem.textContent = 'Error al copiar';
    }
  });
}

/* ==========================================================================
   3. 3D Tilt Effect on Cards
   ========================================================================== */
function initTiltCards() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const tiltElements = document.querySelectorAll('[data-tilt]');
  tiltElements.forEach((elem) => {
    elem.addEventListener('pointermove', (e) => {
      const rect = elem.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      elem.style.transform = `perspective(1000px) rotateX(${y * -7}deg) rotateY(${x * 9}deg) translateY(-2px)`;
    });

    elem.addEventListener('pointerleave', () => {
      elem.style.transform = '';
    });
  });
}

/* ==========================================================================
   4. Project Filtering & Dynamic Catalog
   ========================================================================== */
function initProjectFiltering() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const container = document.getElementById('projects-container');
  if (!filterBtns.length || !container) return;

  filterBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      filterBtns.forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      const filter = btn.dataset.filter;
      const cards = container.querySelectorAll('.project-card');

      cards.forEach((card) => {
        if (filter === 'all' || card.dataset.category === filter) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  // Intentar sincronizar con /api/projects para actualizar la lista completa
  loadLiveProjects();
}

async function loadLiveProjects() {
  try {
    const res = await fetch('/api/projects');
    if (!res.ok) return;
    const data = await res.json();
    if (data && Array.isArray(data.projects) && data.projects.length > 0) {
      renderProjectsList(data.projects);
    }
  } catch (_e) {
    // Si falla, el fallback HTML en index.html ya se encuentra renderizado
  }
}

function renderProjectsList(projects) {
  const container = document.getElementById('projects-container');
  if (!container) return;

  container.innerHTML = projects.map((p) => {
    const categoryClass = `badge-${p.category_id || 'infra'}`;
    const actionHtml = p.url
      ? `<a href="${escapeAttr(p.url)}" target="_blank" rel="noopener noreferrer" class="card-link">Ver Sistema / Repo →</a>`
      : `<span class="card-status-text">Operación Privada / Interna</span>`;

    return `
      <article class="project-card" data-category="${escapeAttr(p.category_id || 'all')}" data-tilt>
        <div class="card-meta">
          <span class="category-badge ${categoryClass}">${escapeHtml(p.category)}</span>
          <span class="status-pill-small">${escapeHtml(p.badge || 'Producción')}</span>
        </div>
        <h3>${escapeHtml(p.name)}</h3>
        <p>${escapeHtml(p.description)}</p>
        <div class="tags-cloud">
          ${(p.tags || []).map((t) => `<span>${escapeHtml(t)}</span>`).join('')}
        </div>
        <div class="card-actions">
          ${actionHtml}
        </div>
      </article>
    `;
  }).join('');

  // Re-aplicar tilt a las nuevas tarjetas
  initTiltCards();
}

/* ==========================================================================
   5. Star Terminal CLI Interactivo
   ========================================================================== */
function initTerminalCLI() {
  const form = document.getElementById('terminal-form');
  const input = document.getElementById('terminal-input');
  const body = document.getElementById('terminal-body');
  const shortcutBtns = document.querySelectorAll('.term-btn');
  if (!form || !input || !body) return;

  const COMMANDS = {
    help: () => [
      'Comandos disponibles:',
      '  status       - Muestra telemetría en vivo del clúster físico Star',
      '  saori        - Consulta el estado del enjambre multiagente de IA',
      '  drakescraft  - Métricas de la red de Minecraft y plugins en Java 21',
      '  education    - Sistemas y laboratorios de tecnología educativa',
      '  backups      - Estado de los pipelines híbridos (GitHub + Drive)',
      '  stack        - Resumen de arquitectura y herramientas clave',
      '  whoami       - Identidad y rol técnico de Jack / JackStar',
      '  contact      - Información de contacto y enlaces oficiales',
      '  clear        - Limpia la pantalla de la consola'
    ],
    status: () => [
      '[+] CLÚSTER STAR · TELEMETRÍA GLOBAL',
      '  Nodo Maestro: Star (Santiago, CL) · OS: Ubuntu 24.04 LTS x86_64',
      '  Almacenamiento: LVM Volume Group (NVMe + HDD Array) · Salud: OK (100% libre asignado)',
      '  Red Privada: Tailscale Mesh (WireGuard Cifrado) · Túneles: Cloudflare Edge (Zero Exposed Ports)',
      '  Carga de CPU: 0.85, 0.92, 0.78 (Estable) · RAM: 32 GB DDR4 ECC (Asignada)',
      '  Contenedores Docker: jack-portal (8082), saori-stack, star-monitor, cempudla'
    ],
    saori: () => [
      '[+] SAORI SRE CORE · TRI-AGENT SWARM OPERATIONAL',
      '  Agente Principal Dev: Google Antigravity (Gemini 3.8 Flash High · Esfuerzo Alto)',
      '  Arquitecto Técnico:   Claude Code (Razonamiento y orquestación)',
      '  Integrador & QA:     OpenAI Codex (GPT-5.6 Luna · Verificación y tests)',
      '  Control de Estado:   SQLite WAL Mutex Leasing (observe, develop, admin)',
      '  Presencia Omnicanal: Minecraft Avatar Bot (Mineflayer), Discord Bot, WhatsApp Voice (ElevenLabs)'
    ],
    drakescraft: () => [
      '[+] DRAKESCRAFT NETWORK (Purpur 1.21.11 / Java 21 LTS)',
      '  Modalidades: Survival, OneBlock, SkyBlock, Classic Vanilla, Laboratory',
      '  Addons & Plugins: +100 plugins mantenidos y optimizados',
      '  Odysseia Engine: Pasarela de transacciones Tebex con verificación idempotente',
      '  BentoBox-Drake & InvSwitcher-Drake: Deserialización Data Components zero-loss',
      '  Ecosistema Slimefun: +15 addons compilados y modernizados a Java 21',
      '  Comunidad Oficial: https://discord.gg/rv3vtXZTk7'
    ],
    education: () => [
      '[+] CAMPUS IT & TECNOLOGÍA EDUCATIVA (Colegio Castelgandolfo & Centros)',
      '  Castel LabOps (VeyonScripts): Diagnóstico y administración de aulas, Wake-on-LAN, WinRM',
      '  CampusCare Monitoring: PWA con mapeo físico y telemetría de equipos de laboratorio',
      '  CastelRoomKeeper: Calendario y gestión de salas sin contraseñas maestras compartidas',
      '  CastelCredCam: Software de fotografía masiva escolar en PySide6/Qt con reencuadre facial',
      '  CEMPUDLA: Plataforma multicentro con Google OAuth federado y autenticación por RUT'
    ],
    backups: () => [
      '[+] PIPELINE DE RESPALDO RESILIENTE (Multi-Tier Disaster Recovery)',
      '  Tier 1 (Nocturno): Respaldo incremental automático sincronizado a repositorios Git seguros',
      '  Tier 2 (Semanal Masivo): Archivo completo de mundos, configs y bases de datos a Google Drive',
      '  Notificaciones: Webhooks a Discord con reporte de integridad SHA256 y tamaño',
      '  Filosofía: "Ambitious is good. Recoverable is better."'
    ],
    stack: () => [
      '[+] STACK TECNOLÓGICO CLAVE',
      '  Lenguajes: Java 21 LTS, Python 3.12, TypeScript, JavaScript, Rust, PHP, Bash, PowerShell',
      '  SRE & DevOps: Linux Ubuntu, Docker Compose, LVM RAID, Tailscale Mesh, Cloudflare Tunnels',
      '  Bases de Datos: SQLite WAL, PostgreSQL, Redis, Paper Data Components',
      '  IA & Automatización: Antigravity Gemini 3.8 High, Claude Code, Codex, Mineflayer, ElevenLabs'
    ],
    whoami: () => [
      'Jack / JackStar',
      'Systems Engineer · Infrastructure Operator · Full-Stack Builder & Sovereign AI Creator',
      'Especialista en resiliencia de producción, Java 21 de alta concurrencia y homelab SRE.'
    ],
    contact: () => [
      '[+] CANALES DE CONTACTO OFICIALES',
      '  Discord Oficial: https://discord.gg/rv3vtXZTk7',
      '  GitHub:          https://github.com/JackStar6677-1',
      '  DrakesCraft:     https://web.drakescraft.cl',
      '  Correo:          pablo.elias.miranda.292003@gmail.com'
    ]
  };

  function executeCommand(cmdRaw) {
    const cmd = cmdRaw.trim().toLowerCase();
    if (!cmd) return;

    // Agregar echo del comando
    const echoDiv = document.createElement('div');
    echoDiv.className = 'term-line command-echo';
    echoDiv.innerHTML = `<span class="prompt">jack@star:~$</span> <span class="cmd-text">${escapeHtml(cmdRaw)}</span>`;
    body.appendChild(echoDiv);

    if (cmd === 'clear') {
      body.innerHTML = '';
      return;
    }

    const outputDiv = document.createElement('div');
    outputDiv.className = 'term-line output';

    if (COMMANDS[cmd]) {
      const lines = COMMANDS[cmd]();
      outputDiv.innerHTML = lines.map((l) => `<span>${escapeHtml(l)}</span>`).join('');
    } else {
      outputDiv.innerHTML = `<span style="color:var(--red);">Comando desconocido: '${escapeHtml(cmd)}'. Escribe 'help' para ver la lista de comandos disponibles.</span>`;
    }

    body.appendChild(outputDiv);
    body.scrollTop = body.scrollHeight;
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const val = input.value;
    input.value = '';
    executeCommand(val);
  });

  shortcutBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const cmd = btn.dataset.cmd;
      if (cmd) executeCommand(cmd);
    });
  });
}

/* ==========================================================================
   6. Contact Form Submission
   ========================================================================== */
function initContactForm() {
  const form = document.getElementById('contact-form');
  const statusElem = document.getElementById('form-status');
  const submitBtn = document.getElementById('form-submit-btn');
  if (!form || !statusElem) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    statusElem.className = 'form-status-msg';
    statusElem.textContent = 'Validando y preparando solicitud...';

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    // Validar honeypot antispam
    if (payload.website && payload.website.trim() !== '') {
      statusElem.textContent = 'Solicitud no permitida.';
      return;
    }

    // Validar campos obligatorios
    if (!payload.name || !payload.email || !payload.service || !payload.message) {
      statusElem.className = 'form-status-msg error';
      statusElem.textContent = 'Por favor completa todos los campos requeridos marcados con (*).';
      return;
    }

    if (submitBtn) submitBtn.disabled = true;

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (!response.ok) {
        statusElem.className = 'form-status-msg error';
        statusElem.textContent = result.error || 'Error al validar el formulario. Revisa los datos.';
        if (submitBtn) submitBtn.disabled = false;
        return;
      }

      statusElem.className = 'form-status-msg success';
      statusElem.textContent = '¡Solicitud aceptada! Abriendo tu cliente de correo preparado...';

      // Abrir plantilla de correo pre-rellenada
      const subject = encodeURIComponent(`[Contacto JackStar] ${payload.service} - ${payload.name}`);
      const bodyText = [
        `Nombre: ${payload.name}`,
        `Email de contacto: ${payload.email}`,
        `Área de Servicio: ${payload.service}`,
        `Presupuesto: ${payload.budget || 'A convenir'}`,
        `Urgencia: ${payload.urgency || 'Estándar'}`,
        '----------------------------------------',
        'Mensaje:',
        payload.message
      ].join('\n');

      window.location.href = `mailto:pablo.elias.miranda.292003@gmail.com?subject=${subject}&body=${encodeURIComponent(bodyText)}`;
      form.reset();
    } catch (_err) {
      statusElem.className = 'form-status-msg error';
      statusElem.textContent = 'No se pudo conectar al servidor. Puedes escribir directamente a pablo.elias.miranda.292003@gmail.com';
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

/* ==========================================================================
   7. Three.js 3D Interactive Cyber Constellation Background
   ========================================================================== */
function initThreeBackground() {
  const canvas = document.getElementById('bg-canvas-3d');
  if (!canvas) return;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return; // Respetar accesibilidad
  }

  // Verificar soporte de WebGL y Three.js
  if (typeof THREE === 'undefined') {
    init2DFallback(canvas);
    return;
  }

  let scene, camera, renderer, globeMesh, particlesMesh;
  let mouseX = 0, mouseY = 0;
  let targetX = 0, targetY = 0;
  let isPaused = false;

  try {
    const width = window.innerWidth;
    const height = window.innerHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
    camera.position.z = 180;

    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    // 1. Esfera de malla icosaédrica (Nodo orbital Star)
    const globeGeo = new THREE.IcosahedronGeometry(60, 2);
    const globeMat = new THREE.MeshBasicMaterial({
      color: 0x8b5cf6,
      wireframe: true,
      transparent: true,
      opacity: 0.15
    });
    globeMesh = new THREE.Mesh(globeGeo, globeMat);
    scene.add(globeMesh);

    // 2. Nube de partículas constelación
    const particleCount = Math.min(220, Math.floor(width / 7));
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const cyanColor = new THREE.Color(0x22d3ee);
    const purpleColor = new THREE.Color(0xa855f7);
    const goldColor = new THREE.Color(0xf59e0b);

    for (let i = 0; i < particleCount; i++) {
      const radius = 65 + Math.random() * 85;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      const chosenColor = i % 3 === 0 ? cyanColor : (i % 3 === 1 ? purpleColor : goldColor);
      colors[i * 3] = chosenColor.r;
      colors[i * 3 + 1] = chosenColor.g;
      colors[i * 3 + 2] = chosenColor.b;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 2.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending
    });

    particlesMesh = new THREE.Points(particleGeo, particleMat);
    scene.add(particlesMesh);

    // Mouse movement listener
    window.addEventListener('pointermove', (e) => {
      mouseX = (e.clientX / window.innerWidth) * 2 - 1;
      mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    }, { passive: true });

    // Window resize
    window.addEventListener('resize', () => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }, { passive: true });

    // Pausar renderizado cuando no es visible para maximizar rendimiento
    document.addEventListener('visibilitychange', () => {
      isPaused = document.hidden;
    });

    // Render loop
    function animate() {
      requestAnimationFrame(animate);
      if (isPaused) return;

      // Suavizado del ratón
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;

      if (globeMesh) {
        globeMesh.rotation.y += 0.0018;
        globeMesh.rotation.x += 0.0009;
        globeMesh.rotation.y += targetX * 0.005;
        globeMesh.rotation.x += -targetY * 0.005;
      }

      if (particlesMesh) {
        particlesMesh.rotation.y -= 0.0012;
        particlesMesh.rotation.z += 0.0006;
      }

      renderer.render(scene, camera);
    }

    animate();
  } catch (_e) {
    // Si WebGL falla por drivers o permisos, degradar suavemente al canvas 2D
    init2DFallback(canvas);
  }
}

function init2DFallback(canvas) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let width = 0, height = 0;
  let points = [];

  const resize = () => {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    points = Array.from({ length: 45 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3
    }));
  };

  const draw = () => {
    ctx.clearRect(0, 0, width, height);
    points.forEach((p, idx) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.fillStyle = idx % 2 === 0 ? 'rgba(34, 211, 238, 0.4)' : 'rgba(168, 85, 247, 0.4)';
      ctx.beginPath();
      ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
      ctx.fill();

      points.slice(idx + 1).forEach((p2) => {
        const d = Math.hypot(p.x - p2.x, p.y - p2.y);
        if (d < 120) {
          ctx.strokeStyle = `rgba(34, 211, 238, ${0.12 * (1 - d / 120)})`;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      });
    });
    requestAnimationFrame(draw);
  };

  window.addEventListener('resize', resize);
  resize();
  draw();
}

/* ==========================================================================
   Utilities
   ========================================================================== */
function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }[m]));
}

function escapeAttr(str) {
  return escapeHtml(str).replace(/`/g, '&#096;');
}
