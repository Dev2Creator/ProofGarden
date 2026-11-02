/* Node test suite for the browser model checker.
   Run: node --test tests/playground/ */

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function load(...names) {
  const context = { window: {}, console };
  vm.createContext(context);
  for (const name of names) {
    const file = path.join(__dirname, '..', '..', 'playground', 'js', name);
    vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: name });
  }
  return context.window;
}

const { ModelChecker, PG_MODELS } = load('models.js', 'modelchecker.js');
const model = (id) => PG_MODELS.find((m) => m.id === id);

test('traffic light explores exactly three states', () => {
  const result = ModelChecker.explore(model('traffic_light'));
  assert.strictEqual(result.order.length, 3);
  assert.strictEqual(result.complete, true);
});

test('valid invariant is verified on the traffic light', () => {
  const result = ModelChecker.explore(model('traffic_light'));
  const check = ModelChecker.checkInvariant(result, model('traffic_light').invariants[0]);
  assert.strictEqual(check.outcome, 'verified');
  assert.strictEqual(check.trace, null);
});

test('counter overflow invariant is violated with a five-step trace', () => {
  const m = model('counter_overflow');
  const result = ModelChecker.explore(m);
  const check = ModelChecker.checkInvariant(result, m.invariants[0]);
  assert.strictEqual(check.outcome, 'violated');
  assert.strictEqual(check.trace.length, 5);
  assert.strictEqual(JSON.stringify(check.trace[4].state), JSON.stringify({ count: 4 }));
});

test('trace starts at the initial state', () => {
  const m = model('counter_overflow');
  const check = ModelChecker.checkInvariant(ModelChecker.explore(m), m.invariants[0]);
  assert.strictEqual(JSON.stringify(check.trace[0].state), JSON.stringify({ count: 0 }));
  assert.strictEqual(check.trace[0].label, null);
});

test('deadlock model reports a deadlock with a trace', () => {
  const result = ModelChecker.explore(model('deadlock_locks'));
  const check = ModelChecker.checkDeadlock(result);
  assert.strictEqual(check.outcome, 'violated');
  assert.ok(check.trace.length >= 2);
});

test('state limit produces incomplete, never verified', () => {
  const result = ModelChecker.explore(model('counter_overflow'), 2);
  assert.strictEqual(result.complete, false);
  const check = ModelChecker.checkInvariant(result, model('counter_overflow').invariants[0]);
  assert.strictEqual(check.outcome, 'incomplete');
});

test('temporal operators agree with the explored graph', () => {
  const result = ModelChecker.explore(model('traffic_light'));
  const isAmber = ModelChecker.predicateFromText('light=amber');
  assert.strictEqual(ModelChecker.always(result, isAmber), false);
  assert.strictEqual(ModelChecker.eventually(result, isAmber), true);
  const neverForbidden = ModelChecker.predicateFromText('light=amber');
  assert.strictEqual(ModelChecker.always(result, (s) => s.light !== 'amber'), false);
  assert.strictEqual(ModelChecker.until(result, (s) => s.light !== 'amber', isAmber), true);
});

test('predicate parser reads numbers and strings', () => {
  const p = ModelChecker.predicateFromText('count=4');
  assert.strictEqual(p({ count: 4 }), true);
  assert.strictEqual(p({ count: 3 }), false);
  const q = ModelChecker.predicateFromText('a=free&b=free');
  assert.strictEqual(q({ a: 'free', b: 'free' }), true);
  assert.strictEqual(q({ a: 'free', b: 'held_by_t2' }), false);
});
