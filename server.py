from __future__ import annotations

import json
import os
import re
import time
import uuid
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

APP = "jack-portal"
ENVIRONMENT = "production"
PUBLIC_EMAIL = "pablo.elias.miranda.292003@gmail.com"
ROOT = Path(__file__).resolve().parent
# The web container has no SMTP credentials. It can only create a durable,
# private envelope here; the host-side relay is the only process allowed to
# consume it and use SAORI's existing mail configuration.
CONTACT_QUEUE_DIR = Path(os.environ.get("CONTACT_QUEUE_DIR", "/app/contact-queue"))
MAX_BODY_BYTES = 8_192
RATE_LIMIT_WINDOW = 60 * 60
RATE_LIMIT_MAX = 5
RATE_LIMIT: dict[str, list[float]] = {}
SERVER_START_TIME = time.time()

PROFILE = {
    "name": "Jack / JackStar",
    "handle": "JackStar6677-1",
    "role": "Systems Engineer · Infrastructure Operator · Full-Stack Builder & Sovereign AI Creator",
    "location": "Chile",
    "bio": "Construyo arquitecturas de alta resiliencia, plataformas educativas, clusters de servidores físicos e inteligencia artificial autónoma que sobrevive a la producción.",
    "philosophy": "Ambitious is good. Recoverable is better. Build it beautifully. Explain its state. Keep the rollback close.",
    "links": {
        "email": PUBLIC_EMAIL,
        "github": "https://github.com/JackStar6677-1",
        "drakescraftLabs": "https://github.com/DrakesCraft-Labs",
        "discord": "https://discord.gg/rv3vtXZTk7",
        "drakescraft": "https://web.drakescraft.cl",
    },
    "stats": {
        "pluginsMaintained": "100+",
        "gameModes": 5,
        "clusterNodes": ["Star", "Nexus", "Nova"],
        "aiSwarm": ["Antigravity Gemini 3.8 Flash High", "Claude Code", "OpenAI Codex"],
        "runtime": "Java 21 / Python 3.12 / Linux SRE",
    },
}

SERVICES = [
    {
        "area": "Infraestructura & SRE",
        "title": "Arquitectura y Continuidad Operativa",
        "description": "Servidores bare-metal Linux, virtualización Docker, redes malladas Tailscale, almacenamiento LVM y pipelines de recuperación ante desastres.",
        "items": ["Linux SRE", "Docker & Compose", "Cloudflare Tunnels", "LVM RAID", "Backups Multi-Tier", "Observabilidad"],
    },
    {
        "area": "Ecosistema Minecraft Técnico",
        "title": "Desarrollo de Alta Concurrencia en Java 21",
        "description": "Red DrakesCraft con 5 modalidades, mitigación zero-loss de items, transacciones idempotentes Tebex y mantenimiento de más de 100 plugins.",
        "items": ["Paper / Purpur 1.21.11", "Java 21", "Odysseia Engine", "BentoBox-Drake", "Slimefun Ecosystem", "Economía Balanceada"],
    },
    {
        "area": "Inteligencia Artificial Soberana",
        "title": "Orquestación Multiagente & Automatización",
        "description": "SAORI Core: enjambre de agentes autónomos coordinados bajo leases de concurrencia SQLite WAL con interfaces omnicanal de voz y texto.",
        "items": ["Antigravity Gemini 3.8", "Claude Code", "OpenAI Codex", "Mineflayer Bot", "Discord AI", "WhatsApp Voice AI"],
    },
    {
        "area": "Tecnología Educativa & Campus IT",
        "title": "Sistemas Institucionales y de Laboratorio",
        "description": "Herramientas de diagnóstico para aulas, plataformas de calendarios sin compartir credenciales maestras y automatización de capturas escolares.",
        "items": ["Castel LabOps", "Veyon Automation", "CEMPUDLA PWA", "CastelRoomKeeper", "CredCam PySide6", "WinRM Remoting"],
    },
]

PROJECTS = [
    {
        "id": "saori-core",
        "name": "SAORI Core",
        "category": "IA Soberana",
        "category_id": "ai",
        "badge": "SRE Swarm",
        "featured": True,
        "description": "Sistema operativo multiagente que orquesta Google Antigravity (Gemini 3.8 Flash High), Claude Code y OpenAI Codex con leases de concurrencia SQLite WAL (observe, develop, admin) y autorrecuperación en tiempo real.",
        "tags": ["Python", "SQLite WAL", "Multi-Agent", "Autonomous SRE", "Gemini 3.8 High"],
        "url": "https://github.com/JackStar6677-1/saori",
    },
    {
        "id": "drakescraft-network",
        "name": "DrakesCraft Network",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "Producción",
        "featured": True,
        "description": "Red masiva de alta concurrencia con 5 modalidades activas (Survival, OneBlock, SkyBlock, Vanilla, Lab), Paper/Purpur 1.21.11, soporte híbrido Java & Bedrock y más de 100 plugins optimizados.",
        "tags": ["Paper 1.21.11", "Java 21", "Bedrock Híbrido", "Purpur", "5 Modalidades"],
        "url": "https://web.drakescraft.cl",
    },
    {
        "id": "odysseia-engine",
        "name": "Odysseia Core Engine",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "Engine Central",
        "featured": True,
        "description": "Motor transaccional propietario para DrakesCraft con pasarela Tebex, entregas idempotentes de kits, jerarquía de rangos y aislamiento de inventarios cross-modality.",
        "tags": ["Java 21", "Paper API", "SQLite", "Tebex API", "Idempotencia"],
        "url": "https://github.com/DrakesCraft-Labs/Odysseia",
    },
    {
        "id": "star-cluster",
        "name": "Star Production Cluster",
        "category": "Infraestructura & SRE",
        "category_id": "infra",
        "badge": "Homelab Bare-Metal",
        "featured": True,
        "description": "Centro de cómputo físico (Star, Nexus, Nova) con almacenamiento LVM distribuido en NVMe y HDD, red mallada privada Tailscale, microservicios Docker y túneles Cloudflare sin puertos expuestos.",
        "tags": ["Linux Ubuntu", "Docker Compose", "LVM RAID", "Tailscale", "Cloudflare"],
        "url": "",
    },
    {
        "id": "castel-labops",
        "name": "Castel LabOps (VeyonScripts)",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Campus IT",
        "featured": True,
        "description": "Suite operativa para la administración de laboratorios de computación escolares con Veyon, escaneo y mapeo dinámico de red, Wake-on-LAN y ejecución remota WinRM.",
        "tags": ["PowerShell", "Veyon", "WinRM", "Wake-on-LAN", "Auditoría de Red"],
        "url": "https://github.com/JackStar6677-1/VeyonScripts",
    },
    {
        "id": "bentobox-invswitcher",
        "name": "BentoBox-Drake & InvSwitcher-Drake",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "Resilient Forks",
        "featured": False,
        "description": "Forks de ingeniería custom blindados contra pérdida de items mediante Paper Data Components nativos y aislamiento estricto de 5 inventarios, EnderChests y puntos de experiencia.",
        "tags": ["Java 21", "Paper Data Components", "Zero-Loss", "Hardened Security"],
        "url": "https://github.com/DrakesCraft-Labs/BentoBox-Drake",
    },
    {
        "id": "cempudla-platform",
        "name": "CEMPUDLA",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Plataforma Institucional",
        "featured": False,
        "description": "Plataforma multicentro para calendarios de centros de estudiantes, actividades y reservas con autenticación individual por RUT y sincronización OAuth con Google Calendar sin compartir credenciales maestras.",
        "tags": ["FastAPI", "PostgreSQL", "Google OAuth", "PWA", "RUT Auth"],
        "url": "https://cempudla.drakescraft.cl",
    },
    {
        "id": "campuscare-monitoring",
        "name": "CampusCare Monitoring",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Monitoreo",
        "featured": False,
        "description": "Sistema de monitoreo inteligente de dispositivos, métricas de hardware y mapeo físico espacial para laboratorios escolares con arquitectura PWA y soporte offline.",
        "tags": ["Python", "PWA", "PostgreSQL", "Mapeo Físico", "REST API"],
        "url": "",
    },
    {
        "id": "castel-roomkeeper",
        "name": "CastelRoomKeeper",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Reservas Escolares",
        "featured": False,
        "description": "Sistema de coordinación y reservas de salas de computación y espacios escolares, prevención de colisiones horarias, trazabilidad de solicitudes y notificaciones SMTP.",
        "tags": ["PHP", "MySQL", "SMTP Alerts", "Auditoría de Cambios"],
        "url": "",
    },
    {
        "id": "castel-credcam",
        "name": "CastelCredCam",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Desktop Studio",
        "featured": False,
        "description": "Aplicación de escritorio en PySide6/Qt para jornadas masivas de fotografía escolar tipo credencial, con detección y reencuadre facial automático, rosters Excel/CSV y copias espejo seguras.",
        "tags": ["Python", "PySide6 Qt", "OpenCV", "CSV Rosters", "Mirror Backups"],
        "url": "",
    },
    {
        "id": "slimefun-ecosystem",
        "name": "Slimefun Custom Addons Ecosystem",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "15+ Addons Propios",
        "featured": False,
        "description": "Colección y mantenimiento de más de 15 addons y ports personalizados de Slimefun (Quaptics, NetworksV6, SlimeTinker, SF-BetterChests, MagicXpansion, Galactifun) adaptados a Java 21 y balanceados para alta concurrencia.",
        "tags": ["Java 21", "Slimefun4", "Quaptics", "NetworksV6", "SlimeTinker"],
        "url": "https://github.com/DrakesCraft-Labs",
    },
    {
        "id": "saori-omnichannel",
        "name": "SAORI Omnichannel Interfaces",
        "category": "IA Soberana",
        "category_id": "ai",
        "badge": "Presencia Viva",
        "featured": False,
        "description": "Capas de interacción para SAORI: presencia viva como avatar in-game en Minecraft (Mineflayer), bot de soporte y tickets en Discord, y agente en WhatsApp con transcripción de audios y síntesis de voz ElevenLabs.",
        "tags": ["Mineflayer", "Discord.js", "WhatsApp Web", "ElevenLabs TTS", "Whisper"],
        "url": "",
    },
    {
        "id": "backup-pipeline",
        "name": "Pipeline de Respaldo Híbrido",
        "category": "Infraestructura & SRE",
        "category_id": "infra",
        "badge": "Resiliencia & DR",
        "featured": False,
        "description": "Automatización multi-tier con systemd timers para respaldos nocturnos incrementales a GitHub y sincronización masiva semanal del servidor completo (mundos, configs y bases de datos) hacia Google Drive con reportes a Discord.",
        "tags": ["Python", "Systemd Timers", "Google Drive API", "Git", "Discord Webhooks"],
        "url": "",
    },
    {
        "id": "star-monitor",
        "name": "Star Monitor & Observabilidad",
        "category": "Infraestructura & SRE",
        "category_id": "infra",
        "badge": "Telemetría",
        "featured": False,
        "description": "Sistema ligero de observabilidad de solo lectura para supervisar la salud de contenedores Docker, latencia de red, carga de CPU/RAM y estado de servicios críticos con base de datos SQLite.",
        "tags": ["Python", "SQLite", "Healthcheck", "Alertas", "Uptime"],
        "url": "",
    },
]


class Handler(SimpleHTTPRequestHandler):
    server_version = "JackPortal/2.0"

    def end_headers(self) -> None:
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        super().end_headers()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        if self.path.startswith("/api/"):
            return
        super().log_message(format, *args)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self.send_json({"status": "ok", "app": APP, "environment": ENVIRONMENT, "uptime_sec": int(time.time() - SERVER_START_TIME)})
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
        if self.path == "/api/telemetry":
            uptime = int(time.time() - SERVER_START_TIME)
            self.send_json({
                "cluster": {
                    "master": "Star",
                    "nodes": ["Star", "Nexus", "Nova"],
                    "status": "OPERATIONAL",
                    "uptime_sec": uptime,
                    "storage": "LVM (NVMe + HDD)",
                    "network": "Tailscale Mesh + Cloudflare Edge",
                },
                "saori_swarm": {
                    "state": "ACTIVE",
                    "primary_dev": "Antigravity (Gemini 3.8 Flash High)",
                    "architect": "Claude Code",
                    "integrator_qa": "Codex GPT-5.6",
                    "locking": "SQLite WAL Mutex",
                },
                "drakescraft": {
                    "version": "Paper / Purpur 1.21.11 (Java 21)",
                    "game_modes": 5,
                    "plugins_count": "100+",
                    "slimefun_status": "Hardened & Optimized",
                },
                "timestamp": time.time(),
            })
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

        try:
            contact_id = persist_contact(payload)
        except OSError:
            # Do not claim success when the durable queue is unavailable.
            self.send_json({
                "error": "El sistema de entrega no está disponible. Tu solicitud no fue guardada; intenta nuevamente más tarde.",
            }, HTTPStatus.SERVICE_UNAVAILABLE)
            return

        self.send_json({
            "status": "queued",
            "delivery": "durable-queue",
            "id": contact_id,
            "message": "Tu solicitud fue guardada y será entregada al equipo.",
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


def persist_contact(payload: dict[str, Any]) -> str:
    """Atomically enqueue a validated request for the host-only mail relay.

    An HTTP 202 is returned only after ``os.replace`` has made the envelope
    visible as ``*.pending.json``. A crash can therefore leave a request queued
    for retry, but never report a contact as delivered without storing it.
    """
    contact_id = uuid.uuid4().hex
    envelope = {
        "schema": 1,
        "id": contact_id,
        "created_at": int(time.time()),
        "name": str(payload["name"]).strip(),
        "email": str(payload["email"]).strip(),
        "service": str(payload["service"]).strip(),
        "budget": str(payload.get("budget", "")).strip(),
        "urgency": str(payload.get("urgency", "")).strip(),
        "message": str(payload["message"]).strip(),
    }
    pending_dir = CONTACT_QUEUE_DIR / "pending"
    pending_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = pending_dir / f"{contact_id}.pending.json"
    temporary = pending_dir / f".{contact_id}.tmp"

    try:
        with temporary.open("x", encoding="utf-8") as handle:
            os.chmod(temporary, 0o600)
            json.dump(envelope, handle, ensure_ascii=False, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return contact_id


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("jack-portal listening on :8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
