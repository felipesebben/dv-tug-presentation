# tableau/

The actual Tableau workbook(s) for this project — not to be confused with `docs/`,
which holds the *specs* for what to build, not the built thing itself.

## What goes here

- **`dashboard_v1.twb`** (tracked) — the V1 "antes" workbook, built per
  `docs/dashboard_v1_spec.md`. `.twb` is plain XML with no embedded data (it just
  references `../data/refined/sih_cnes_rs.hyper` by path), so it's small and
  diffable — treat it like source code.
- **`dashboard_v1.twbx`** (gitignored) — the packaged export: `.twb` + the `.hyper`
  extract zipped together, self-contained and portable. This is what you'd hand to
  the UX co-presenters or open on a machine without the rest of this repo. Regenerate
  it from Tableau (*File → Export Packaged Workbook*) whenever you need a fresh
  portable copy — don't hand-maintain it, and don't commit it (same reasoning as
  `data/` and `references/`: it's a large generated binary, not source).
- **`Preferences.tps`** (tracked) — the V2 custom colour palettes. This file is *not*
  read from here: copy it to `Documents/My Tableau Repository/Preferences.tps`
  (pt-BR: `Documentos/Meu repositório do Tableau/Preferences.tps`) and restart Tableau,
  after which the palettes appear by name under *Marks → Color → Edit Colors*. It lives
  in the repo so the palette is versioned alongside the reasoning in
  `docs/dashboard_v2_design_system.md` instead of living only in one person's Tableau
  install. Every value in it was validated with a CVD simulator.
- `dashboard_v2.twb` will show up here once the redesign starts.

## Connection type: always Extract

There's no live-connection choice to make here. Once Tableau points at a local
`.hyper` file, it's an Extract connection by definition — `.hyper` **is** Tableau's
extract format, not a live-queryable endpoint. The live-vs-extract decision that
actually mattered was made upstream, in the pipeline: materialize `data/refined/sih_cnes_rs.hyper`
locally via `scripts/run_refine.py` rather than have Tableau query BigQuery directly.
That keeps every dashboard iteration free and offline — BigQuery billing only happens
during `scripts/run_extraction.py --execute`.

**Workflow when the data needs to change:** edit `src/refine/` (or upstream in
`src/transform/`) → rerun the relevant `scripts/run_*.py` → hit *Data → Refresh* on
the extract in Tableau (or *Data → Extract → Refresh*, or re-run *Refresh from Source*
if the `.hyper`'s schema changed). No BigQuery calls in that loop.
