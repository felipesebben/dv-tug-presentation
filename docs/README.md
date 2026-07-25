# docs/ — file manifest

> **Keep this file in sync.** Whenever a file in `docs/` is added, renamed, or has its
> purpose/scope meaningfully change, update the matching entry below in the same
> change. This is the map new sessions (human or Claude) use to figure out what's
> here before opening anything.

## Reading order

For someone new to the project, the natural read order is: `data_briefing.md` →
`uxers_guidance.md` → `dashboard_v1_spec.md` → `dashboard_v1_spec.html` (or
`dashboard_v1_wireframe.html`) for the visual version.

## Files

### `data_briefing.md`
Data briefing for the UX co-presenters, written by the data side of the project.
States what the data *can* answer (five business-question groups: occupancy over
time, geographic comparison, patient demographics, bed capacity by type, cost),
which three refined tables exist (`occupancy`, `hospitalizacoes`, `leitos`) and their
grain, and the four caveats that must surface somewhere in the dashboard (occupancy
is an approximation and can exceed 100%, data is administrative not clinical,
single-state scope, ~6-month lag). Does **not** prescribe chart types or layout —
that's `uxers_guidance.md` and `dashboard_v1_spec.md`'s job. Input to everything else
in this folder.

### `uxers_guidance.md`
Transcription of `references/uxers_guidance.pdf` — the two UX co-presenters' own
priority pass over the Aurélien deck (*Learn Design Driven Data Visualization*),
organized into three blocks: **Fundamentos de Design**, **Experiência do Usuário**,
**Acessibilidade**, each principle with a concrete antes/depois example. This is the
**decision layer that wins on conflicts** with the Aurélien deck (e.g. worst color
pair for colorblindness — Aurélien says green/red, this doc says blue/red; V1 uses
both, one per map). Also flags the "Top 5 UX Laws" the pair treats as unmissable:
Proximity, Hick's Law, Law of Focus, Law of Simplicity, Jakob's Law.

### `dashboard_v1_spec.md`
The build spec for the intentionally bad first-version dashboard ("V1"), and the
**source of truth** — everything else about V1 is derived from or should match this
file. Contents: the "rules of the game" that keep V1 plausible instead of a
caricature, the persona-of-error framing, the fixed 1200×2600px page layout (regions
**N** through **J**), the full Aurélien principle inventory (reference), a
per-region principle map tagging each region's primary/secondary sins by block
(FD/UX/A11) with citations back to `uxers_guidance.md` (`[UXers]`) or the Aurélien
deck (`[p.NN]`), sheet-by-sheet Tableau build instructions, a 46-item sin ledger
(38 from Aurélien + 8 from the UXers refinement) meant to be checked off live during
the redesign workshop, the suggested build order (including the Tableau
Relationships-not-Joins data-source setup), and how to capture "before" artefacts.

### `dashboard_v1_spec.html`
Styled, browsable companion to `dashboard_v1_spec.md` — same content, condensed
(drops the full sheet-by-sheet tables in favor of a shorter build-order panel),
formatted as a readable single-page doc with a sticky TOC and light/dark theme.
Open this to *read* the spec; open the `.md` to *edit* it.

### `dashboard_v1_wireframe.html`
Mid/high-fidelity **visual mockup** of the V1 dashboard described in
`dashboard_v1_spec.md` — not a write-up, an actual rendering (KPI tiles, pies, a
schematic map grid, bar charts, a canvas scatter, an SVG time series, etc.) built to
look like a plausible bad Tableau export. Real anchor numbers (the 8 KPI values, sex
split, yearly occupancy averages, Porto Alegre's share, the age-97-99 tail) are
accurate against the base; fine-grained fill data (month-by-month table cells,
long-tail bed-specialty names, scatter points) is synthetic and flagged as such in
the page's own intro text. Has a "Mostrar diagnóstico" toggle that outlines each
region and shows its principle(s)/citation/fix in a bottom drawer — condensed from
`dashboard_v1_spec.md` section 5. Published as a Claude artifact for quick review;
the file in this repo is the source of truth for that artifact.

## Not yet created

- `dashboard_v2_spec.md` — the "depois": documents the redesign once the UX
  co-presenters have gone through the workshop. Mentioned as a next step in
  `dashboard_v1_spec.md` section 10.
- `assets/v1/` — screenshots, load-time measurements, and a screen recording of the
  actual V1 Tableau workbook, captured per `dashboard_v1_spec.md` section 9. Not
  created until the real `.twbx` exists.
