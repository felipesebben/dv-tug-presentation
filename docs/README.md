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
computed at, and the trap it hides. Section 4.3 is the one to read first as of 29/07/2026: **ICU occupancy inverts the
pandemic story.** 111,9% in 2021 and 131,9% in June 2021, while general occupancy *fell*
to 53,2% — so a dashboard showing only the aggregate would have told a health secretary
the network was under less pressure in 2021 than in 2019. Section 4.4 adds per-bed-type
rates and the two reading caveats they need. Leads with the `107,9 leitos` tile — which is the
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

### `dashboard_v2_spec.md`
The build spec for the corrected dashboard ("V2"), and the counterpart to
`dashboard_v1_spec.md` — same section structure so the two read side by side. Contents:
the persona (an SES-RS analyst assembling a federal funding case, which is what decides
every cut below it), the one sentence each tab has to prove, a four-tab architecture at
1200×800 so nothing scrolls, and a sheet-by-sheet spec with **real anchor numbers**
verified against the refined tables — KPI values, the indexed capacity/demand series, the
municipal ranking, bed counts by type, cost by complexity.

Its section 6 is the workshop script: V1 sin → V2 correction, mapped item by item. The
last row is the one with no ledger number — the wrong denominator — and it's the point of
the whole talk: no amount of design catches it.

Ends with a build order that puts the palette and workbook-level formatting *before* the
first sheet, which is what stops V1's inconsistency from reaccumulating.

### `dashboard_v2_wireframe_template.html`
**Edit this one.** Source for `dashboard_v2_wireframe.html`, which is *generated* by
`scripts/build_wireframe_v2_data.py` injecting a ~230 KB data blob into the
`/*__DATA__*/` placeholder. The split exists because the wireframe has to be a single
self-contained file (it publishes as an artifact under a CSP that blocks every external
request, so data cannot be fetched at runtime) while nobody should be hand-pasting 230 KB
of JSON. Regenerate rather than patch: a stale figure then shows up as a diff.

Verified by `scripts/test_wireframe.js`, which runs the page's script against a stubbed
DOM and renders all four tabs under all seven period selections, failing on thrown errors,
`NaN`, `undefined`, `Infinity` or a leaked `null`, and asserting that the headline figures
(ICU 111,9% in 2021, network 53,2%, 60,0% in 2023, 55,8% across the period) actually come
out of the code rather than out of prose.

### `dashboard_v2_wireframe.html`
**Generated — do not edit.** See the template entry above.

Mid/high-fidelity **visual mockup** of V2 and the counterpart to
`dashboard_v1_wireframe.html` — the two are meant to be shown side by side. Four
navigable tabs rendered inside a true 1200×800 frame, so "fits on one screen" is visible
rather than claimed. Every number and series is real, read from `data/refined/` — no
synthetic fill.

**The Panorama hero is ICU versus network occupancy**, and it is the page's argument: from
2019 to 2021 the network rate *fell* 5,2 p.p. while ICU *rose* 35,8 p.p., peaking at 131,9%
in June 2021 against 57,0% for the network. A dashboard showing only the aggregate would
have reported less pressure in the worst health year of the century. A useful side effect
is that the hero no longer needs the indexed-axis exception: both series are rates in the
same unit, so the axis starts at zero and the 100% line becomes a real threshold. The
capacity-versus-demand scissors keeps the 100 baseline, and is now the only chart that
needs it.

**The period filter genuinely works.** It drives all four tabs, and the data blob ships raw
numerators and denominators rather than rates so the page recomputes
`SUM(num) / SUM(den)` — the same rule the Tableau build follows. Shipping rates would have
forced the mock to average averages, which is the exact defect the V2 occupancy rebuild
exists to fix, and the filter would have produced wrong numbers while looking like it
worked. Two regional filters exist: Região intermediária (8) visible, Região de saúde (30)
behind "mais filtros" for Hick's Law. Both are shown but not wired, and the page says so.

**No chart subtitle asserts a conclusion.** Titles describe and carry the selected period;
min/max annotations are computed so they follow the filter. The editorial claims that used
to live in subtitles are destined for the orientation layer instead. Colour valence is
enforced: the three places where orange marked merely "most recent" or "the median" are now
blue or grey.

The canvas is **fixed light** deliberately — its palette was contrast-validated against a
white card, so theming it would invalidate the measurement.

Published as a Claude artifact; `dashboard_v2_wireframe_template.html` plus the generator is
the source of truth for it.

### `dashboard_v2_orientation.md`
Content-of-record for the V2's orientation layer — guided tour, "how to use it", and
glossary — specified together because they overlap heavily, so each sentence lives in one
place and is referenced from the others. Closes the last open row of `uxers_guidance.md`
(Nielsen, help and documentation: *"dashboard sem glossário e sem botão de suporte"*).

It has a second job worth understanding before reading it: the 29/07/2026 revision removed
every editorial claim from the chart subtitles, because a subtitle asserting a conclusion is
contradicted by the first filter a user applies. Those conclusions did not stop being true —
they moved here. Without this layer the V2 trades a title that lies for a dashboard that
explains nothing.

Section 1 fixes the procedence rule: the glossary is the **user-facing subset** of
`metrics_dictionary.md`, which wins on any conflict, and nothing may be defined here that
isn't defined there. Section 3 is the 6-step tour, including why the first-run prompt is not
a modal. Section 4 carries the hardest thing the layer has to teach — the indexed chart's
100 baseline, which contradicts the design system's own zero-baseline rule for reasons that
have to be stated rather than assumed. Section 5 is the 14 glossary entries, each with the
caveat that changes the reading. Section 6 maps each piece to its Tableau equivalent, and
recommends a "Comece aqui" tab over a chain of show/hide containers for the tour, because the
chain is the kind of construction nobody can maintain afterwards.

### `dashboard_v2_design_system.md`
The token set the V2 is built from — colours, type scale, spacing grid, chart rules —
so that consistency is a decision made once rather than a judgement repeated per
sheet. Turns the direction in `uxers_guidance.md`'s accessibility block into numbers:
exactly 3 greys with measured contrast, an 8px spacing grid where the 8-vs-24
intra/inter-group gap *is* the proximity law, a 9pt type floor, and a banned-forms
list (pie, 3D, bubble, dual axis).

The green+orange highlight pair the guidance recommended was tested with a CVD simulator
and failed (ΔE 3,2 under protanopia, against a target of 8) — both hues sit on the
red-green confusion axis. Blue+orange (ΔE 24,7) replaced it and was **ratified 29/07/2026**,
closing the document's last open decision.

Two additions from that ratification. First, the colours now carry fixed **valence**, not
just visual role: grey is neutral, blue means healthy, orange means *needs attention* —
which implies a prohibition that is easy to violate by habit, namely that orange must never
mark merely "the most recent" or "the median". Second, the type family is **Roboto**, with
the warning that matters more than the choice: Tableau embeds no fonts and Roboto ships with
neither Windows nor Tableau, so an uninstalled font is substituted silently on whatever
machine renders the view. Section 6 also documents how the choropleth is wired — an IBGE
spatial file joined on the 7-digit code rather than Tableau's name-based geocoding, because
38 RS municipality names are reused in other states. Palettes ship as
`tableau/Preferences.tps`.

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

## Fixed in the 29/07/2026 revision

Recorded because these are the defects the rebuild removed, and three of them are worth
telling the audience about:

- **KPI tiles were hardcoded to 2023** while the filter bar read `2019–2023`. Both figures
  were right (60,0% and 55,8%) and together they were misleading, because the tile could not
  say which one you were looking at. The tile now prints its own period.
- **"Os 15 municípios com mais leitos SUS" was wrong three ways.** The bed figure was
  `AVG(leitos_sus)`, a mean per hospital-month, so Porto Alegre read **281** instead of
  **4.748,6**; the ranking was therefore wrong (Passo Fundo, Caxias do Sul and Novo Hamburgo
  were missing, São Jerônimo and Uruguaiana did not belong); and the bars encoded occupancy
  while the title said beds. Worth a slide: this is the same trap section 1 of
  `metrics_dictionary.md` opens with, committed one tab away from where it is documented.
- **The map was a schematic grid in a wide strip.** RS's aspect ratio is 1,03 — square — so
  the strip either wasted ~800px or squashed the state. Now real IBGE geometry in a square
  container.
- **`55,9%` was a rounding error** repeated across six files. The true full-period rate is
  55,8498%, which is 55,8% at the one decimal the rest of the docs use.
- Subtitles no longer assert conclusions, and orange no longer marks "most recent".

## Not yet created

- The workbook itself, `tableau/dashboard_v2.twb`, which lives in `tableau/`, not here.
  Everything it needs now exists: the refined tables with ICU columns, the design system
  with a ratified palette and type family, the build spec, the wireframe, and
  `dashboard_v2_orientation.md` section 6 for how the help layer maps onto Tableau objects.
  Two prerequisites are on Felipe rather than in the repo: install Roboto, and copy
  `tableau/Preferences.tps` into the Tableau repository folder.

**Every row of `uxers_guidance.md` is now addressed.** The last one to close was Nielsen's
help/documentation row, via `dashboard_v2_orientation.md`; the error-prevention row's
"breadcrumb to undo a filter" closed in the same pass. One row was already marked open by
the UX pair themselves (Nielsen — flexibility and efficiency of use, where they left a "?"
on both sides), so it has nothing to satisfy.
## Deliberately not created

- `assets/v1/` (i.e. `docs/assets/v1/`) — screenshots, load-time measurements and a
  usability screen recording of the V1 workbook. **Dropped from this repo's scope**: this
  repo builds and documents the dashboards; the UX co-presenters own the presentation and
  its materials. Don't add this folder back without that decision changing.
