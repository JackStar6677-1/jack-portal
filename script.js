document.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');
  const progress = document.getElementById('progress');

  menu?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });

  nav?.addEventListener('click', () => {
    nav.classList.remove('open');
    menu?.setAttribute('aria-expanded', 'false');
  });

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));

  window.addEventListener('scroll', () => {
    const available = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${available > 0 ? (window.scrollY / available) * 100 : 0}%`;
  }, { passive: true });

  document.getElementById('year').textContent = String(new Date().getFullYear());
  setupSignalField();
  loadPortalData();
  setupContactForm();
});

async function loadPortalData() {
  const [services, projects] = await Promise.all([
    fetchJson('/api/services'),
    fetchJson('/api/projects')
  ]);

  renderServices(services.services || []);
  renderProjects(projects.projects || []);
  renderStack([
    'Python', 'JavaScript', 'HTML/CSS', 'FastAPI', 'Node.js', 'Docker', 'Linux',
    'Cloudflare Tunnel', 'PostgreSQL', 'GitHub', 'Veyon', 'PowerShell', 'Java', 'Paper', 'Slimefun'
  ]);
}

async function fetchJson(url) {
  const response = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!response.ok) return {};
  return response.json();
}

function renderServices(services) {
  const container = document.getElementById('services-grid');
  container.innerHTML = services.map((service, index) => `
    <article class="service-card reveal visible">
      <div class="card-kicker"><span>${String(index + 1).padStart(2, '0')}</span><span>${escapeHtml(service.area)}</span></div>
      <h3>${escapeHtml(service.title)}</h3>
      <p>${escapeHtml(service.description)}</p>
      <ul>${service.items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
    </article>
  `).join('');
}

function renderProjects(projects) {
  const container = document.getElementById('projects-list');
  container.innerHTML = projects.map((project, index) => {
    const content = `
      <div class="project-meta"><span>${escapeHtml(project.category)}</span><b>${String(index + 1).padStart(2, '0')}</b></div>
      <h3>${escapeHtml(project.name)}</h3>
      <p>${escapeHtml(project.description)}</p>
      <div class="project-tags">${project.tags.map((tag) => `<span>${escapeHtml(tag)}</span>`).join('')}</div>
    `;
    if (project.url) {
      return `<a class="project-card reveal visible" href="${escapeAttribute(project.url)}" target="_blank" rel="noopener">${content}</a>`;
    }
    return `<article class="project-card reveal visible">${content}</article>`;
  }).join('');
}

function renderStack(stack) {
  document.getElementById('stack-list').innerHTML = stack.map((item) => `<span>${escapeHtml(item)}</span>`).join('');
}

function setupContactForm() {
  const form = document.getElementById('contact-form');
  const status = document.getElementById('form-status');

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.textContent = 'Validando solicitud...';

    const payload = Object.fromEntries(new FormData(form).entries());
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok) {
        status.textContent = result.error || 'Revisa los campos del formulario.';
        return;
      }

      status.textContent = 'Solicitud validada. Se abrirá tu cliente de correo para enviarla.';
      const subject = encodeURIComponent(`Diagnóstico técnico: ${payload.service}`);
      const body = encodeURIComponent([
        `Nombre: ${payload.name}`,
        `Email: ${payload.email}`,
        `Servicio: ${payload.service}`,
        `Presupuesto: ${payload.budget || 'No indicado'}`,
        `Urgencia: ${payload.urgency || 'No indicada'}`,
        '',
        payload.message
      ].join('\n'));
      window.location.href = `mailto:pablo.elias.miranda.292003@gmail.com?subject=${subject}&body=${body}`;
      form.reset();
    } catch (_error) {
      status.textContent = 'No se pudo validar ahora. Puedes escribir directamente al correo publicado.';
    }
  });
}

function setupSignalField() {
  const canvas = document.getElementById('signal-field');
  if (!canvas || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const context = canvas.getContext('2d');
  let width = 0;
  let height = 0;
  let points = [];

  const resize = () => {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    points = Array.from({ length: Math.min(42, Math.floor(width / 28)) }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.12,
      vy: (Math.random() - 0.5) * 0.12
    }));
  };

  const draw = () => {
    context.clearRect(0, 0, width, height);
    points.forEach((point, index) => {
      point.x += point.vx;
      point.y += point.vy;
      if (point.x < 0 || point.x > width) point.vx *= -1;
      if (point.y < 0 || point.y > height) point.vy *= -1;

      context.fillStyle = index % 3 === 0 ? 'rgba(245,197,66,.48)' : 'rgba(168,85,247,.34)';
      context.beginPath();
      context.arc(point.x, point.y, 1.25, 0, Math.PI * 2);
      context.fill();

      points.slice(index + 1).forEach((other) => {
        const distance = Math.hypot(point.x - other.x, point.y - other.y);
        if (distance < 125) {
          context.strokeStyle = `rgba(34,211,238,${(1 - distance / 125) * 0.08})`;
          context.beginPath();
          context.moveTo(point.x, point.y);
          context.lineTo(other.x, other.y);
          context.stroke();
        }
      });
    });
    window.requestAnimationFrame(draw);
  };

  window.addEventListener('resize', resize);
  resize();
  draw();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }[char]));
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, '&#096;');
}
