# Security

## Reporting
Email the project owner (cuteypieanika@gmail.com) with a description and reproduction steps. Please do not open a public issue for a security report.

## Supported versions
Only the latest release receives fixes.

## Scope notes
ProofGarden executes no user-supplied code beyond its own restricted grammars: formulas are parsed, not evaluated as Python; models are JSON data with explicit edges. The browser playground makes no network requests and stores only learning progress in `localStorage`.
