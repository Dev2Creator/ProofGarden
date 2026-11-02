# Contributing

ProofGarden is source-available under a custom EULA. Before contributing code, text or examples, contact the project owner for written permission; contributions that are accepted are licensed to the owner under the EULA.

## Standards
- Python 3.11+, standard library preferred.
- Type hints and docstrings on public functions.
- One behaviour change per commit with a test.
- Never introduce `eval`/`exec` on user input.
- Run `python -m unittest discover -s tests` before proposing a change.
