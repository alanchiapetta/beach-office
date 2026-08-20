# Beach Office — Agent Instructions

## Project Overview
Mapa interativo com cidadezinhas litorâneas brasileiras para devs remotos que querem morar na praia. Inspirado em [Dev Remoto na Roça](https://marcos-dev79.github.io/sitedaroca/), mas focado exclusivamente em **municípios defrontantes com o mar** (IBGE 2024).

## Tech Stack
- **Frontend**: HTML + CSS + Leaflet.js (mapa interativo)
- **Backend/Build**: Python 3 (scripts de coleta e build)
- **Data**: IBGE (população, MUNIC), Atlas IDH 2010, saudeemdado/IBGE (causas externas)
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
│   ├── zonas-crime.json      # 131 zonas de crime (gerado)
│   └── cache/                # Bases baixadas (não versionar)
├── dist/                     # Build output (GitHub Pages)
├── build.py                  # Gera dist/
├── rebuild_litoraneas.py     # Cruza lista costeira com dados IBGE
├── rebuild_zonas_crime.py    # Atualiza zonas de crime
├── index.html                # Template HTML
├── MEMORY.md                 # Histórico detalhado do projeto
├── README.md
└── AGENTS.md                 # Este arquivo
```

## Key Differences from sitedaroca
- **Universo**: 280 municípios costeiros (IBGE) → 35 filtrados (≤80 mil hab.)
- **Filtro de altitude**: REMOVIDO (litoral = baixa altitude sempre)
- **Tema visual**: Dark com azul-marinho, verde-água, areia
- **Nome**: Beach Office
- **Dados de mortalidade**: Dados reais de causas externas (cap. XX CID-10) da API saudeemdado/IBGE — NÃO são homicídios X85-Y09 específicos (ver MEMORY.md para limitações)

## Data Sources
- **Municípios costeiros**: IBGE Municípios Defrontantes com o Mar 2024
  - XLS: `https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/municipios_defrontantes_com_o_mar/2024/Municipios_Defrontantes_com_o_Mar_2024.xls`
- **População**: IBGE SIDRA tabela 6579 (estimativas 2024)
- **IDH**: Atlas IDHM 2010 (PNUD/IPEA/FJP)
- **Infraestrutura**: IBGE MUNIC 2021 (saúde, educação) e 2023 (segurança)
- **Mortalidade por causas externas**: saudeemdado/IBGE (cap. XX CID-10, 2022–2024)
- **UPA/Farmácia**: CNES/DATASUS (indisponível — dados pendentes)

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
  "homicidios": 17,
  "homicidios_ano": 2024,
  "taxa_homicidios_100k": 90.3,
  "saude": "emergência 24h municipal (IBGE MUNIC); ...",
  "educacao": "órgão de educação: Secretaria exclusiva; ...",
  "seguranca": "mortalidade por causas externas 90.3/100 mil hab. (...); delegacia...",
  "infra": {
    "upa_ou_emergencia_24h": true,
    "escola": true,
    "mercado": false,
    "farmacia": false,
    "delegacia": true,
    "correios": true
  },
  "hidden": false,
  "nota": "IDH 0.718 (Atlas 2010); causas externas 90.3/100 mil (2024); validar comércio e Correios no local"
}
```

**Importante**: Os campos `homicidios`, `taxa_homicidios_100k` e `homicidios_ano` contêm dados reais de **causas externas (cap. XX)** — incluem acidentes, suicídios, agressões — e NÃO apenas homicídios X85-Y09. Labels no frontend já foram atualizados para refletir isso.

## Infrastructure Keys
| Key | Label |
|---|---|
| `upa_ou_emergencia_24h` | 🏥 UPA / emergência |
| `escola` | 🏫 Escola |
| `mercado` | 🛒 Mercado |
| `farmacia` | 💊 Farmácia |
| `delegacia` | 🚓 Delegacia |
| `correios` | 📮 Correios |

**Nota sobre farmácia/mercado**: Sem dados do CNES, `farmacia` sempre é false. `mercado` é proxy (sede ≥2 mil hab. + farmácia). `correios` é proxy (sede ≥2 mil hab.). Esses flags NÃO bloqueiam visibilidade.

## Filtros de visibilidade
Uma cidade só aparece no mapa se tiver:
- UPA ou emergência 24h
- Escola
Se faltar qualquer um dos dois, `hidden = true`.

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
- **NUNCA inventar dados** — se não tem fonte, deixa vazio/n/d
- Population cap: ≤ 80,000
- Mortality data: cap. XX CID-10 real da API saudeemdado/IBGE
- Faixas de cor no mapa: ≤50 azul, 50–100 amarelo, >100 vermelho (por 100 mil hab.)
