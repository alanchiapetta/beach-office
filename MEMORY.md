# MEMORY.md — Histórico do Projeto Beach Office

## Objetivo
Mapa interativo com cidadezinhas litorâneas brasileiras para devs remotos que querem morar na praia. Site: `https://alanchiapetta.github.io/beach-office/`

## Origem
Clonado de [Dev Remoto na Roça](https://github.com/marcos-dev79/sitedaroca) — mesmo conceito, mas sitedaroca foca interior/campo, Beach Office foca litoral.

## Critérios de seleção (atuais)
1. Município defrontante com o mar (IBGE 2024)
2. População ≤ 80 mil hab. (IBGE 2024)
3. 20–50 km de cidade média (≥150 mil hab.)
4. Até 1h30 de cidade grande (≥500 mil hab.)
5. UPA ou emergência 24h (MUNIC 2021 ou CNES)
6. Escola (MUNIC 2021)
7. Mortalidade por causas externas ≤ 150/100 mil hab. (saudeemdado/IBGE)
8. Visíveis = UPA + escola; sem esses, `hidden = true`

## Limitação crítica: dados de mortalidade
**NÃO temos dados de homicídios X85-Y09 por município.** Isso é uma limitação real, não técnica.

O que temos:
- **saudeemdado Supabase API** (`https://zekjhmxjamatlxpkykde.supabase.co/rest/v1`):
  - `mart_mortalidade_municipio` → cap. XX (causas externas) por município. ~16k linhas. Não tem causa específica (X85-Y09).
  - `mart_mortalidade_causa` → causa específica (3-char CID) mas só por UF. Não é municipal.
  - `dim_municipio` → mapeamento cod_ibge 6→7 dígitos (5571 municípios)
- Chave API pública: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

O que NÃO funciona:
- **DATASUS/TABNET**: DNS inacessível deste ambiente
- **OpenDataSUS**: DNS inacessível
- **saudeemdado.com.br**: DNS inacessível (mas a API Supabase funciona)
- **IBGE SIDRA**: Acessível mas não tem tabelas de mortalidade por causa+município

### O que tentamos e descartamos
1. **Estimativa via proporção UF**: Baixamos `mart_mortalidade_causa` por UF (proporção X85-Y09 dentro do cap. XX) e aplicamos ao dado municipal. O usuário rejeitou — "dados inventados".
2. **Dados brutos cap. XX como "homicídios"**: Inicialmente rotulamos como homicídios, mas é incorreto. Usuário pediu honestidade.

### Solução atual (definitiva)
Dados reais de **mortalidade por causas externas (cap. XX CID-10)** da API saudeemdado/IBGE. Campos JSON ainda se chamam `homicidios` / `taxa_homicidios_100k` por compatibilidade com código, mas todos os labels do frontend dizem "causas externas" / "óbitos ext./100 mil".

### Se no futuro conseguir dados X85-Y09 municipais
O pipeline aceita dados de homicídio no mesmo formato CSV (`ibge_code,year,homicide_count,homicide_rate_per_100k`). Basta gerar um novo `data/cache/homicidios.csv` com os dados corretos — os nomes de coluna são os mesmos.

## O que foi feito (cronológico)

### 1. Setup inicial
- Clonou sitedaroca, renomeou para beach-office
- Configurou remote SSH (`git@github.com:alanchiapetta/beach-office.git`)
- Setou GitHub Pages source para "GitHub Actions"
- Adaptou HTML/CSS/JS: tema dark, nome "Beach Office", litoral

### 2. Dados geográficos
- Baixou lista de municípios costeiros IBGE 2024 (XLS)
- Cruzei com `dados2010-ref.csv` (Atlas IDH: lat, lng, altitude, IDHM)
- Cruzei com `ibge-pop-2024.json` (população SIDRA 6579)
- Geocodificação por distância: cidades médias (≥150k) e grandes (≥500k) usando distância haversine

### 3. Infraestrutura (MUNIC)
- Baixou MUNIC 2021 XLSX (saúde e educação) e 2023 (segurança)
- Extraiu flags: UPA, escola, delegacia
- CNES (farmácia/mercado): **indisponível** — portal inacessível, download timeout
- Farmácia/mercado usam proxy (pop sede ≥2k + farmácia假設)

### 4. Dados de mortalidade
- Baixou cap. XX de `mart_mortalidade_municipio` via API REST (16.244 linhas, 2022–2024)
- Download em batches de 1000 (API tem limite)
- Mapeamento 6→7 dígitos via `dim_municipio`
- Gerou `data/cache/homicidios.csv`

### 5. Refinamento
- Testou estimativa UF → rejeitado pelo usuário
- Reverteu para dados brutos cap. XX
- Atualizou labels: "homicídios" → "causas externas"
- Ajustou faixas de cor: ≤50 azul, 50–100 amarelo, >100 vermelho
- Atualizou legenda em `build.py`
- Pop. máxima: 20k → 80k (a pedido do usuário, de 11 para 35 cidades)

## Resultado atual
- **35 cidades visíveis** (NE=23, SE=9, S=3, N=0)
- Top IDH: Bombinhas (0.781), Garopaba (0.753), Mangaratiba (0.753)
- Deploy automático via GitHub Actions

## Regra de ouro
> **NUNCA inventar dados.** Se não tem fonte, deixa vazio/n/d. Se o dado é aproximado ou de outro nível geográfico, documentar explicitamente no label.

## Dependências Python
```
openpyxl
requests
```
Virtual env em `.venv/`

## Comandos úteis
```bash
source .venv/bin/activate

# Pipeline completo
python3 rebuild_litoraneas.py   # Gera data/litoraneas.json
python3 build.py                # Gera dist/

# Zonas de crime (separado)
python3 rebuild_zonas_crime.py

# Testar local
cd dist && python3 -m http.server 8080

# Deploy
git push  # GitHub Actions publica automaticamente
```

## Arquivos importantes
| Arquivo | O que faz |
|---|---|
| `rebuild_litoraneas.py` | Pipeline principal: cruza costeiros + IDH + pop + MUNIC + mortalidade |
| `build.py` | Gera HTML em `dist/` a partir de `litoraneas.json` |
| `assets/js/mapa.js` | Leaflet, filtros sidebar, popups, modos de cor |
| `assets/css/site.css` | Tema dark + praia |
| `data/litoraneas.json` | Output: 35 cidades com todos os campos |
| `data/ibge-pop-2024.json` | População por código IBGE 7 dígitos |
| `data/dados2010-ref.csv` | Atlas IDH + coordenadas + altitude |
| `data/cache/homicidios.csv` | Dados brutos cap. XX (saudeemdado API) |
| `data/cache/dim_municipio*` | Mapeamento IBGE 6→7 dígitos |
| `data/cache/munic2021_saude.csv` | MUNIC saúde |
| `data/cache/munic2021_educacao.csv` | MUNIC educação |
| `data/cache/munic2023_seguranca.csv` | MUNIC segurança |
| `data/cache/municipios_costeiros_2024.xls` | Lista IBGE |

## Pendências conhecidas
1. **CNES (farmácia/mercado)**: Dados indisponíveis. `farmacia` sempre false. `mercado` é proxy. Não bloqueia visibilidade mas é impreciso.
2. **Dados X85-Y09**: Se conseguir baixar SIM microdados de outra fonte, pode substituir `homicidios.csv` e ter dados municipais de homicídio reais.
3. **zonas-crime.json**: Gerado por script separado, não atualizado nesta sessão.
