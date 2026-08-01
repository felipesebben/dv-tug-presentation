/* Headless smoke test for the generated wireframe.
   Extracts the inline <script>, stubs the DOM just enough to let it initialise, then
   renders all 4 tabs under several period selections and checks the output for the
   failure modes that a static read cannot catch: thrown errors, NaN, undefined and
   "null%" leaking into the markup. */
const fs = require("fs");

const html = fs.readFileSync(process.argv[2], "utf8");
const m = html.match(/<script>([\s\S]*)<\/script>\s*$/);
if (!m) { console.error("FAIL: no trailing <script> block found"); process.exit(1); }
const src = m[1];

/* --- minimal DOM stub --- */
const listeners = {};
function makeEl(id) {
  const classes = new Set();
  return {
    id, innerHTML: "", style: {}, dataset: {},
    classList: {
      add: c => classes.add(c), remove: c => classes.delete(c),
      toggle: (c, on) => (on ? classes.add(c) : classes.delete(c)),
      contains: c => classes.has(c), _set: classes,
    },
    setAttribute() {}, getAttribute() { return null; },
    addEventListener(ev, fn) { (listeners[id + ":" + ev] ||= []).push(fn); },
    appendChild() {}, closest() { return null; },
    focus() {}, setSelectionRange() {},
  };
}
const els = {};
const document = {
  getElementById(id) { return (els[id] ||= makeEl(id)); },
  querySelectorAll() { return []; },
  querySelector() { return null; },
  createElement(tag) { return makeEl("new-" + tag); },
  addEventListener() {},
};
globalThis.document = document;
/* Fire a listener registered on a stubbed element, so the test can drive the UI the way a
   click would rather than reaching into internal state. */
function click(id) {
  const fns = listeners[id + ":click"] || [];
  if (!fns.length) throw new Error(`no click listener bound on #${id}`);
  fns.forEach(fn => fn({ stopPropagation() {}, target: els[id] }));
}
const orientHTML = () => (els["orient"] ? els["orient"].innerHTML : "");

let failures = 0;
function check(label, html) {
  const problems = [];
  if (/NaN/.test(html)) problems.push("NaN");
  if (/undefined/.test(html)) problems.push("undefined");
  if (/null%|null leitos|>null</.test(html)) problems.push("null value");
  if (/Infinity/.test(html)) problems.push("Infinity");
  if (html.length < 400) problems.push("suspiciously short (" + html.length + " chars)");
  if (problems.length) {
    failures++;
    console.log(`  FAIL ${label}: ${problems.join(", ")}`);
    const at = html.search(/NaN|undefined|Infinity|null%/);
    if (at >= 0) console.log(`       context: ...${html.slice(Math.max(0, at - 90), at + 60)}...`);
  } else {
    console.log(`  ok   ${label} (${html.length} chars)`);
  }
}

/* Run the wireframe script, then reach into its scope via an appended probe. */
const probe = `
;globalThis.__probe = { TABS, STATE, PERIODOS, show, renderFilters,
                        ORIENT, TOUR, GLOSSARIO, refreshOrient, glossarioHTML };
`;
try {
  new Function(src + probe)();
} catch (e) {
  console.error("FAIL: script threw on initialisation:", e.message);
  console.error(e.stack.split("\n").slice(0, 4).join("\n"));
  process.exit(1);
}
const { TABS, STATE, PERIODOS, show, ORIENT, TOUR, GLOSSARIO, refreshOrient,
        glossarioHTML } = globalThis.__probe;
const names = ["Panorama", "Territorio", "Capacidade", "Custo"];

console.log("=== all tabs, all period presets, both views ===");
for (const visao of ["rede", "uti"]) {
  STATE.visao = visao;
  for (const p of PERIODOS) {
    STATE.periodo = p.id; STATE.anos = p.anos.slice(); STATE.rotulo = p.rotulo;
    for (let t = 0; t < 4; t++) {
      STATE.tab = t;
      try { check(`${visao} / ${p.rotulo} / ${names[t]}`, TABS[t]()); }
      catch (e) { failures++; console.log(`  FAIL ${visao} / ${p.rotulo} / ${names[t]}: threw ${e.message}`); }
    }
  }
}
STATE.visao = "rede";

console.log("=== single years (the degenerate case for indexed charts) ===");
for (const ano of [2019, 2021, 2023]) {
  STATE.periodo = "ano" + ano; STATE.anos = [ano]; STATE.rotulo = String(ano);
  for (let t = 0; t < 4; t++) {
    STATE.tab = t;
    try { check(`${ano} / ${names[t]}`, TABS[t]()); }
    catch (e) { failures++; console.log(`  FAIL ${ano} / ${names[t]}: threw ${e.message}`); }
  }
}

/* Verify the headline figures the page asserts in prose actually come out of the code. */
console.log("=== figure verification ===");
STATE.periodo = "ano2021"; STATE.anos = [2021]; STATE.rotulo = "2021";
const pan2021 = TABS[0]();
for (const [needle, why] of [["111,9%", "ICU rate 2021"], ["53,2%", "network rate 2021"]]) {
  if (pan2021.includes(needle)) console.log(`  ok   ${why} renders as ${needle}`);
  else { failures++; console.log(`  FAIL ${why}: ${needle} not found in Panorama`); }
}
STATE.periodo = "ano2023"; STATE.anos = [2023]; STATE.rotulo = "2023";
if (TABS[0]().includes("60,0%")) console.log("  ok   network rate 2023 renders as 60,0%");
else { failures++; console.log("  FAIL network rate 2023: 60,0% not found"); }
STATE.periodo = "todos"; STATE.anos = PERIODOS[0].anos.slice(); STATE.rotulo = "2019–2023";
if (TABS[0]().includes("55,8%")) console.log("  ok   full-period rate renders as 55,8%");
else { failures++; console.log("  FAIL full-period rate: 55,8% not found"); }

/* ---------- orientation layer ---------- */
console.log("=== orientation layer ===");
STATE.periodo = "todos"; STATE.anos = PERIODOS[0].anos.slice(); STATE.rotulo = "2019–2023";

/* First-run invitation must be present on load, and must NOT be a modal veil. */
show(0);
if (/Primeira vez aqui/.test(orientHTML())) console.log("  ok   first-run invitation shown on load");
else { failures++; console.log("  FAIL first-run invitation missing on load"); }
if (!/class="veil"/.test(orientHTML())) console.log("  ok   first-run is not a blocking modal");
else { failures++; console.log("  FAIL first-run rendered a blocking veil"); }

/* Dismissing it must not resurrect it on tab change. */
click("fr-no");
show(1);
if (!/Primeira vez aqui/.test(orientHTML())) console.log("  ok   dismissed invitation stays dismissed across tabs");
else { failures++; console.log("  FAIL invitation reappeared after dismissal"); }

/* Help sheets. */
click("h-ajuda");
check("Como usar sheet", orientHTML());
for (const needle of ["100 é o zero", "vale para a aba inteira", "6 meses"]) {
  if (orientHTML().includes(needle)) console.log(`  ok   'como usar' teaches: ${needle}`);
  else { failures++; console.log(`  FAIL 'como usar' missing: ${needle}`); }
}
click("h-gloss");
check("Glossário sheet", orientHTML());
if (GLOSSARIO.length === 16) console.log(`  ok   glossary has ${GLOSSARIO.length} entries`);
else { failures++; console.log(`  FAIL glossary has ${GLOSSARIO.length}, expected 16`); }
for (const term of ["Taxa de ocupação de UTI", "Complementar", "Hospital dia", "Valor da AIH"]) {
  if (orientHTML().includes(term)) console.log(`  ok   glossary defines: ${term}`);
  else { failures++; console.log(`  FAIL glossary missing: ${term}`); }
}

/* Glossary search: a hit, and the empty state. */
ORIENT.busca = "uti";
if (/Taxa de ocupação de UTI/.test(glossarioHTML())) console.log("  ok   glossary search finds 'uti'");
else { failures++; console.log("  FAIL glossary search failed on 'uti'"); }
ORIENT.busca = "zzzznotarealterm";
if (/Nenhum termo encontrado/.test(glossarioHTML())) console.log("  ok   glossary search has an empty state");
else { failures++; console.log("  FAIL glossary search lacks an empty state"); }
ORIENT.busca = "";

/* Every tour step renders, and each one that names a target actually spotlights it. */
click("h-gloss");            /* close the glossary */
click("h-tour");
for (let i = 0; i < TOUR.length; i++) {
  ORIENT.sheet = null; ORIENT.tour = i; refreshOrient();
  const html = orientHTML();
  check(`tour step ${i + 1}/${TOUR.length}`, html);
  if (!html.includes(`passo ${i + 1} de ${TOUR.length}`)) {
    failures++; console.log(`  FAIL tour step ${i + 1} lost its step counter`);
  }
  const alvo = TOUR[i].alvo;
  if (alvo) {
    const el = els[alvo];
    if (el && el.classList.contains("spot")) console.log(`  ok   step ${i + 1} spotlights #${alvo}`);
    else { failures++; console.log(`  FAIL step ${i + 1} did not spotlight #${alvo}`); }
  }
}

/* Only one element may be spotlit at a time, or the tour points at two things at once. */
const lit = Object.values(els).filter(e => e.classList && e.classList.contains("spot"));
if (lit.length <= 1) console.log(`  ok   at most one spotlight at a time (${lit.length})`);
else { failures++; console.log(`  FAIL ${lit.length} elements spotlit simultaneously: ${lit.map(e => e.id)}`); }

/* Leaving the tour clears the spotlight. */
ORIENT.tour = -1; refreshOrient();
const stillLit = Object.values(els).filter(e => e.classList && e.classList.contains("spot"));
if (!stillLit.length) console.log("  ok   exiting the tour clears the spotlight");
else { failures++; console.log(`  FAIL spotlight survived tour exit: ${stillLit.map(e => e.id)}`); }

/* Filter reset appears only when something is filtered — otherwise it is decoration. */
console.log("=== filter reset (Nielsen, error prevention) ===");
STATE.periodo = "todos"; STATE.anos = PERIODOS[0].anos.slice(); STATE.rotulo = "2019–2023";
show(0);
if (!/f-reset/.test(els["filters"].innerHTML)) console.log("  ok   no reset shown at default period");
else { failures++; console.log("  FAIL reset shown when nothing is filtered"); }
STATE.periodo = "pand"; STATE.anos = [2020, 2021]; STATE.rotulo = "Pandemia · 2020–2021";
show(0);
if (/f-reset/.test(els["filters"].innerHTML)) console.log("  ok   reset appears once a period is chosen");
else { failures++; console.log("  FAIL reset missing while filtered"); }
click("f-reset");
if (STATE.periodo === "todos" && STATE.anos.length === 5) console.log("  ok   reset restores the full period");
else { failures++; console.log(`  FAIL reset left periodo=${STATE.periodo}, anos=${STATE.anos}`); }

/* ---------- view switch, thresholds, and the retired caveat strip ---------- */
console.log("=== visão switch (rede / UTI) ===");
/* The scissors indexes against the first selected year, so it needs the full period —
   with a single year there is no base to index against and the chart says so. */
STATE.periodo = "todos"; STATE.anos = PERIODOS[0].anos.slice(); STATE.rotulo = "2019–2023";

STATE.visao = "rede"; STATE.tab = 0;
const panRede = TABS[0]();
STATE.visao = "uti";
const panUti = TABS[0]();
if (panRede !== panUti) console.log("  ok   switching visão changes Panorama");
else { failures++; console.log("  FAIL visão switch produced identical Panorama"); }

/* The scissors must follow the view. 2019=100 endpoints at 2023:
   rede capacity 100,3 / demand 103,1 — ICU capacity 121,1 / demand 125,1. */
for (const [needle, why] of [["Capac. 100,3", "rede capacity endpoint"],
                             ["Demanda 103,1", "rede demand endpoint"]]) {
  if (panRede.includes(needle)) console.log(`  ok   ${why} = ${needle.split(" ")[1]}`);
  else { failures++; console.log(`  FAIL ${why}: '${needle}' not found`); }
}
for (const [needle, why] of [["Capac. 121,1", "UTI capacity endpoint"],
                             ["Demanda 125,1", "UTI demand endpoint"]]) {
  if (panUti.includes(needle)) console.log(`  ok   ${why} = ${needle.split(" ")[1]}`);
  else { failures++; console.log(`  FAIL ${why}: '${needle}' not found`); }
}
if (/não é folga de capacidade/.test(panRede))
  console.log("  ok   scissors states the gap is not spare capacity");
else { failures++; console.log("  FAIL scissors lacks the 'not spare capacity' warning"); }

/* Território in ICU view: far fewer municipalities, and the absence is the finding.
   Counts are 2023 figures, so pin the period to 2023. */
STATE.periodo = "ano2023"; STATE.anos = [2023]; STATE.rotulo = "2023";
STATE.tab = 1; STATE.visao = "rede";
const terRede = TABS[1]();
STATE.visao = "uti";
const terUti = TABS[1]();
if (terRede !== terUti) console.log("  ok   switching visão changes Território");
else { failures++; console.log("  FAIL visão switch produced identical Território"); }
if (/59 municípios com leito/.test(terUti))
  console.log("  ok   UTI Território reports 59 municipalities with ICU beds");
else { failures++; console.log("  FAIL UTI Território municipality count wrong or missing"); }
if (/225 municípios com leito/.test(terRede))
  console.log("  ok   rede Território reports 225 municipalities");
else { failures++; console.log("  FAIL rede Território municipality count wrong or missing"); }
/* The ICU view's headline is absence, and it must say so. */
if (/A ausência é o achado/.test(terUti))
  console.log("  ok   UTI Território names absence as the finding");
else { failures++; console.log("  FAIL UTI Território missing the absence insight"); }

console.log("=== thresholds ===");
/* 2021 is the year that crosses both lines: ICU 111,9%, network 53,2%. */
STATE.periodo = "ano2021"; STATE.anos = [2021]; STATE.rotulo = "2021";
STATE.visao = "uti"; STATE.tab = 0;
const utiPan = TABS[0]();
for (const [needle, why] of [["atenção 85%", "85% band labelled"],
                             ["crítico 95%", "95% band labelled"]]) {
  if (utiPan.includes(needle)) console.log(`  ok   ${why}`);
  else { failures++; console.log(`  FAIL ${why}: '${needle}' not found`); }
}
/* ICU 2021 is 111,9%, above both thresholds, so the tile must say crítico. */
if (/crítico/.test(utiPan)) console.log("  ok   ICU 2021 tile reads crítico (111,9% > 95%)");
else { failures++; console.log("  FAIL ICU 2021 tile did not reach crítico"); }
/* The network at 53,2% must NOT be flagged. */
if (/sob controle/.test(utiPan)) console.log("  ok   network tile reads sob controle at 53,2%");
else { failures++; console.log("  FAIL network tile missing 'sob controle'"); }
/* Volume tiles must carry no target: nobody steers admissions. */
const kpiBlock = utiPan.slice(0, utiPan.indexOf('class="row"'));
const alvos = (kpiBlock.match(/alvo /g) || []).length;
if (alvos === 2) console.log(`  ok   only the 2 rate tiles carry a target (${alvos})`);
else { failures++; console.log(`  FAIL ${alvos} tiles carry a target, expected 2`); }

console.log("=== caveat strip retired in favour of info affordances ===");
if (!/class="caveat"/.test(html)) console.log("  ok   standing caveat strip removed");
else { failures++; console.log("  FAIL caveat strip still present in the markup"); }
STATE.visao = "rede";
let infoCount = 0;
for (let t = 0; t < 4; t++) { STATE.tab = t; infoCount += (TABS[t]().match(/class="infob"/g) || []).length; }
if (infoCount >= 5) console.log(`  ok   ${infoCount} info affordances across the four tabs`);
else { failures++; console.log(`  FAIL only ${infoCount} info affordances found`); }

console.log("=== reset clears visão too ===");
STATE.visao = "uti"; STATE.periodo = "pand"; STATE.anos = [2020, 2021];
STATE.rotulo = "Pandemia · 2020–2021"; STATE.tab = 0;
show(0);
click("f-reset");
if (STATE.visao === "rede" && STATE.periodo === "todos")
  console.log("  ok   reset restores both period and visão");
else { failures++; console.log(`  FAIL reset left visao=${STATE.visao}, periodo=${STATE.periodo}`); }

console.log();
console.log(failures ? `${failures} FAILURE(S)` : "ALL CHECKS PASSED");
process.exit(failures ? 1 : 0);
