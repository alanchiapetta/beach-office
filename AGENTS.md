# Beach Office — Agent Instructions

## Project Overview
Mapa interativo com cidadezinhas litorâneas brasileiras para devs remotos que querem morar na praia. Inspirado em [Dev Remoto na Roça](https://marcos-dev79.github.io/sitedaroca/), mas focado exclusivamente em **municípios defrontantes com o mar** (IBGE 2024).

## Tech Stack
- **Frontend**: HTML + CSS + Leaflet.js (mapa interativo)
- **Backend/Build**: Python 3 (scripts de coleta e build)
- **Data**: IBGE (população, MUNIC, CNES), Atlas IDH 2010, SIM/DATASUS (homicídios)
- **Deploy**: GitHub Pages via GitHub Actions

## Build Commands
```bash
# Gerar JSON de cidades litorâneas (precisa de dados em data/cache/)
python3 rebuild_litoraneas.py

# Gerar site em dist/
python3 build.py

# Testar localmente
cd dist && python3 -m http.server 8080
```

## Project Structure
```
beach-office/
├── assets/
│   ├── css/site.css          # Dark mode + tema praia
│   ├── js/mapa.js            # Leaflet, filtros, popups
│   └── img/
├── data/
│   ├── litoraneas.json       # Municípios costeiros filtrados (gerado)
│   ├── ibge-pop-2024.json    # População IBGE
│   ├── dados2010-ref.csv     # Atlas IDH (lat, lng, altitude)
│   └── cache/                # Bases MUNIC/CNES/SIM (não versionar)
├── dist/                     # Build output (GitHub Pages)
├── build.py                  # Gera dist/
├── rebuild_litoraneas.py     # Cruza lista costeira com dados IBGE
├── rebuild_zonas_crime.py    # Atualiza zonas de crime
├── index.html                # Template HTML
├── README.md
└── AGENTS.md                 # Este arquivo
```

## Key Differences from sitedaroca
- **Universo**: 279 municípios costeiros (IBGE) → ~20-40 filtrados (≤20 mil hab.)
- **Filtro de altitude**: REMOVIDO (litoral = baixa altitude sempre)
- **Tema visual**: Dark com azul-marinho, verde-água, areia
- **Nome**: Beach Office

## Data Sources
- **Municípios costeiros**: IBGE Municípios Defrontantes com o Mar 2024
  - XLS: `https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/municipios_defrontantes_com_o_mar/2024/Municipios_Defrontantes_com_o_Mar_2024.xls`
- **População**: IBGE SIDRA tabela 6579 (estimativas 2024)
- **IDH**: Atlas IDHM 2010 (PNUD/IPEA/FJP)
- **Infraestrutura**: IBGE MUNIC 2021 (saúde, educação) e 2023 (segurança)
- **Homicídios**: SIM/DATASUS (X85–Y09, 2022–2024)
- **UPA/Farmácia**: CNES/DATASUS

## City JSON Schema
```json
{
  "rank": 1,
  "nome": "Cidade",
  "uf": "XX",
  "regiao": "Região",
  "pop": 10000,
  "idh": 0.75,
  "idh_renda": 0.7,
  "idh_longev": 0.85,
  "idh_edu": 0.65,
  "ibge": "0000000",
  "lat": -23.0,
  "lng": -45.0,
  "altitude": 5,
  "cidade_media": "Cidade Média (30 km)",
  "grande_centro": "São Paulo (~45 min, 60 km)",
  "homicidios": 2,
  "homicidios_ano": 2023,
  "taxa_homicidios_100k": 8.5,
  "saude": "UPA municipal; farmácia CNES",
  "educacao": "escola municipal",
  "seguranca": "delegacia civil",
  "infra": {
    "upa_ou_emergencia_24h": true,
    "escola": true,
    "mercado": true,
    "farmacia": true,
    "delegacia": true,
    "correios": true
  },
  "hidden": false,
  "nota": "..."
}
```

## Infrastructure Keys
| Key | Label |
|---|---|
| `upa_ou_emergencia_24h` | 🏥 UPA / emergência |
| `escola` | 🏫 Escola |
| `mercado` | 🛒 Mercado |
| `farmacia` | 💊 Farmácia |
| `delegacia` | 🚓 Delegacia |
| `correios` | 📮 Correios |

## Design Tokens
- Background: `#0f172a` (dark navy)
- Primary: `#0ea5e9` (ocean blue)
- Accent: `#06b6d4` (teal/cyan)
- Sand: `#fbbf24` (amber/gold)
- Success: `#10b981` (green for good IDH)
- Danger: `#ef4444` (red for high violence)

## Rules
- Always test with `python3 build.py` before committing
- Never commit files in `data/cache/` or `dist/`
- Keep Portuguese language for UI text
- Validate data quality: null homicide data is OK (shows "sem série")
- Homicide cap: ≤ 15 per 100k (same as original)
- Population cap: ≤ 20,000 (same as original)
