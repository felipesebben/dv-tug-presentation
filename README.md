# dv-tug-presentation

Data pipeline for a Tableau User Group (TUG) presentation on gestalt/UX heuristics
in dashboard design. Sources public Brazilian health data (SUS hospitalizations +
hospital bed capacity) and produces a Tableau `.hyper` file. The plan: build this
pipeline and a dashboard briefing, produce an intentionally poor first-version
dashboard from it, then have two UXer co-presenters redesign it principle-by-principle
for the talk.

## Data

- **Source**: [Base dos Dados](https://basedosdados.org/) (public BigQuery datasets)
- **Hospitalizations**: `br_ms_sih.aihs_reduzidas` (SIH-SUS, AIH reduzida records)
- **Bed capacity**: `br_ms_cnes.leito` (CNES)
- **Scope**: Rio Grande do Sul (RS), 2019-2023
- **Occupancy rate** = total bed-days used ÷ (bed count × days in month), joined by
  hospital/month. This is DATASUS's documented approximation, not a true point-in-time
  occupancy rate — values can exceed 100% (bed turnover within a month, etc.). Flag
  this caveat wherever the metric is shown.
- Base dos Dados' free tier lags ~6 months behind current data.

See `CLAUDE.md` for the full data-profiling notes (dead columns, join-key gotchas,
dictionary tables, etc.).

### Tableau data model

`data/refined/sih_cnes_rs.hyper` holds three tables at three different grains. In
Tableau they're connected as **one data source using Relationships** (the logical/
noodle layer, Tableau 2020.2+) on `id_estabelecimento_cnes` + `ano_mes` — **not**
physical Joins. `hospitalizacoes` (one row per admission) and `leitos` (one row per
hospital×month×bed-type) don't share a grain, so a physical join between them would
fan out and silently inflate every sum; `occupancy` is already pre-aggregated to
hospital×month and acts as the safe anchor table. Relationships let each sheet query
only the table(s) its fields need, at that table's native grain, which is also what
makes filters cascade correctly across all three tables from a single V1 dashboard tab.

```mermaid
erDiagram
    OCCUPANCY {
        string id_estabelecimento_cnes PK
        date ano_mes PK
        string nome_municipio
        string nome_uf
        int total_internacoes
        int leitos_total
        float taxa_ocupacao
    }
    HOSPITALIZACOES {
        string id_estabelecimento_cnes FK
        date ano_mes FK
        int idade_paciente
        string sexo
        string raca_cor
        string tipo_aih_desc
        string complexidade_desc
        float valor_aih
        int quantidade_dias_permanencia
    }
    LEITOS {
        string id_estabelecimento_cnes FK
        date ano_mes FK
        string tipo_leito_desc
        string tipo_especialidade_leito_desc
        int quantidade_total
        int quantidade_sus
    }
    OCCUPANCY ||--o{ HOSPITALIZACOES : "Relationship, not Join"
    OCCUPANCY ||--o{ LEITOS : "Relationship, not Join"
```

Field lists above are the fields relevant to the join/grain story, not exhaustive —
`hospitalizacoes` alone carries the full `aihs_reduzidas` column set (109 raw columns)
plus resolved dictionary/geography fields.

The workbook itself lives in `tableau/` (not committed as `.twbx` — see `tableau/README.md`
for why the connection is always Extract, never Live, for a local `.hyper` file).

## Setup

```bash
poetry install
cp .env.example .env   # fill in BD_BILLING_PROJECT_ID with your own GCP project id
```

The first BigQuery call opens a one-time browser OAuth prompt; credentials cache
locally after that. Verify the connection with:

```bash
poetry run python scripts/check_auth.py
```

## Pipeline

Three stages, each reading the previous stage's output from `data/`
(`raw/` → `transformed/` → `refined/`, all gitignored):

```bash
# 1. Extract: BigQuery -> data/raw/*.parquet
poetry run python scripts/run_extraction.py            # dry run, prints byte estimates only
poetry run python scripts/run_extraction.py --execute   # runs for real (touches billing)

# 2. Transform: join + resolve dictionaries + compute occupancy -> data/transformed/*.parquet
poetry run python scripts/run_transform.py              # local only, no cost

# 3. Refine: finalize tables + export -> data/refined/*.parquet, data/refined/sih_cnes_rs.hyper
poetry run python scripts/run_refine.py                 # local only, no cost
```

Only step 1 touches BigQuery/billing; steps 2 and 3 run entirely locally via DuckDB.

### Extract (`src/extract/`)

- `BigQuerySession` — wraps `basedosdados` auth, adds dry-run bytes estimation
- `AihsReduzidasExtractor`, `LeitoExtractor` — the two fact tables, scoped to RS/2019-2023
- `DictionaryExtractor` — code→description lookups (`dicionario` tables)
- `DirectoryExtractor` — `municipio`/`uf` dimension tables

### Transform (`src/transform/`)

- `DuckDBSession` — local query engine over the raw parquet files
- `DictionaryResolver` — generates the repeated code→description join SQL
- `AihsEnricher`, `LeitoEnricher` — record-level detail + dictionary descriptions + geography
- `OccupancyCalculator` — hospital/month occupancy rate aggregate

### Refine (`src/refine/`)

- `OccupancyRefiner`, `HospitalizacoesRefiner`, `LeitosRefiner` — final column cleanup,
  adds a proper `ano_mes` date column for Tableau's date hierarchy
- `HyperExporter` — writes all three tables into one `sih_cnes_rs.hyper` file (via `pantab`)

## Repo structure

- `scripts/` — one-off/exploratory + pipeline entrypoints, run manually, no package
  structure (doubles as a record of how the data was investigated)
- `src/` — reusable pipeline classes (`extract/`, `transform/`, `refine/`)
- `docs/` — briefing and dashboard specs (versioned) — see `docs/README.md` for a
  manifest of what each file contains
- `tableau/` — the actual Tableau workbook(s); `.twb` tracked, `.twbx` gitignored —
  see `tableau/README.md`
- `data/raw|transformed|refined/` — gitignored, never committed
- `references/` — third-party licensed material, gitignored, never committed
- `CLAUDE.md` — full data-profiling notes and working agreement for this project

## Presentation deliverables

See `docs/README.md` for the full manifest (what each file contains, how they relate).
Short version:

- `docs/data_briefing.md` — data briefing for the UX team: what the data can answer,
  which business questions are prioritised, and the caveats that must be surfaced
- `docs/uxers_guidance.md` — the UX co-presenters' own priority filter over the
  Aurélien deck (Fundamentos de Design / Experiência do Usuário / Acessibilidade,
  each with antes/depois examples) — the refinement layer `dashboard_v1_spec.md` builds on
- `docs/dashboard_v1_spec.md` — build spec for the intentionally bad first version:
  page layout (regions N–J), sheet-by-sheet Tableau instructions, and a 46-item ledger
  of which design principle each choice violates (and how the redesign fixes it)
- `docs/dashboard_v1_spec.html` / `docs/dashboard_v1_wireframe.html` — styled,
  browsable companions to the spec: the first is the write-up, the second is a mid/high-fidelity
  navigable mockup with a toggleable per-region diagnostic

Principles come from *Learn Design Driven Data Visualization* (Aurélien Vautier /
Dataviz Clarity, CC BY-NC-ND 4.0) — the PDF lives in the gitignored `references/`.

## Status

- [x] Extraction pipeline (BigQuery → parquet), RS/2019-2023
- [x] Transform pipeline (join, dictionary resolution, occupancy calc)
- [x] Refine pipeline + `.hyper` export
- [x] Dashboard briefing document (`docs/data_briefing.md`)
- [x] Spec for the intentionally poor first-version dashboard (`docs/dashboard_v1_spec.md`),
  refined against the UX co-presenters' own priority pass (`docs/uxers_guidance.md`)
- [x] Mid/high-fidelity wireframe mockup with per-region diagnostic (`docs/dashboard_v1_wireframe.html`)
- [x] Build V1 in Tableau (`tableau/dashboard_v1.twb`) — single data source, three tables
  related (not joined) on `id_estabelecimento_cnes` + `ano_mes`; 21 worksheets assembled
  onto one fixed 1200×2600 dashboard, with all 11 region-I filters placed across their
  six spec'd blocks
- [x] Scope the region-I filters — 8 of 11 now apply to selected worksheets, 3 stay global.
  Scoping is deliberately approximate versus `docs/dashboard_v1_spec.md` section 6; the
  proximity sin still lands on 8 filters
- [x] Record the as-built deviations (`docs/dashboard_v1_as_built.md`) — filter scope,
  automatic Y axis on the time series, dual-axis line chart, one known legend/pie filter
  mismatch
- [ ] Principle-by-principle redesign → V2 (`docs/dashboard_v2_spec.md`)

*Capturing the "before" artefacts (screenshots, timings, usability recording) was dropped
from this repo's scope — the UX co-presenters own the presentation materials.*
