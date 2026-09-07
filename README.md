# Jack Portal · Portafolio técnico público

Portafolio técnico público seudónimo de **JackStar** (`https://jack.drakescraft.cl`).

## Objetivo

Presentar experiencia en ingeniería de sistemas, software Java, infraestructura Linux, automatización y tecnología aplicada sin revelar identidad legal, ubicación, datos de empleadores ni detalles operacionales.

La interfaz de telemetría es una **demostración representativa y sanitizada**: no consulta sistemas internos y no debe contener hosts, direcciones, credenciales, registros ni métricas de producción.

## Stack

- **Servidor Backend**: Python 3.12 (librería estándar, sin dependencias externas pesadas).
- **Frontend**: HTML5 semántico, CSS3 moderno con glassmorphism cyberpunk y JavaScript nativo.
- **3D & Interactividad**: Three.js (constelación de partículas y esfera orbital reactiva al cursor).
- **Terminal CLI**: Emulador interactivo de arquitectura de referencia, sin acceso a producción.
- **Despliegue**: Docker en `127.0.0.1:8082`, servido a través de Cloudflare Tunnel hacia `jack.drakescraft.cl`.

## Endpoints

- `GET /healthz`: Healthcheck estándar para Docker.
- `GET /api/health`: Estado del servicio y tiempo de actividad (uptime).
- `GET /api/profile`: Metadatos seudónimos, enlaces públicos y estadísticas generales.
- `GET /api/services`: Áreas de servicio: infraestructura, Java/Minecraft, automatización y tecnología aplicada.
- `GET /api/projects`: Catálogo enriquecido de proyectos con filtros de categoría.
- `GET /api/telemetry`: Arquitectura de referencia sanitizada; no incluye telemetría viva.
- `POST /api/contact`: Validación, honeypot antispam, rate limiting y encolado durable de solicitudes.

## Arquitectura de Despliegue

```text
GitHub (JackStar6677-1/jack-portal) -> Star (/opt/stacks/repos/jack-portal)
                                     -> Docker Compose (jack-portal en 127.0.0.1:8082)
                                     -> Cloudflare Tunnel -> jack.drakescraft.cl
```

## Entrega de contactos

El formulario no usa `mailto:`: eso solo abre un cliente local y no garantiza que
el mensaje llegue. La API valida la solicitud y la guarda de forma atómica en una
cola privada de Star antes de devolver `202 Accepted`.

```text
Navegador -> POST /api/contact -> cola privada /opt/stacks/state/jack-portal-contact
                                  -> relay systemd del host -> correo de SAORI
```

- El contenedor solo puede escribir envelopes JSON en la cola; no contiene ni lee
  credenciales SMTP.
- `contact_relay.py` ejecuta fuera de Docker e importa únicamente la función de
  correo ya configurada para SAORI. Si el correo falla, deja el archivo pendiente
  para el siguiente reintento.
- Los archivos entregados pasan a `sent/` y se eliminan después de 30 días. La
  cola, su contenido y los logs de entrega no se versionan ni se publican.
- Los archivos de `deploy/` instalan un `systemd.path` (entrega inmediata) y un
  `systemd.timer` (reintento periódico). Revisa el resultado con
  `systemctl --user status jack-portal-contact-relay.path`.

## Privacidad antes de publicar

- No subas CVs sin sanitizar, fotografías con pantallas legibles, correos, teléfonos,
  ubicaciones, instituciones, direcciones, nombres de hosts, IPs o registros.
- Toda imagen de entorno de trabajo debe eliminar marcas de dispositivo, fecha/hora y
  contenido legible de pantallas antes de entrar en `assets/`.
- Antes de un `git push`, ejecuta una búsqueda de datos personales y revisa
  `git diff --check`. Nunca uses `git add -A` para publicar este portal.
