#!/usr/bin/env python3
"""Deliver private portal contacts through SAORI's host-side SMTP notifier.

This program deliberately runs on Star, never in the web container.  A failed
SMTP attempt keeps its ``.pending.json`` envelope intact, so delivery retries do
not lose a visitor's request.  It never prints contact contents to logs.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable

QUEUE_DIR = Path(os.environ.get("CONTACT_QUEUE_DIR", "/opt/stacks/state/jack-portal-contact"))
NOTIFIER_PATH = Path(os.environ.get("SAORI_NOTIFIER", "/home/jack/ai-hub/scripts/saori_notificar.py"))
RETENTION_SECONDS = int(os.environ.get("CONTACT_RETENTION_DAYS", "30")) * 86_400


def load_mailer() -> Callable[[str, str, str], bool]:
    """Load the existing SAORI sender without importing any secrets here."""
    spec = importlib.util.spec_from_file_location("saori_notificar", NOTIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar el notificador de SAORI.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sender = getattr(module, "enviar_correo", None)
    if not callable(sender):
        raise RuntimeError("El notificador de SAORI no expone enviar_correo().")
    return sender


def read_envelope(path: Path) -> dict[str, Any]:
    """Reject malformed queue files instead of passing arbitrary data to mail."""
    data = json.loads(path.read_text(encoding="utf-8"))
    required = ("id", "name", "email", "service", "message")
    if not isinstance(data, dict) or any(not isinstance(data.get(key), str) or not data[key].strip() for key in required):
        raise ValueError("Envelope de contacto inválido")
    return data


def make_message(data: dict[str, Any]) -> tuple[str, str]:
    """Produce plain text only; user input is never executed or interpreted."""
    subject = f"[Jack Portal] Nueva solicitud: {data['service'][:80]}"
    body = "\n".join((
        "Nueva solicitud recibida desde jack.drakescraft.cl",
        f"ID: {data['id']}",
        f"Nombre: {data['name']}",
        f"Email: {data['email']}",
        f"Servicio: {data['service']}",
        f"Presupuesto: {data.get('budget') or 'No indicado'}",
        f"Urgencia: {data.get('urgency') or 'No indicada'}",
        "",
        "Mensaje:",
        data["message"],
    ))
    return subject, body


def move_to(path: Path, directory: str, suffix: str) -> None:
    destination = QUEUE_DIR / directory
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    shutil.move(str(path), destination / path.name.replace(".pending.json", suffix))


def purge_sent(now: float) -> None:
    sent_dir = QUEUE_DIR / "sent"
    if not sent_dir.is_dir():
        return
    for path in sent_dir.glob("*.sent.json"):
        try:
            if now - path.stat().st_mtime > RETENTION_SECONDS:
                path.unlink()
        except OSError:
            continue


def deliver_pending() -> int:
    """Attempt every pending envelope once; return nonzero while work remains."""
    pending_dir = QUEUE_DIR / "pending"
    pending_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    purge_sent(time.time())
    pending = sorted(pending_dir.glob("*.pending.json"))
    if not pending:
        return 0

    try:
        sender = load_mailer()
    except Exception as error:
        print(f"[WARN] relay no disponible: {type(error).__name__}", file=sys.stderr)
        return 1

    failed = False
    for path in pending:
        try:
            data = read_envelope(path)
            subject, body = make_message(data)
            if sender("saori", subject, body):
                move_to(path, "sent", ".sent.json")
                print(f"[INFO] contacto {data['id']} entregado")
            else:
                failed = True
                print(f"[WARN] contacto {data['id']} queda pendiente", file=sys.stderr)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            failed = True
            try:
                move_to(path, "failed", ".failed.json")
            except OSError:
                pass
            print(f"[WARN] envelope inválido aislado: {type(error).__name__}", file=sys.stderr)
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Procesa la cola una vez (modo systemd).")
    parser.parse_args()
    return deliver_pending()


if __name__ == "__main__":
    raise SystemExit(main())
