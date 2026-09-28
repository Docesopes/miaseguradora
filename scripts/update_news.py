#!/usr/bin/env python3
"""Actualiza site/news.json con titulares recientes de medios del sector asegurador.
Guarda SOLO titulo, enlace, fuente y fecha (no copia el texto de las notas).
Si ningun feed responde, deja el news.json anterior sin tocar."""
import json, re, sys, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
from pathlib import Path

# Editá esta lista para sumar o quitar medios. Deben ofrecer feed RSS/Atom.
FEEDS = [
    ("100% Seguro", "https://100seguro.com.ar/feed/"),
    ("APASER", "https://www.apaser.com.ar/feed/"),
    ("Prensa Aseguradora", "https://www.prensaaseguradora.com/blog-feed.xml"),
    ("El Seguro en Acción", "https://elseguroenaccion.com.ar/feed/"),
    ("Tiempo de Seguros", "https://www.tiempodeseguros.com.ar/feed/"),
]
KEYWORDS = ["ssn", "superintendencia", "resolucion", "aseguradora", "compania", "inhibi", "prohib",
            "multa", "revoca", "liquidacion", "balance", "solvencia", "ranking", "primas", "mercado asegurador"]
ALERT = ["inhibi", "prohib", "revoca", "liquidacion", "multa", "medida precautoria", "intervenci"]
MAX_ITEMS, MAX_PER_SOURCE, MAX_AGE_DAYS = 8, 3, 60
OUT = Path(__file__).resolve().parent.parent / "site" / "news.json"
MES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

def norm(t):
    return unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "miaseguradora-news-bot/1.0 (+https://miaseguradora.com.ar)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    out = []
    for it in root.iter():
        tag = it.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        g = lambda n: next((c for c in it if c.tag.split("}")[-1] == n), None)
        title, link = g("title"), g("link")
        date = next((x for x in (g("pubDate"), g("published"), g("updated")) if x is not None), None)
        url = (link.get("href") if link is not None and link.get("href") else (link.text if link is not None else "")) or ""
        try:
            d = parsedate_to_datetime(date.text) if date is not None and date.text and "," in date.text else datetime.fromisoformat(date.text.replace("Z", "+00:00"))
            if d.tzinfo is None: d = d.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if title is None or not title.text or not url.startswith(("http://", "https://")):
            continue
        out.append((re.sub(r"\s+", " ", title.text).strip(), url.strip(), d))
    return out

def main():
    now = datetime.now(timezone.utc)
    items, ok = [], 0
    for src, url in FEEDS:
        try:
            got = parse(fetch(url)); ok += 1
            print(f"OK   {src}: {len(got)} notas")
        except Exception as e:
            print(f"FAIL {src}: {e}"); continue
        n = 0
        for t, u, d in sorted(got, key=lambda x: x[2], reverse=True):
            if now - d > timedelta(days=MAX_AGE_DAYS) or not any(k in norm(t) for k in KEYWORDS): continue
            items.append({"title": t, "url": u, "source": src, "date": d.astimezone().date().isoformat(),
                          "date_label": f"{d.day} {MES[d.month-1]} {d.year}"})
            n += 1
            if n >= MAX_PER_SOURCE: break
    if not ok or not items:
        print("Sin datos nuevos: se conserva news.json anterior."); return 0
    seen, final = set(), []
    for i in sorted(items, key=lambda x: x["date"], reverse=True):
        key = norm(i["title"])
        if i["url"] in seen or key in seen: continue
        seen.update([i["url"], key]); final.append(i)
    final = final[:MAX_ITEMS]
    old = json.loads(OUT.read_text(encoding="utf-8")).get("items", []) if OUT.exists() else []
    if [x["url"] for x in old] == [x["url"] for x in final]:
        print("Sin cambios."); return 0
    OUT.write_text(json.dumps({"updated": now.astimezone().strftime("%d/%m/%Y"), "items": final}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"news.json actualizado con {len(final)} notas.")
    for i in final:
        if any(k in norm(i["title"]) for k in ALERT):
            print("REVISAR ESTADO SSN ->", i["title"], i["url"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
