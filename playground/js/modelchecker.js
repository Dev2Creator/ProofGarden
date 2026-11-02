/* Breadth-first exploration over the bundled example models.
   Mirrors proofgarden/modelchecking: same outcome vocabulary. */

window.ModelChecker = (() => {
  const key = (state) => JSON.stringify(Object.entries(state).sort());

  function matches(state, pattern) {
    return Object.entries(pattern).every(([k, v]) => state[k] === v);
  }

  function explore(model, maxStates = 5000) {
    const parents = new Map();   // key -> { parentKey, label }
    const states = new Map();    // key -> state object
    const order = [];
    const edges = [];
    const queue = [];

    model.initial.forEach((s) => {
      const k = key(s);
      if (!parents.has(k)) {
        parents.set(k, { parent: null, label: null });
        states.set(k, s);
        queue.push(k);
      }
    });

    let complete = true;
    let stopReason = null;

    while (queue.length) {
      const k = queue.shift();
      order.push(k);
      const state = states.get(k);
      const outgoing = model.edges.filter((e) => key(e.from) === k);
      outgoing.forEach((edge) => {
        const targetKey = key(edge.to);
        edges.push({ from: k, label: edge.label, to: targetKey });
        if (!parents.has(targetKey)) {
          if (states.size >= maxStates) {
            complete = false;
            stopReason = `state limit of ${maxStates} reached`;
            return;
          }
          parents.set(targetKey, { parent: k, label: edge.label });
          states.set(targetKey, edge.to);
          queue.push(targetKey);
        }
      });
      if (!complete) break;
    }

    const deadlocks = order.filter((k) => !model.edges.some((e) => key(e.from) === k));

    return { order, states, parents, edges, deadlocks, complete, stopReason };
  }

  function pathTo(result, targetKey) {
    const path = [];
    let cursor = targetKey;
    while (cursor !== null && cursor !== undefined) {
      const node = result.parents.get(cursor);
      if (!node) break;
      path.push({ state: result.states.get(cursor), label: node.label });
      cursor = node.parent;
    }
    return path.reverse();
  }

  function checkInvariant(result, invariant) {
    for (const k of result.order) {
      const state = result.states.get(k);
      if (matches(state, invariant.forbidden)) {
        return {
          name: invariant.name, outcome: 'violated',
          message: `Violated by ${JSON.stringify(state)}`,
          trace: pathTo(result, k)
        };
      }
    }
    if (result.complete) {
      return {
        name: invariant.name, outcome: 'verified',
        message: `Holds in all ${result.order.length} reachable states`, trace: null
      };
    }
    return {
      name: invariant.name, outcome: 'incomplete',
      message: `Exploration stopped: ${result.stopReason}`, trace: null
    };
  }

  function checkDeadlock(result) {
    if (result.deadlocks.length) {
      return {
        outcome: 'violated',
        message: `${result.deadlocks.length} state(s) have no outgoing transition`,
        trace: pathTo(result, result.deadlocks[0])
      };
    }
    return result.complete
      ? { outcome: 'verified', message: 'Every reachable state has a successor', trace: null }
      : { outcome: 'incomplete', message: `Exploration stopped: ${result.stopReason}`, trace: null };
  }

  /* Temporal operators over the explored (finite) state graph. */
  function predicateFromText(text) {
    const trimmed = text.trim();
    if (!trimmed) return () => true;
    return (state) => trimmed.split('&').every((part) => {
      const [k, v] = part.split('=').map((s) => s.trim());
      if (k === undefined || v === undefined) return false;
      const target = v === 'true' ? true : v === 'false' ? false : (isNaN(Number(v)) ? v : Number(v));
      return state[k] === target;
    });
  }

  function always(result, predicate) {
    return result.order.every((k) => predicate(result.states.get(k)));
  }

  function eventually(result, predicate) {
    return result.order.some((k) => predicate(result.states.get(k)));
  }

  function until(result, hold, reach) {
    // is there a path where `hold` is true until `reach` becomes true?
    if (!result.complete) return null;
    const queue = result.order.filter((k) => !result.parents.get(k).parent);
    const seen = new Set();
    while (queue.length) {
      const k = queue.shift();
      if (seen.has(k)) continue;
      seen.add(k);
      const state = result.states.get(k);
      if (reach(state)) return true;
      if (!hold(state)) continue;
      result.edges.filter((e) => e.from === k).forEach((e) => queue.push(e.to));
    }
    return false;
  }

  return { explore, checkInvariant, checkDeadlock, pathTo, predicateFromText, always, eventually, until, key };
})();
