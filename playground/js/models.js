/* Bundled example models. Embedded so the playground works from file://
   without a server and without network access. */

window.PG_MODELS = [
  {
    id: 'traffic_light',
    name: 'Traffic light',
    description: 'Red → green → amber → red. One timer transition per step.',
    variables: ['light'],
    initial: [{ light: 'red' }],
    edges: [
      { label: 'timer', from: { light: 'red' }, to: { light: 'green' } },
      { label: 'timer', from: { light: 'green' }, to: { light: 'amber' } },
      { label: 'timer', from: { light: 'amber' }, to: { light: 'red' } }
    ],
    invariants: [
      { name: 'no_undefined_signal', description: 'light is never "undefined"', forbidden: { light: 'undefined' } }
    ]
  },
  {
    id: 'counter_overflow',
    name: 'Counter overflow',
    description: 'A 2-bit counter that was allowed to reach 4.',
    variables: ['count'],
    initial: [{ count: 0 }],
    edges: [
      { label: 'inc', from: { count: 0 }, to: { count: 1 } },
      { label: 'inc', from: { count: 1 }, to: { count: 2 } },
      { label: 'inc', from: { count: 2 }, to: { count: 3 } },
      { label: 'inc', from: { count: 3 }, to: { count: 4 } },
      { label: 'reset', from: { count: 4 }, to: { count: 0 } }
    ],
    invariants: [
      { name: 'counter_below_4', description: 'count <= 3', forbidden: { count: 4 } }
    ]
  },
  {
    id: 'deadlock_locks',
    name: 'Deadlock (two locks)',
    description: 'Two threads take two locks in opposite order.',
    variables: ['a', 'b'],
    initial: [{ a: 'free', b: 'free' }],
    edges: [
      { label: 't1_acquire_a', from: { a: 'free', b: 'free' }, to: { a: 'held_by_t1', b: 'free' } },
      { label: 't2_acquire_b', from: { a: 'free', b: 'free' }, to: { a: 'free', b: 'held_by_t2' } },
      { label: 't1_wait_b', from: { a: 'held_by_t1', b: 'free' }, to: { a: 'held_by_t1', b: 'held_by_t2' } },
      { label: 't2_wait_a', from: { a: 'free', b: 'held_by_t2' }, to: { a: 'held_by_t1', b: 'held_by_t2' } }
    ],
    invariants: []
  },
  {
    id: 'bank_withdrawal',
    name: 'Bank withdrawal',
    description: 'A withdrawal without a bounds check can go negative.',
    variables: ['balance'],
    initial: [{ balance: 2 }],
    edges: [
      { label: 'withdraw', from: { balance: 2 }, to: { balance: 1 } },
      { label: 'withdraw', from: { balance: 1 }, to: { balance: 0 } },
      { label: 'withdraw', from: { balance: 0 }, to: { balance: -1 } },
      { label: 'deposit', from: { balance: -1 }, to: { balance: 0 } }
    ],
    invariants: [
      { name: 'balance_never_negative', description: 'balance >= 0', forbidden: { balance: -1 } }
    ]
  }
];
