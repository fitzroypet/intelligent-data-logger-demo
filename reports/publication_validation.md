# Publication validation — 28 September 2026

- `python -m pytest -q`: **115 passed in 113.95 seconds**. Includes archive-to-explorer
  equality, bounded static build, outage provenance and separation of primary/post-hoc
  live scores. Existing mocked model tests remain mocked, distinct from the paid pilot.
- `python scripts/verify_research_run.py reports/research/offline-evaluation`:
  288 episodes, 3,456 predictions, physical checks and all hashes verified.
- Same verifier on development: 96 episodes, 1,152 predictions and all hashes verified.
- `scripts/check_publication_browser.py` against local port 8503 using installed Edge:
  six scenario selections, URL deep link, outage plots, milestone controls, three stress
  selections, live primary/post-hoc distinction, operational dashboard and 320/390/850/
  1440-pixel layouts passed. No JavaScript or CSP errors. An initial 320-pixel header
  overflow was fixed before the passing check. No API calls were made by browser checks.
- README screenshots are actual browser captures under `docs/images/`.
- Original demo JSON evidence, dimensions, outcomes and ground truth agree exactly with
  the archived run. Outage samples come from the original CSV with matching SHA-256.
- Word generation: abstract 228 words, title 12 words, five keywords; manuscript includes
  three tables and three figures. Correspondence-bearing output is ignored by Git.

Live generation is separately archived: 24 conversations, 48 requests, estimated token
cost USD 0.213009; strict JSON 0/24. The preserved connection failure returned no generated
response or usage. Post-hoc parser normalization did not make additional API calls.

The checks establish software and provenance properties. They do not constitute
external domain review, independent human annotation, venue acceptance or field validation.

A fresh export of the committed checkout also passed the dependency-free static build
and evaluation verifier, matching the GitHub Actions build environment's input boundary.
Word ZIP/XML integrity, author/contact presence, 12 pt Times New Roman, double-spacing,
three tables and three figures were verified programmatically. Optional Microsoft Word
PDF rendering stalled and was stopped; no PDF or full visual pagination validation is
claimed. The saved .docx files remain the deliverables for author inspection.

GitHub Pages workflow [36395722747](https://github.com/Engr-Daniel/intelligent-data-logger-demo/actions/runs/36395722747)
succeeded for release commit 01e9522. Public checks at
https://engr-daniel.github.io/intelligent-data-logger-demo/ passed for all eight artifact
hashes, outage deep link/trace, research navigation, stress selection, primary pilot
failure disclosure and 320 px layout. .env and backend API paths returned HTTP 404.
