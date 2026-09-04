# Jack Portal · Portafolio Profesional de Alto Impacto

Portafolio técnico público de **Jack / JackStar** (`https://jack.drakescraft.cl`).

## Objetivo

Exhibir la ingeniería de sistemas, arquitectura de software, clúster físico bare-metal (Star), desarrollo de alta concurrencia en Java 21 (DrakesCraft), enjambre de IA multiagente (SAORI) y plataformas de tecnología institucional/educativa.

## Stack

- **Servidor Backend**: Python 3.12 (librería estándar, sin dependencias externas pesadas).
- **Frontend**: HTML5 semántico, CSS3 moderno con glassmorphism cyberpunk y JavaScript nativo.
- **3D & Interactividad**: Three.js (constelación de partículas y esfera orbital reactiva al cursor).
- **Terminal CLI**: Emulador interactivo con telemetría en tiempo real del clúster Star.
- **Despliegue**: Docker en `127.0.0.1:8082`, servido a través de Cloudflare Tunnel hacia `jack.drakescraft.cl`.

## Endpoints

- `GET /healthz`: Healthcheck estándar para Docker.
- `GET /api/health`: Estado del servicio y tiempo de actividad (uptime).
- `GET /api/profile`: Metadatos profesionales, enlaces de Discord, GitHub y estadísticas.
- `GET /api/services`: Cuatro pilares de servicios (SRE, Minecraft Java 21, IA Soberana, Campus IT).
- `GET /api/projects`: Catálogo enriquecido de proyectos con filtros de categoría.
- `GET /api/telemetry`: Telemetría viva del clúster Star, SAORI Swarm y DrakesCraft.
- `POST /api/contact`: Validación de solicitudes con honeypot antispam y rate limiting.

## Arquitectura de Despliegue

```text
GitHub (JackStar6677-1/jack-portal) -> Star (/opt/stacks/repos/jack-portal)
                                     -> Docker Compose (jack-portal en 127.0.0.1:8082)
                                     -> Cloudflare Tunnel -> jack.drakescraft.cl
```
