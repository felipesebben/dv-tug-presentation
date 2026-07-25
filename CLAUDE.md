Use object oriented programming for developing the pipelines. Always use branching development for each feature.
Suggest code and work in a pair programming iteration.

## Project context
Dashboard for a Tableau User Group presentation on gestalt/UX heuristics. Plan: build a dashboard briefing, produce an intentionally poor first version, then two UXer co-presenters redesign it principle-by-principle for the talk.

## Working agreement
- Mentor role: move through implementation at working pace once a feature is greenlit (no need to pause before every file/edit) — but do a code review + teaching pass together once the feature is done, walking through what was built and why. Still stop and confirm explicitly before costly/hard-to-reverse actions (real cloud queries, commits, anything touching billing)
- Branch-per-feature; commit only once a feature is clean and working
- Never run commands that could incur unintended cloud costs (billing accounts, cloud queries)

## Data pipeline
- Main goal: extract the two raw fact tables from BigQuery, then resolve their coded/dimensional columns (geography, and coded fields like `tipo_aih`, `motivo_saida`, `tipo_leito`, etc.) into human-readable descriptions using BD's dictionary/directory tables — a coded value on its own isn't useful in the dashboard briefing or the final Tableau viz
- Source fact tables: `br_ms_sih.aihs_reduzidas` (hospitalizations — AIH reduzida/reduced hospital admission records; `microdados` does not exist in this dataset) + `br_ms_cnes.leito` (bed capacity)
- `aihs_reduzidas`: 109 columns, partitioned by `ano`, clustered by `mes` then `sigla_uf` (INT64 — numeric UF code, not the 2-letter abbreviation)
- `leito`: 10 columns, partitioned by `ano` only, no clustering; `sigla_uf` here is STRING, not INT64 like in `aihs_reduzidas`
- `aihs_reduzidas.sigla_uf` is dead — 100% NULL across all years checked (2019-2023), despite being a clustering column. Do not rely on it.
- Geography join, decided: `aihs_reduzidas` ⋈ `leito` on `id_estabelecimento_cnes` + `ano` + `mes` (the join the occupancy calc needs anyway), taking `sigla_uf`/`id_municipio` from the `leito` side since it's already populated. Earlier idea was to cast one side's `sigla_uf` (INT64 vs STRING type mismatch) to match the other directly — ruled out, since `aihs_reduzidas.sigla_uf` is NULL regardless of type, casting wouldn't fix that.
- Geographic granularity goes down to municipio level, not just UF — so `br_bd_diretorios_brasil.municipio` (id_municipio key) is a required join, not just a nice-to-have for `nome_uf`/`nome_regiao`. Still done as a small local join in DuckDB after extraction (municipio dimension is tiny — 5,571 rows), not another BigQuery join over the large fact tables
- `br_bd_diretorios_brasil.municipio`/`uf` profiled and sampled:
  - `uf`: 27 rows, `id_uf` (2-digit numeric string, e.g. `11`=RO), `sigla` (2-letter), `nome`, `regiao`
  - `municipio`: `id_municipio` is the 7-digit IBGE code (matches `leito.id_municipio` format directly — join as-is) — but `aihs_reduzidas.id_municipio_estabelecimento` uses the legacy DATASUS **6-digit** code (drops the trailing IBGE check digit), which does NOT match `id_municipio`. Use `municipio.id_municipio_6` instead — verified via test join (5/5 sample codes resolved correctly to real municipality names/UFs)
  - So: `aihs_reduzidas.id_municipio_estabelecimento` = `municipio.id_municipio_6`; `leito.id_municipio` = `municipio.id_municipio`. Don't join either fact table's municipio field to `id_municipio` uniformly — the two fact tables use different code widths
- Dimensional descriptions, profiled: both `br_ms_sih.dicionario` and `br_ms_cnes.dicionario` follow the same generic key-value schema (`id_tabela`, `nome_coluna`, `chave`, `cobertura_temporal`, `valor`) — one row per (table, column, code)
  - `br_ms_sih.dicionario`: 34,416 rows total, scoped to `aihs_reduzidas` + `servicos_profissionais` only. Covers `carater_internacao`, `motivo_saida`, `tipo_aih`, `complexidade`, `especialidade_leito`, `procedimento_solicitado`/`realizado`, and others — but NOT `br_ms_cnes.leito`
  - `br_ms_cnes.dicionario`: separate table, scoped to CNES's own tables. Covers `leito`'s two coded columns, `tipo_leito` and `tipo_especialidade_leito`
  - Each fact table's coded columns must be joined against its own dataset's `dicionario` (chave = the fact table's code column, cast as needed since `chave`/codes are STRING) — there is no single shared dictionary across datasets
- Occupancy rate = SIH-SUS admissions/bed-days ÷ CNES bed capacity, joined by hospital/state/month (approximation — DATASUS notes length-of-stay alone can't give a true occupancy rate)
- Free tier lags ~6 months behind current data — acceptable for this project, flag as a caveat in the briefing
- Geographic scope: decided — Rio Grande do Sul (RS), 2019-2023, for the first end-to-end pipeline pass. Drill-down to municipio level is in scope within RS
- pysus was tried and ruled out (DuckLake catalog gaps, Windows-only bug in legacy FTP client) — don't revisit
- Stack: poetry, DuckDB, Tableau .hyper export at the end

## Data access (Base dos Dados)
- Python package: `basedosdados`, functions `read_sql`/`read_table`
- Requires `billing_project_id` (Felipe's own GCP project — queries bill against it, not BD's)
- First call opens a one-time browser OAuth prompt; credentials cache locally after that
- Filter on partition/cluster columns (e.g. `ano`, `sigla_uf`) to keep bytes scanned near zero — verify actual column names per table before assuming

## Repo structure
- `scripts/` — one-off/exploratory, run manually, no package structure, committed (doubles as a record of how data was investigated)
- `src/` — reusable pipeline code once stages stabilize (extract/transform/refine)
- `data/raw|transformed|refined/` — gitignored, never committed
- `docs/` — briefing + dashboard spec docs, versioned. **`docs/README.md` is a manifest of
  every file in this folder — update it in the same change whenever a `docs/` file is
  added, renamed, or has its purpose/scope meaningfully change.**
- `references/` — third-party licensed material (Aurélien deck, UXers guidance PDF), gitignored, never committed
- Poetry: package-mode disabled (`[tool.poetry] package-mode = false`) — this is a pipeline project, not a distributable library
- You can update by yourself README.md documentation and add widgets that can update the status of the project for yourself as we commit our job.
- Documentation can be also added to functions, classes etc using best practices.
- When private keys used, always remember to use .env variables and other best practices.