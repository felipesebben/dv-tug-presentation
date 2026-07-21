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
- `data/raw|transformed|refined/` — gitignored, never committed
- `CLAUDE.md` — full data-profiling notes and working agreement for this project

## Status

- [x] Extraction pipeline (BigQuery → parquet), RS/2019-2023
- [x] Transform pipeline (join, dictionary resolution, occupancy calc)
- [x] Refine pipeline + `.hyper` export
- [ ] Dashboard briefing document
- [ ] Intentionally poor first-version Tableau dashboard
- [ ] Principle-by-principle redesign (TUG talk)
