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
    "name": "JackStar",
    "handle": "JackStar6677-1",
    "role": "Systems Engineer · Software & Infrastructure Operator",
    "bio": "Diseño compiladores de AST, software distribuido, infraestructura Linux y orquestación multiagente con foco en trazabilidad, datos protegidos y alta resiliencia.",
    "philosophy": "Ambitious is good. Recoverable is better. Build it beautifully. Explain its state. Keep the rollback close.",
    "links": {
        "github": "https://github.com/JackStar6677-1",
        "drakescraftLabs": "https://github.com/SlimefunNewHorizons",
        "discord": "https://discord.gg/rv3vtXZTk7",
        "drakescraft": "https://web.drakescraft.cl",
        "youtube": "https://www.youtube.com/@jackstar6677",
    },
    "stats": {
        "pluginsMaintained": "100+",
        "gameModes": 6,
        "stagingAddons": "49 Slimefun (S2 - 100% Verificado)",
        "runtime": "Java 21 · Python 3.12 · Linux SRE",
    },
}

SERVICES = [
    {
        "area": "Infraestructura & SRE",
        "title": "Arquitectura y continuidad bare-metal",
        "description": "Servicios Linux en nodo Star VPS, Docker Compose, almacenamiento administrado LVM/RAID, redes privadas WireGuard/Tailscale, túneles Zero Trust Cloudflare y observabilidad.",
        "items": ["Linux Bare-Metal", "Docker & Compose", "Redes privadas WireGuard", "Almacenamiento LVM", "Backups & DR", "Observabilidad"],
    },
    {
        "area": "Ecosistema Minecraft Técnico",
        "title": "Desarrollo Java & Engines Transaccionales",
        "description": "Paper / Purpur 1.21.11, Java 21, Odysseia Engine (idempotencia y entrega Tebex), BentoBox-Drake, 100+ plugins mantenidos y 49 addons Slimefun en staging automatizado.",
        "items": ["Purpur 1.21.11", "Java 21", "Odysseia Engine", "BentoBox-Drake", "Slimefun S2 Staging", "6 Modalidades"],
    },
    {
        "area": "Compiladores & Multiagente",
        "title": "OmniAST & Orquestación SAORI",
        "description": "Compilación universal por grafos AST (Python, Rust, TS, Java) con Hermes y OpenClaw; orquestación multiagente SRE con leases de concurrencia SQLite WAL.",
        "items": ["OmniAST Compiler", "Hermes Agent", "OpenClaw Runtime", "SQLite WAL", "Multi-Agent Swarm", "Automated QA"],
    },
    {
        "area": "Tecnología Aplicada & Multimedia",
        "title": "DSP Streaming 24/7 & Soporte TI",
        "description": "Transmisión procedural 24/7 en YouTube Live con síntesis de audio, CampusCare para monitoreo de laboratorios, CastelCredCam en PySide6 y automatización Veyon.",
        "items": ["DSP 24/7 YouTube", "CampusCare PWA", "CastelCredCam Qt", "VeyonScripts", "Diagnóstico TI", "Reservas Escolares"],
    },
]

PROJECTS = [
    {
        "id": "omniast",
        "name": "OmniAST & Semantic Engine",
        "category": "Compiladores & AST",
        "category_id": "ai",
        "badge": "Universal AST",
        "featured": True,
        "description": "Compilador y transpilador universal multi-lenguaje basado en grafos AST (Python, Rust, TypeScript, Java) con lowering de tipos y preservación semántica sin pérdida, integrado con el agente Hermes y runtime OpenClaw.",
        "tags": ["AST Graph", "Python", "Rust", "TypeScript", "Transpiler", "Hermes Agent"],
        "url": "https://github.com/JackStar6677-1/omniast",
    },
    {
        "id": "star-ambient-stream",
        "name": "Star Ambient DSP Streamer",
        "category": "Multimedia & DSP",
        "category_id": "infra",
        "badge": "Live 24/7 Broadcast",
        "featured": True,
        "description": "Motor autónomo de transmisión procedural 24/7 en Star VPS para YouTube Live. Generación y remasterización DSP con espectrograma en tiempo real, crossfade de 2.0s y diseño foley adaptativo (lluvia, nieve, viento, servidores).",
        "tags": ["Python", "FFmpeg", "DSP", "YouTube Live 24/7", "Docker", "Audio Synthesis"],
        "url": "https://github.com/JackStar6677-1/star-ambient-stream",
    },
    {
        "id": "saori-core",
        "name": "SAORI Core · SRE Swarm",
        "category": "Automatización",
        "category_id": "ai",
        "badge": "Orquestación SRE",
        "featured": True,
        "description": "Orquestador multiagente para trabajo técnico: coordinación de Gemini 3.8 Flash High, Claude Code y OpenAI Codex con bloqueos SQLite WAL (observe, develop, admin), staging de 49 addons y autorrecuperación en tiempo real.",
        "tags": ["Python", "SQLite WAL", "Multi-agent", "Autonomous SRE", "Staging S2"],
        "url": "https://github.com/JackStar6677-1/saori",
    },
    {
        "id": "drakescraft-network",
        "name": "DrakesCraft Network · Temporada 2",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "190 Plugins · 26.2",
        "featured": True,
        "description": "Ecosistema Minecraft en Paper 26.2 y Purpur 1.21.11 (Java 25) con 6 modalidades activas (Survival Slimefun, BSkyBlock, AOneBlock, OneChunk, Clásico, Laboratorio), 190 plugins operativos con 100% de paridad y crossplay Geyser Bedrock.",
        "tags": ["Paper 26.2", "Java 25", "Bedrock Híbrido", "190 Plugins", "6 Modalidades"],
        "url": "https://web.drakescraft.cl",
    },
    {
        "id": "saori-kokoro-audio",
        "name": "SAORI Kokoro TTS & Voice Pipeline",
        "category": "IA Soberana & DSP",
        "category_id": "ai",
        "badge": "Neural Voice DSP",
        "featured": True,
        "description": "Framework de voz neuronal y síntesis de audio autónomo basado en Kokoro ONNX, normalización broadcast EBU R128 (-16 LUFS), ducking dinámico y compresión multibanda para alertas Discord, YouTube Live y SRE dispatch.",
        "tags": ["Python", "Kokoro TTS", "EBU R128", "FFmpeg DSP", "Docker", "Neural Voice"],
        "url": "https://github.com/JackStar6677-1/saori",
    },
    {
        "id": "odysseia-engine",
        "name": "Odysseia Core Engine",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "Engine Central",
        "featured": True,
        "description": "Núcleo transaccional para flujos de tienda Tebex, rangos e inventarios por modalidad, diseñado con entregas idempotentes para evitar duplicaciones de ítems.",
        "tags": ["Java 21", "Paper API", "SQLite", "Tebex API", "Idempotencia"],
        "url": "https://github.com/SlimefunNewHorizons/Odysseia",
    },
    {
        "id": "linux-infrastructure",
        "name": "Infraestructura Star Bare-Metal",
        "category": "Infraestructura & SRE",
        "category_id": "infra",
        "badge": "Clúster Bare-Metal",
        "featured": True,
        "description": "Servicios Linux con contenedores Docker aislados, almacenamiento RAID LVM, red privada WireGuard/Tailscale y túneles seguros Cloudflare Zero Trust.",
        "tags": ["Linux", "Docker Compose", "LVM RAID", "Tailscale", "Cloudflare"],
        "url": "",
    },
    {
        "id": "slimefun-ecosystem",
        "name": "Slimefun S2 Addons Pipeline",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "49 Addons Staging",
        "featured": True,
        "description": "Catálogo de 49 addons y ports de Slimefun actualizados a Purpur 1.21.11 / Java 21, con compilación automatizada y validación continua.",
        "tags": ["Java 21", "Slimefun4", "Purpur", "Compatibilidad", "Staging S2"],
        "url": "https://github.com/SlimefunNewHorizons",
    },
    {
        "id": "labops-tools",
        "name": "Herramientas LabOps (VeyonScripts)",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Soporte TI",
        "featured": True,
        "description": "Herramientas para administración de laboratorios: diagnóstico, mapeo de red, Wake-on-LAN y ejecución remota controlada.",
        "tags": ["PowerShell", "Veyon", "WinRM", "Wake-on-LAN", "Auditoría de Red"],
        "url": "https://github.com/JackStar6677-1/VeyonScripts",
    },
    {
        "id": "data-integrity-forks",
        "name": "Forks de Integridad de Datos",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "Resilient Forks",
        "featured": False,
        "description": "Forks Java centrados en serialización robusta e inventarios aislados para reducir riesgos de pérdida en cambios de modalidad.",
        "tags": ["Java", "Paper Data Components", "Integridad", "Pruebas"],
        "url": "https://github.com/SlimefunNewHorizons/BentoBox-Drake",
    },
    {
        "id": "calendar-platform",
        "name": "Plataforma de calendario",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Plataforma web",
        "featured": False,
        "description": "Plataforma web para calendarios, actividades y reservas con cuentas individuales y sincronización sin compartir credenciales maestras.",
        "tags": ["FastAPI", "PostgreSQL", "OAuth", "PWA", "Reservas"],
        "url": "",
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
        "id": "roomkeeper",
        "name": "Gestión de salas",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Reservas Escolares",
        "featured": False,
        "description": "Sistema de coordinación y reservas de espacios, prevención de colisiones horarias y trazabilidad de solicitudes.",
        "tags": ["PHP", "MySQL", "SMTP Alerts", "Auditoría de Cambios"],
        "url": "",
    },
    {
        "id": "credcam",
        "name": "Herramienta de captura asistida",
        "category": "Tecnología Educativa",
        "category_id": "education",
        "badge": "Desktop Studio",
        "featured": False,
        "description": "Aplicación de escritorio con apoyo de encuadre, importación tabular y copias de resguardo para jornadas de captura.",
        "tags": ["Python", "PySide6", "OpenCV", "CSV", "Backups"],
        "url": "",
    },
    {
        "id": "slimefun-ecosystem",
        "name": "Slimefun Custom Addons Ecosystem",
        "category": "Minecraft Técnico",
        "category_id": "gaming",
        "badge": "15+ Addons Propios",
        "featured": False,
        "description": "Colección y mantenimiento de addons y ports de Slimefun adaptados al runtime Java actual y al equilibrio del servidor.",
        "tags": ["Java", "Slimefun4", "Addons", "Compatibilidad", "Mantenimiento"],
        "url": "https://github.com/SlimefunNewHorizons",
    },
    {
        "id": "saori-omnichannel",
        "name": "SAORI Omnichannel Interfaces",
        "category": "Automatización",
        "category_id": "ai",
        "badge": "Presencia Viva",
        "featured": False,
        "description": "Interfaces de mensajería y presencia para soporte técnico, diseñadas con límites de permisos, trazabilidad y supervisión humana.",
        "tags": ["Mineflayer", "Discord", "Mensajería", "TTS", "Auditoría"],
        "url": "",
    },
    {
        "id": "backup-pipeline",
        "name": "Pipeline de Respaldo Híbrido",
        "category": "Infraestructura & SRE",
        "category_id": "infra",
        "badge": "Resiliencia & DR",
        "featured": False,
        "description": "Automatización de respaldos con verificación, retención y reportes operacionales; los destinos y la topología no se exponen públicamente.",
        "tags": ["Python", "Systemd", "Git", "Verificación", "Reportes"],
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
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; "
                         "form-action 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' "
                         "https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; "
                         "img-src 'self' data: https:; connect-src 'self'")
        if self.path.startswith("/assets/") or self.path.endswith((".png", ".jpg", ".webp", ".svg", ".css", ".js", ".ico")):
            self.send_header("Cache-Control", "public, max-age=86400")
        super().end_headers()

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".xml": "application/xml; charset=utf-8",
        ".webmanifest": "application/manifest+json; charset=utf-8",
    }

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        if code == HTTPStatus.NOT_FOUND:
            not_found_file = ROOT / "404.html"
            if not_found_file.exists():
                content = not_found_file.read_bytes()
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
        super().send_error(code, message, explain)

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
            self.send_json({
                "mode": "reference",
                "disclosure": "Datos representativos y sanitizados; no es telemetría de producción.",
                "architecture": {
                    "runtime": "Linux y servicios contenerizados",
                    "data": "Respaldos verificables y procedimientos de restauración",
                    "network": "Acceso privado y publicación controlada",
                    "automation": "Tareas coordinadas con revisión humana",
                },
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
        if self.path == "/api/analytics/collect":
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            if content_length <= 0 or content_length > MAX_BODY_BYTES:
                self.send_json({"ok": False}, HTTPStatus.BAD_REQUEST)
                return
            try:
                raw = self.rfile.read(content_length).decode("utf-8")
                body = json.loads(raw)
                analytics_file = ROOT / "data" / "analytics.jsonl"
                analytics_file.parent.mkdir(parents=True, exist_ok=True)
                body["ts"] = int(time.time() * 1000)
                body["client_ip"] = (self.client_address[0] if self.client_address else "0.0.0.0").rsplit(".", 1)[0] + ".0"
                body["ua"] = self.headers.get("User-Agent", "")
                with open(analytics_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(body) + chr(10))
                self.send_json({"ok": True})
            except Exception:
                self.send_json({"ok": False}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

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
