#!/usr/bin/env python3
"""Build do site Beach Office para publicação."""

import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
DATA_SRC = ROOT / "data" / "litoraneas.json"
CRIME_SRC = ROOT / "data" / "zonas-crime.json"
ASSETS = ROOT / "assets"

SITE_NAME = "Beach Office"
SITE_DESC = (
    "Cidadezinhas litorâneas para dev remoto — dados do IBGE, Atlas IDH e SIM/DATASUS."
)
SITE_URL = ""


def load_cities():
    with open(DATA_SRC, encoding="utf-8") as f:
        return json.load(f)


def load_crime() -> list:
    if not CRIME_SRC.exists():
        return []
    with open(CRIME_SRC, encoding="utf-8") as f:
        payload = json.load(f)
    return payload.get("zonas_crime") or []


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def nav() -> str:
    return """<nav class="site-nav">
  <a class="brand" href="index.html">🏖️ <span>Beach Office</span></a>
</nav>"""


def head(title: str, desc: str = SITE_DESC, page: str = "index", css_href: str = "assets/css/site.css") -> str:
    url = f"{SITE_URL}/{page}.html" if SITE_URL else ""
    og = f'<meta property="og:url" content="{url}">' if url else ""
    return f"""<meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#0c1524">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  {og}
  <meta property="og:locale" content="pt_BR">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏖️</text></svg>">
  <link rel="stylesheet" href="{css_href}">"""


def cities_script(cities: list) -> str:
    payload = json.dumps(cities, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")
    return f"<script>window.CIDADEZINHAS={payload};</script>"


def crime_script(zones: list) -> str:
    payload = json.dumps(zones, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")
    return f"<script>window.ZONAS_CRIME={payload};</script>"


def footer(total: int) -> str:
    return f"""<footer class="site-footer">
  <p>🏖️ Beach Office · Dados: IBGE 2024, Atlas IDH 2010 · Mapa interativo com {total} municípios litorâneos</p>
</footer>"""


def build_index(stats: dict, cities: list, crime_zones: list, css_href: str, js_href: str) -> str:
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  {head(SITE_NAME, page="index", css_href=css_href)}
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">
</head>
<body>
  {nav()}

  <header class="map-header">
    <h1>Top {stats["total"]} Cidadezinhas para Dev Remoto no Litoral</h1>
    <p>Apenas municípios defrontantes com o mar. Até 20 mil hab., 20–50 km de cidade média (≥150 mil), até 1h30 de cidade grande (≥500 mil). UPA/emergência no conjunto. Homicídios ≤ 15/100 mil. Ordenado por IDH. Marque um serviço para exigir que a cidade o tenha.</p>
    <div class="map-stats">
      <span class="stat">Total: {stats["total"]}</span>
      <span class="stat">NE: {stats["ne"]}</span>
      <span class="stat">SE: {stats["se"]}</span>
      <span class="stat">S: {stats["s"]}</span>
      <span class="stat">N: {stats["n"]}</span>
    </div>
    <p class="map-disclaimer">Isto não é um conselho profissional. Faça sua própria pesquisa.</p>
  </header>

  <div class="map-wrap">
    <div id="map-loading" class="map-loading">Carregando mapa…</div>
    <div id="map"></div>
    <aside class="map-sidebar" id="map-controls" aria-label="Filtros do mapa">
      <div class="sidebar-header">
        <strong>Filtros</strong>
        <button class="sidebar-close" id="sidebar-close" type="button" aria-label="Recolher filtros">✕</button>
      </div>
      <div class="sidebar-body">
        <input type="search" id="search" placeholder="Buscar cidade, UF ou região…" aria-label="Buscar cidade">

        <div class="filter-group">
          <span class="filter-label" id="label-regiao">Região</span>
          <div class="filter-chips" role="group" aria-labelledby="label-regiao">
            <button class="chip active" data-regiao="all" type="button">Todas</button>
            <button class="chip" data-regiao="Nordeste" type="button">Nordeste</button>
            <button class="chip" data-regiao="Sudeste" type="button">Sudeste</button>
            <button class="chip" data-regiao="Sul" type="button">Sul</button>
            <button class="chip" data-regiao="Norte" type="button">Norte</button>
          </div>
        </div>

        <div class="filter-group">
          <span class="filter-label" id="label-infra">Serviços exigidos</span>
          <div class="infra-filters" role="group" aria-labelledby="label-infra">
            <label><input type="checkbox" data-infra="upa_ou_emergencia_24h" checked> 🏥 UPA / emergência</label>
            <label><input type="checkbox" data-infra="escola"> 🏫 Escola</label>
            <label><input type="checkbox" data-infra="mercado"> 🛒 Mercado</label>
            <label><input type="checkbox" data-infra="farmacia"> 💊 Farmácia</label>
            <label><input type="checkbox" data-infra="delegacia"> 🚓 Delegacia</label>
            <label><input type="checkbox" data-infra="correios"> 📮 Correios</label>
          </div>
        </div>

        <div class="filter-group">
          <span class="filter-label" id="label-cor">Colorir pinos por</span>
          <div class="filter-chips" role="group" aria-labelledby="label-cor">
            <button class="chip active" data-cor="regiao" type="button" aria-pressed="true">Região</button>
            <button class="chip" data-cor="idh" type="button" aria-pressed="false">IDH</button>
            <button class="chip" data-cor="violencia" type="button" aria-pressed="false">Violência</button>
          </div>
        </div>

        <button class="chip chip-crime" id="toggle-crime" type="button" aria-pressed="false">Zonas de Crime</button>

        <div class="sidebar-footer">
          <p class="result-count" role="status">
            <strong id="visible-count">{stats["total"]}</strong> de
            <span id="total-count">{stats["total"]}</span> cidades no mapa
          </p>
          <p class="empty-state" id="empty-state" hidden>
            Nenhuma cidade atende a todos os filtros. Desmarque um serviço ou volte para "Todas" as regiões.
          </p>
          <div class="sidebar-actions">
            <button class="btn-mini" id="clear-filters" type="button">Limpar filtros</button>
            <button class="btn-mini" id="copy-link" type="button">Copiar link</button>
          </div>
        </div>
      </div>
    </aside>

    <button class="sidebar-toggle" id="sidebar-toggle" type="button"
            aria-controls="map-controls" aria-expanded="true">
      <span aria-hidden="true">☰</span> Filtros
    </button>

    <div class="map-legend" id="map-legend"></div>
  </div>

  {footer(stats["total"])}
  <script>
    if ("serviceWorker" in navigator) {{
      navigator.serviceWorker.getRegistrations().then(function (rs) {{
        rs.forEach(function (r) {{ r.unregister(); }});
      }});
    }}
  </script>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
  __CITIES_SCRIPT__
  __CRIME_SCRIPT__
  <script src="{js_href}"></script>
</body>
</html>"""
    return (
        html.replace("__CITIES_SCRIPT__", cities_script(cities)).replace(
            "__CRIME_SCRIPT__", crime_script(crime_zones)
        )
    )


def build_404(total: int, css_href: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  {head("Página não encontrada — " + SITE_NAME, css_href=css_href)}
</head>
<body>
  {nav()}
  <div class="error-page">
    <h1>404</h1>
    <p>Esta página não existe.</p>
    <a href="index.html" class="btn btn-primary">Voltar ao início</a>
  </div>
  {footer(total)}
</body>
</html>"""


def stats_from(cities: list) -> dict:
    reg = Counter(c["regiao"] for c in cities)
    return {
        "total": len(cities),
        "ne": reg.get("Nordeste", 0),
        "se": reg.get("Sudeste", 0),
        "s": reg.get("Sul", 0),
        "n": reg.get("Norte", 0),
        "co": reg.get("Centro-Oeste", 0),
    }


def main():
    payload = load_cities()
    cities = payload["cidadezinhas"]
    crime_zones = load_crime()
    stats = stats_from(cities)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "assets" / "css").mkdir(parents=True)
    (DIST / "assets" / "js").mkdir(parents=True)
    (DIST / "data").mkdir()

    css_hash = file_hash(ASSETS / "css" / "site.css")
    js_hash = file_hash(ASSETS / "js" / "mapa.js")
    css_name = f"site.{css_hash}.css"
    js_name = f"mapa.{js_hash}.js"
    css_href = f"assets/css/{css_name}"
    js_href = f"assets/js/{js_name}"
    shutil.copy2(ASSETS / "css" / "site.css", DIST / "assets" / "css" / css_name)
    shutil.copy2(ASSETS / "js" / "mapa.js", DIST / "assets" / "js" / js_name)
    shutil.copy2(DATA_SRC, DIST / "data" / "litoraneas.json")
    if CRIME_SRC.exists():
        shutil.copy2(CRIME_SRC, DIST / "data" / "zonas-crime.json")

    (DIST / "index.html").write_text(
        build_index(stats, cities, crime_zones, css_href, js_href), encoding="utf-8"
    )
    (DIST / "404.html").write_text(build_404(stats["total"], css_href), encoding="utf-8")
    (DIST / ".nojekyll").touch()
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")

    print(f"Site gerado em: {DIST}")
    print(f"  index.html, 404.html")
    print(f"  {stats['total']} cidades | NE={stats['ne']} SE={stats['se']} S={stats['s']} N={stats['n']}")


if __name__ == "__main__":
    main()
