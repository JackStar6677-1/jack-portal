from __future__ import annotations

import json
import re
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


APP = "jack-portal"
ENVIRONMENT = "production"
PUBLIC_EMAIL = "pablo.elias.miranda.292003@gmail.com"
ROOT = Path(__file__).resolve().parent
MAX_BODY_BYTES = 8_192
RATE_LIMIT_WINDOW = 60 * 60
RATE_LIMIT_MAX = 5
RATE_LIMIT: dict[str, list[float]] = {}

PROFILE = {
    "name": "Pablo Elías Avendaño Miranda",
    "role": "Ingeniero en Informática",
    "location": "Santiago, Chile",
    "bio": "Construyo y mantengo sistemas reales: sitios, servidores, automatizaciones, calendarios, herramientas internas y soporte técnico.",
    "links": {
        "email": PUBLIC_EMAIL,
        "github": "https://github.com/JackStar6677-1",
        "drakescraftLabs": "https://github.com/DrakesCraft-Labs",
    },
}

SERVICES = [
    {
        "area": "Soporte",
        "title": "Soporte TI y mantención escolar",
        "description": "Soporte operativo para equipos, salas, laboratorios y necesidades técnicas cotidianas.",
        "items": ["computadores", "proyectores", "red", "cableado", "soporte operativo", "herramientas internas"],
    },
    {
        "area": "Software",
        "title": "Desarrollo web y sistemas internos",
        "description": "Sitios, paneles y flujos internos para ordenar información, reservas y coordinación.",
        "items": ["sitios web", "paneles", "calendarios", "reservas", "formularios", "dashboards"],
    },
    {
        "area": "Infraestructura",
        "title": "Servidores e infraestructura",
        "description": "Servicios Linux y Docker con publicación segura, monitoreo, backups y hardening básico.",
        "items": ["Linux", "Docker", "Cloudflare Tunnel", "monitoreo", "backups", "hardening básico"],
    },
    {
        "area": "Automatización",
        "title": "Automatización y scripts",
        "description": "Scripts y pequeñas integraciones para reducir trabajo repetitivo y errores manuales.",
        "items": ["Python", "PowerShell", "reportes", "flujos repetitivos", "integración de APIs"],
    },
    {
        "area": "Gaming técnico",
        "title": "Minecraft técnico / DrakesCraft",
        "description": "Mantenimiento y optimización de servidores Minecraft técnicos y ecosistemas de plugins.",
        "items": ["Paper", "Slimefun", "plugins", "rendimiento", "mantenimiento de servidores"],
    },
]

PROJECTS = [
    {
        "name": "CCAACalendar",
        "category": "Calendarios",
        "description": "Plataforma multicentro para calendarios institucionales, reservas, Google Calendar y coordinación de espacios.",
        "tags": ["FastAPI", "PostgreSQL", "Google Calendar"],
        "url": "https://calendar.drakescraft.cl",
    },
    {
        "name": "CastelRoomKeeper",
        "category": "Reservas",
        "description": "Sistema de calendario y reservas de salas para entorno escolar.",
        "tags": ["Calendario", "Reservas", "Escolar"],
        "url": "",
    },
    {
        "name": "VeyonScripts",
        "category": "Automatización TI",
        "description": "Automatización y diagnóstico para laboratorios con Veyon, escaneo de red y mapeo operativo.",
        "tags": ["PowerShell", "Veyon", "Redes"],
        "url": "https://github.com/JackStar6677-1/VeyonScripts",
    },
    {
        "name": "Castel CredCam",
        "category": "Aplicación local",
        "description": "Aplicación local para captura y preparación de fotos tipo credencial por curso.",
        "tags": ["Local", "Credenciales", "Cursos"],
        "url": "",
    },
    {
        "name": "DrakesCraft Web",
        "category": "Portal público",
        "description": "Portal público del ecosistema DrakesCraft.",
        "tags": ["Web", "Comunidad", "Portal"],
        "url": "https://web.drakescraft.cl",
    },
    {
        "name": "DrakesCraft / Slimefun",
        "category": "Minecraft técnico",
        "description": "Servidor Minecraft técnico con ecosistema de plugins, mantenimiento y ports personalizados.",
        "tags": ["Paper", "Slimefun", "Plugins"],
        "url": "",
    },
]


class Handler(SimpleHTTPRequestHandler):
    server_version = "JackPortal/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        if self.path == "/api/contact":
            print(f"{self.address_string()} - contact request handled")
            return
        super().log_message(format, *args)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self.send_json({"status": "ok", "app": APP, "environment": ENVIRONMENT})
            return
        if self.path == "/api/profile":
            self.send_json({"profile": PROFILE})
            return
        if self.path == "/api/services":
            self.send_json({"services": SERVICES})
            return
        if self.path == "/api/projects":
            self.send_json({"projects": PROJECTS})
            return
        if self.path == "/healthz":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/contact":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not self.rate_limit_ok():
            self.send_json({"error": "Demasiadas solicitudes. Intenta más tarde."}, HTTPStatus.TOO_MANY_REQUESTS)
            return

        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            self.send_json({"error": "Solicitud inválida."}, HTTPStatus.BAD_REQUEST)
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json({"error": "JSON inválido."}, HTTPStatus.BAD_REQUEST)
            return

        error = validate_contact(payload)
        if error:
            self.send_json({"error": error}, HTTPStatus.BAD_REQUEST)
            return

        self.send_json({
            "status": "accepted",
            "delivery": "mailto",
            "message": "Solicitud validada. Usa el correo preparado para enviarla.",
        }, HTTPStatus.ACCEPTED)

    def rate_limit_ok(self) -> bool:
        client = self.client_address[0]
        now = time.time()
        recent = [stamp for stamp in RATE_LIMIT.get(client, []) if now - stamp < RATE_LIMIT_WINDOW]
        if len(recent) >= RATE_LIMIT_MAX:
            RATE_LIMIT[client] = recent
            return False
        recent.append(now)
        RATE_LIMIT[client] = recent
        return True

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def validate_contact(payload: dict[str, Any]) -> str | None:
    if str(payload.get("website", "")).strip():
        return "Solicitud inválida."

    required = {
        "name": 80,
        "email": 120,
        "service": 120,
        "message": 1200,
    }
    for field, max_length in required.items():
        value = str(payload.get(field, "")).strip()
        if not value:
            return "Completa los campos obligatorios."
        if len(value) > max_length:
            return "Uno de los campos supera el largo permitido."

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", str(payload["email"]).strip()):
        return "Ingresa un email válido."

    for optional in ("budget", "urgency"):
        if len(str(payload.get(optional, "")).strip()) > 80:
            return "Uno de los campos opcionales supera el largo permitido."

    return None


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("jack-portal listening on :8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
