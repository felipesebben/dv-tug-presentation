# docs/ — file manifest

> **Keep this file in sync.** Whenever a file in `docs/` is added, renamed, or has its
> purpose/scope meaningfully change, update the matching entry below in the same
> change. This is the map new sessions (human or Claude) use to figure out what's
> here before opening anything.

## Reading order

For someone new to the project, the natural read order is: `data_briefing.md` →
`uxers_guidance.md` → `dashboard_v1_spec.md` → `dashboard_v1_spec.html` (or
`dashboard_v1_wireframe.html`) for the visual version. Read `metrics_dictionary.md`
whenever you need to know what a number on the dashboard actually measures.

If you're about to open or change the actual workbook, read `dashboard_v1_as_built.md`
first — the spec describes the design, that file describes what got built.

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

### `metrics_dictionary.md`
Definition-of-record for every number shown on the dashboard, verified against
`data/refined/*.parquet` — **the build reference to keep open while making the Tableau
sheets**. Section 3 covers every chart region (C–J) with its source table, shelf
assignment, real values to build against, and per-chart trap; it opens with the warning
that `dashboard_v1_wireframe.html` is **only partly** fed by real data (header anchors
real, fine fill synthetic), so the wireframe must not be used as a build target — this
file is the source of truth, and where Tableau disagrees with the wireframe, Tableau is
right. Sections 1–2 cover the 8 KPI tiles: the exact SQL, the grain it's
computed at, and the trap it hides. Leads with the `107,9 leitos` tile — which is the
**mean beds per hospital per month**, not RS's bed count (~28.775/month), a 267× gap —
and covers the three occupancy-rate weightings (30,8% unweighted vs 43,1% weighted vs
39,6% SUS-only denominator), the SUS-numerator/total-denominator bias that systematically
understates occupancy, the real `6,05 dias / 6,05%` collision, and the `indicador_obito`
vs `motivo_saida` cross-validation (they agree on all 3.739.506 rows; use
`indicador_obito`). Also the **metadata provenance** section: which `dicionario` tables
resolve which coded columns, why the `basedosdados-dev` auxiliary-files bucket returns
`UserProjectMissing` (it's requester-pays, not broken — with the `--billing-project`
command, unrun, and why we don't need it), and the 6- vs 7-digit municipality-code trap.
Closes with the six caveats that should surface in V2's footer. Doubles as a presentation
artifact: V1 deliberately ships **no** data dictionary, and this is what it's missing.

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
the redesign workshop, and the suggested build order (including the Tableau
Relationships-not-Joins data-source setup). Section 9 ("before" artefacts) is retained
only as a record that it was dropped from scope.

**Caveat:** this is the *design* document. V1 has been built, and the workbook diverges
from it in a few places — read `dashboard_v1_as_built.md` alongside it. The spec keeps
its reasoning intact because that reasoning is the redesign material.

### `dashboard_v1_as_built.md`
Record of what `tableau/dashboard_v1.twb` **actually contains**, verified by reading the
workbook XML rather than by looking at it. Written because the spec is a design document
that the build intentionally diverged from, and a fresh reader would otherwise assume
every spec'd sin exists in the workbook. Contents: the five deviations (automatic Y axis
instead of the spec'd 0,26–0,34 truncation; a dual synchronized axis on the time series;
approximate filter scoping with 3 of 11 filters left global; 21 sheets not 22; "before"
artefacts dropped from scope), the per-filter scope table as built, confirmation that the
line-chart calculations are correct, and one known defect (the sex/ethnicity pie legends
don't receive their pies' filters, so their percentages disagree once filtered). Also
flags that **sin-ledger item 32 ("eixo truncado") is not realized in the build** — the
redesign shouldn't fix a sin that isn't there. The review that produced this file covered
the time series and the filters, not all 46 ledger items, so it notes that a full
ledger-vs-workbook pass is still worth doing before the workshop.

### `dashboard_v2_design_system.md`
The token set the V2 is built from — colours, type scale, spacing grid, chart rules —
so that consistency is a decision made once rather than a judgement repeated per
sheet. Turns the direction in `uxers_guidance.md`'s accessibility block into numbers:
exactly 3 greys with measured contrast, an 8px spacing grid where the 8-vs-24
intra/inter-group gap *is* the proximity law, a 9pt type floor, and a banned-forms
list (pie, 3D, bubble, dual axis).

Contains one **open decision**: the guidance's recommended green+orange highlight pair
was tested with a CVD simulator and failed (ΔE 3,2 under protanopia, against a target
of 8) — both hues sit on the red-green confusion axis. The document adopts blue+orange
(ΔE 24,7) provisionally and flags that this contradicts a guidance document that
normally wins on conflicts. Palettes ship as `tableau/Preferences.tps`.

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

Note that it renders the **design intent**, not the built workbook — its time series shows
the truncated 0,26–0,34 Y axis that V1 ended up not having. Left as-is on purpose: it is a
mockup of the spec, and the spec's argument is what the redesign works from.

Three regions were deliberately made **more plausible** (caricature gets dismissed; a
mistake the audience recognizes from their own work lands harder): **N** is a full-height
left rail plus a content-column appbar rather than a floating strip of buttons; **A** uses
Arial rather than a decorative font, so the typographic sin is the *absence of scale*
(3 arbitrary sizes, all-caps, stretched tracking, low contrast) instead of an ugly
typeface; **I**'s 10 filters are scattered across **5 differently-styled blocks** down the
page rather than stacked in a footer, so each block sits far from the chart it controls.
Region A embeds inline copies of the three fictional SVG marks in `assets/logos/`.

## Not yet created

- `dashboard_v2_spec.md` — the "depois": the per-tab build spec for V2. Persona and tab
  architecture are settled (SES-RS analyst building a federal funding case; Panorama →
  Território → Capacidade → Custo); the design tokens it will reference already exist in
  `dashboard_v2_design_system.md`.
## Deliberately not created

- `assets/v1/` (i.e. `docs/assets/v1/`) — screenshots, load-time measurements and a
  usability screen recording of the V1 workbook. **Dropped from this repo's scope**: this
  repo builds and documents the dashboards; the UX co-presenters own the presentation and
  its materials. Don't add this folder back without that decision changing.
