/* Node test suite for the browser logic engine.
   Run: node --test tests/playground/
   The playground files are plain scripts that attach to a global `window`,
   so each one is evaluated in its own sandbox. */

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadPlaygroundScript(...names) {
  const context = { window: {}, console };
  vm.createContext(context);
  for (const name of names) {
    const file = path.join(__dirname, '..', '..', 'playground', 'js', name);
    vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: name });
  }
  return context.window;
}

const { LogicLab } = loadPlaygroundScript('logic.js');

test('tautology is classified as tautology', () => {
  const table = LogicLab.truthTable(LogicLab.parse('(P AND Q) IMPLIES P'));
  assert.strictEqual(table.classification, 'tautology');
});

test('contradiction is classified as contradiction', () => {
  const table = LogicLab.truthTable(LogicLab.parse('P AND NOT P'));
  assert.strictEqual(table.classification, 'contradiction');
});

test('xor is contingent', () => {
  const table = LogicLab.truthTable(LogicLab.parse('P XOR Q'));
  assert.strictEqual(table.classification, 'contingent');
});

test('truth table has 2^n rows', () => {
  const table = LogicLab.truthTable(LogicLab.parse('(P AND Q) OR R'));
  assert.strictEqual(table.rows.length, 8);
  assert.strictEqual(JSON.stringify(table.names.slice().sort()), JSON.stringify(['P', 'Q', 'R']));
});

test('AND binds tighter than OR', () => {
  // P OR (Q AND R) is false when P is false and R alone is true,
  // which distinguishes it from (P OR Q) AND R.
  const table = LogicLab.truthTable(LogicLab.parse('P OR Q AND R'));
  const falsifying = table.rows.filter((row) => row.result === false);
  assert.strictEqual(falsifying.length, 3);
  const loneR = table.rows.find((row) => row.env.P === false && row.env.Q === false && row.env.R === true);
  assert.strictEqual(loneR.result, false);
  const qr = table.rows.find((row) => row.env.P === false && row.env.Q === true && row.env.R === true);
  assert.strictEqual(qr.result, true);
});

test('de morgan equivalence holds', () => {
  const left = LogicLab.truthTable(LogicLab.parse('NOT (P AND Q)'));
  const right = LogicLab.truthTable(LogicLab.parse('(NOT P) OR (NOT Q)'));
  assert.strictEqual(JSON.stringify(left.rows.map((r) => r.result)), JSON.stringify(right.rows.map((r) => r.result)));
});

test('implication is not commutative', () => {
  const a = LogicLab.truthTable(LogicLab.parse('P IMPLIES Q'));
  const b = LogicLab.truthTable(LogicLab.parse('Q IMPLIES P'));
  assert.notStrictEqual(JSON.stringify(a.rows.map((r) => r.result)), JSON.stringify(b.rows.map((r) => r.result)));
});

test('evaluation follows the assignment', () => {
  const expr = LogicLab.parse('(P IFF Q) XOR R');
  assert.strictEqual(LogicLab.evaluate(expr, { P: true, Q: true, R: false }), true);
  assert.strictEqual(LogicLab.evaluate(expr, { P: true, Q: true, R: true }), false);
});

test('malformed input is rejected, not executed', () => {
  assert.throws(() => LogicLab.parse('P AND'), /./);
  assert.throws(() => LogicLab.parse('((P)'), /./);
  assert.throws(() => LogicLab.parse('P @ Q'), /./);
});
