# Jack Portal

Portal profesional publico de Pablo Elias Avendano Miranda.

## Objetivo

Presentar servicios tecnicos de desarrollo web, infraestructura, automatizacion,
soporte TI y sistemas internos para colegios, centros, comunidades y pequenas
organizaciones.

## Stack

- Python 3.12 con libreria estandar.
- HTML/CSS/JavaScript sin dependencias de frontend.
- Docker en `127.0.0.1:8082`.

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
