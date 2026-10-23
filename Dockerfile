FROM python:3.12-alpine

WORKDIR /app

# CVE 2026-10 (vuln_watch): pip de la imagen base
RUN pip install --no-cache-dir -U "pip>=25.3"

COPY index.html styles.css script.js server.py sitemap.xml robots.txt 404.html site.webmanifest ./
COPY assets ./assets

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1

CMD ["python", "server.py"]
