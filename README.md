# Jack Portal

Portfolio tecnico publico de Jack / JackStar.

## Objetivo

Presentar el trabajo real de software, infraestructura, automatizacion y
operacion que sostiene el ecosistema Star, DrakesCraft, Odysseia e IA Hub.

## Stack

- Python 3.12 con libreria estandar.
- HTML/CSS/JavaScript sin dependencias de frontend.
- Docker en `127.0.0.1:8082`.
- Cloudflare Tunnel publica `jack.drakescraft.cl`.

## Endpoints

- `GET /api/health`
- `GET /api/profile`
- `GET /api/services`
- `GET /api/projects`
- `POST /api/contact`

El formulario de contacto valida payload, aplica honeypot y rate limit simple.
No imprime mensajes completos ni credenciales en logs. La entrega queda en modo
`mailto` para evitar hardcodear webhooks o secretos.

## Despliegue

```text
GitHub -> star -> jack-portal en 127.0.0.1:8082 -> Cloudflare Tunnel -> jack.drakescraft.cl
```

El portal se mantiene separado de `drakescraft-web`, CCAACalendar, Vault,
Webmin y paneles privados.

El contenido publico evita rutas internas, credenciales y detalles operativos
que no aportan al portfolio. Los proyectos privados se describen sin exponer
endpoints de administracion.

<!-- Updated for 2026 active baseline maintenance -->
