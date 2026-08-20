# Beach Office

Mapa interativo com cidadezinhas litorâneas brasileiras para devs remotos que querem morar na praia.

Inspirado em [Dev Remoto na Roça](https://marcos-dev79.github.io/sitedaroca/), mas focado exclusivamente em **municípios defrontantes com o mar** (IBGE 2024).

## Critérios de seleção

- Municípios defrontantes com o mar (IBGE 2024)
- Até 20 mil habitantes (IBGE 2024)
- Entre 20 e 50 km de cidade média (≥150 mil hab.)
- Até 1h30 de cidade grande (≥500 mil hab.)
- UPA no CNES ou emergência 24h municipal
- Escola: estrutura educacional municipal
- Homicídios ≤ 15/100 mil (SIM/DATASUS)

## Build

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install xlrd requests

# Gerar JSON preliminar (sem cache MUNIC/CNES/SIM)
python3 "gerar preliminar.py"

# Gerar JSON completo (precisa de dados em data/cache/)
python3 rebuild_litoraneas.py

# Gerar site
python3 build.py

# Testar localmente
cd dist && python3 -m http.server 8080
```

## Deploy

GitHub Pages via GitHub Actions. Push em `main` → build automático.

## Fontes

- IBGE Municípios Defrontantes com o Mar 2024
- IBGE Estimativas de população 2024
- Atlas IDHM 2010 (PNUD/IPEA/FJP)
- IBGE MUNIC 2021/2023
- SIM/DATASUS
- CNES/DATASUS
