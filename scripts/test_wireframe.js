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
  return {
    id, innerHTML: "", style: {}, dataset: {},
    setAttribute() {}, getAttribute() { return null; },
    addEventListener(ev, fn) { (listeners[id + ":" + ev] ||= []).push(fn); },
    appendChild() {}, closest() { return null; },
  };
}
const els = {};
const document = {
  getElementById(id) { return (els[id] ||= makeEl(id)); },
  querySelectorAll() { return []; },
  createElement(tag) { return makeEl("new-" + tag); },
  addEventListener() {},
};
globalThis.document = document;

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
;globalThis.__probe = { TABS, STATE, PERIODOS, show, renderFilters };
`;
try {
  new Function(src + probe)();
} catch (e) {
  console.error("FAIL: script threw on initialisation:", e.message);
  console.error(e.stack.split("\n").slice(0, 4).join("\n"));
  process.exit(1);
}
const { TABS, STATE, PERIODOS, show } = globalThis.__probe;
const names = ["Panorama", "Territorio", "Capacidade", "Custo"];

console.log("=== all tabs, all period presets ===");
for (const p of PERIODOS) {
  STATE.periodo = p.id; STATE.anos = p.anos.slice(); STATE.rotulo = p.rotulo;
  for (let t = 0; t < 4; t++) {
    STATE.tab = t;
    try { check(`${p.rotulo} / ${names[t]}`, TABS[t]()); }
    catch (e) { failures++; console.log(`  FAIL ${p.rotulo} / ${names[t]}: threw ${e.message}`); }
  }
}

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

console.log();
console.log(failures ? `${failures} FAILURE(S)` : "ALL CHECKS PASSED");
process.exit(failures ? 1 : 0);
