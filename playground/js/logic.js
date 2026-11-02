/* Propositional logic engine for the browser.
   Mirrors proofgarden/logic: explicit lexer + recursive-descent parser.
   No eval() is ever used. */

const LogicLab = (() => {
  const KEYWORDS = {
    NOT: 'NOT', AND: 'AND', OR: 'OR', XOR: 'XOR', IMPLIES: 'IMPLIES', IFF: 'IFF',
    TRUE: 'CONST', FALSE: 'CONST'
  };
  const SYMBOLS = {
    '~': 'NOT', '!': 'NOT', '¬': 'NOT',
    '&': 'AND', '&&': 'AND', '∧': 'AND',
    '|': 'OR', '||': 'OR', '∨': 'OR',
    '^': 'XOR', '⊕': 'XOR',
    '->': 'IMPLIES', '=>': 'IMPLIES', '→': 'IMPLIES',
    '<->': 'IFF', '<=>': 'IFF', '↔': 'IFF'
  };
  const MULTI = ['<->', '<=>', '->', '=>', '&&', '||'];

  function tokenize(src) {
    const tokens = [];
    let i = 0;
    while (i < src.length) {
      const ch = src[i];
      if (/\s/.test(ch)) { i++; continue; }
      if (ch === '(') { tokens.push({ kind: 'LPAREN', pos: i }); i++; continue; }
      if (ch === ')') { tokens.push({ kind: 'RPAREN', pos: i }); i++; continue; }
      let matched = null;
      for (const sym of MULTI) if (src.startsWith(sym, i)) { matched = sym; break; }
      if (matched) { tokens.push({ kind: SYMBOLS[matched], pos: i }); i += matched.length; continue; }
      if (SYMBOLS[ch]) { tokens.push({ kind: SYMBOLS[ch], pos: i }); i++; continue; }
      if (/[A-Za-z_]/.test(ch)) {
        const start = i;
        while (i < src.length && /[A-Za-z0-9_]/.test(src[i])) i++;
        const word = src.slice(start, i);
        const kind = KEYWORDS[word.toUpperCase()] || 'NAME';
        tokens.push({ kind, text: word, pos: start });
        continue;
      }
      throw new Error(`unexpected character ${JSON.stringify(ch)} at position ${i + 1}`);
    }
    tokens.push({ kind: 'EOF', pos: src.length });
    return tokens;
  }

  function parse(src) {
    if (!src.trim()) throw new Error('empty formula');
    const tokens = tokenize(src);
    let index = 0;
    const cur = () => tokens[index];
    const advance = () => tokens[index++];

    function parseIff() {
      let e = parseImplies();
      while (cur().kind === 'IFF') { advance(); e = { op: 'IFF', left: e, right: parseImplies() }; }
      return e;
    }
    function parseImplies() {
      const left = parseOr();
      if (cur().kind === 'IMPLIES') { advance(); return { op: 'IMPLIES', left, right: parseImplies() }; }
      return left;
    }
    function parseOr() {
      let e = parseXor();
      while (cur().kind === 'OR') { advance(); e = { op: 'OR', left: e, right: parseXor() }; }
      return e;
    }
    function parseXor() {
      let e = parseAnd();
      while (cur().kind === 'XOR') { advance(); e = { op: 'XOR', left: e, right: parseAnd() }; }
      return e;
    }
    function parseAnd() {
      let e = parseUnary();
      while (cur().kind === 'AND') { advance(); e = { op: 'AND', left: e, right: parseUnary() }; }
      return e;
    }
    function parseUnary() {
      if (cur().kind === 'NOT') { advance(); return { op: 'NOT', operand: parseUnary() }; }
      return parseAtom();
    }
    function parseAtom() {
      const tok = cur();
      if (tok.kind === 'NAME') { advance(); return { type: 'var', name: tok.text }; }
      if (tok.kind === 'CONST') { advance(); return { type: 'const', value: tok.text.toUpperCase() === 'TRUE' }; }
      if (tok.kind === 'LPAREN') {
        advance();
        const e = parseIff();
        if (cur().kind !== 'RPAREN') throw new Error(`expected ')' at position ${cur().pos + 1}`);
        advance();
        return e;
      }
      throw new Error(`expected a variable, constant or '(' at position ${tok.pos + 1}`);
    }

    const expr = parseIff();
    if (cur().kind !== 'EOF') throw new Error(`unexpected trailing input at position ${cur().pos + 1}`);
    return expr;
  }

  function variables(expr, acc = new Set()) {
    if (expr.type === 'var') acc.add(expr.name);
    else if (expr.operand) variables(expr.operand, acc);
    else if (expr.left) { variables(expr.left, acc); variables(expr.right, acc); }
    return acc;
  }

  function evaluate(expr, env) {
    if (expr.type === 'const') return expr.value;
    if (expr.type === 'var') {
      if (!(expr.name in env)) throw new Error(`missing value for ${expr.name}`);
      return env[expr.name];
    }
    if (expr.op === 'NOT') return !evaluate(expr.operand, env);
    const a = evaluate(expr.left, env);
    if (expr.op === 'AND') return a && evaluate(expr.right, env);
    if (expr.op === 'OR') return a || evaluate(expr.right, env);
    if (expr.op === 'XOR') return a !== evaluate(expr.right, env);
    if (expr.op === 'IMPLIES') return !a || evaluate(expr.right, env);
    if (expr.op === 'IFF') return a === evaluate(expr.right, env);
    throw new Error(`unknown operator ${expr.op}`);
  }

  function truthTable(expr) {
    const names = Array.from(variables(expr)).sort();
    if (names.length > 12) throw new Error('too many variables for a table in the browser (max 12)');
    const rows = [];
    const total = 2 ** names.length;
    for (let mask = 0; mask < total; mask++) {
      const env = {};
      names.forEach((n, bit) => { env[n] = Boolean(mask & (1 << (names.length - 1 - bit))); });
      rows.push({ env, result: evaluate(expr, env) });
    }
    const values = new Set(rows.map(r => r.result));
    const classification = values.size === 1 ? (rows[0].result ? 'tautology' : 'contradiction') : 'contingent';
    return { names, rows, classification };
  }

  return { parse, evaluate, truthTable, variables };
})();

window.LogicLab = LogicLab;
