# scripts/ — the pipeline, in the order it runs

Every stage reads files and writes files, so any of it can be rerun and checked; nothing lives in
a shell history. Two stages collect and therefore refuse to run until the protocol and the
consent form are real (`sms_collect.py --check` prints what is missing); the later stages operate
on data already held, and gate nothing.

```
contributor's phone                    author's machine
───────────────────                    ────────────────────────────────────────────────
redact.html (paste route) ──────────→  submission rows
screenshots in a .zip ──────────────→  sms_transcribe.py extract → draft.csv, checked by
                                       hand against each image → finalize → ingest/<token>.csv
                                       sms_collect.py --ingest → data/raw/.../submissions.csv
                                       sms_annotate.py init → data/private/sms_working.csv
                                       sms_import.py <published corpus> → appended, for re-annotation
                                       sms_annotate.py label --annotator 1   (independently: 2)
                                       sms_annotate.py adjudicate --by <name> → final_label
                                       sms_templates.py --assign → template_id
                                       sms_split.py --assign → split
                                       sms_publish.py → data/sms_dataset.csv (at deposit)
```

| script | what it does, and the rule it enforces |
|---|---|
| `redact.html` | the redaction page a contributor opens offline on their own phone. Holds **the one copy of the redaction rules**; `sms_transcribe.py` and `sms_templates.py` read them out of this file, so the routes cannot drift. |
| `sms_transcribe.py` | the author's side of the screenshot route: `extract` re-encodes images from pixels alone (no name or metadata survives), OCRs them and writes a draft; the hand check sits between the two commands; `finalize` redacts, refuses rows that still fail the schema, and **deletes the images**. Gated: receiving screenshots is collecting. |
| `sms_collect.py` | the collector. `--check` prints what still blocks collection; `--ingest` validates each submission row (reviewed, sender type, month format, capture route) and appends to `submissions.csv`. Gated. |
| `sms_import.py` | the imported subset (protocol §1): a published corpus's rows appended to the working file for blind re-annotation — placeholder tokens mapped by an allowlist, the source's binary label kept in `label_source` where no annotator sees it, rows failing SCHEMA rule 2 dropped and named, never repaired. Not collection, so not gated. |
| `sms_annotate.py` | `init` builds the working file (message_id, participant_id — the reason `data/` is private); `label` shows an annotator **the text and nothing else**, so the two annotators and the contributor stay independent; `adjudicate` finalizes agreements without an adjudicator and decides the rest with a recorded name and a one-line note; `report` prints Cohen's kappa, disagreements per class pair and the share adjudicated — whatever they show. |
| `sms_templates.py` | groups messages into templates on a normalized view (URLs and amounts tokenized for grouping only), word 4-shingles, Jaccard τ = 0.8, connected components; reports τ = 0.7/0.9 beside it so chaining is visible. `--assign` writes `template_id`. |
| `sms_split.py` | the fixed 70/15/15 split, assigned **per template, never per message**; greedy over seeded restarts, scored on size and label mix; seed and restart count are constants in the file, so the split reproduces from the working file alone. `--assign` writes `split`. |
| `sms_publish.py` | the projection of SCHEMA_raw §3, mechanical because a promise about a manual step is worth nothing: keeps SCHEMA.md's columns, derives the four `has_*` flags from redact.html's patterns and the placeholders, and refuses a working file with holes — `uncertain` never ships, and neither does a row without a template or a split. |

`label` and `adjudicate` are interactive and run in a terminal; everything else is batch. The
report modes (`sms_templates.py`, `sms_split.py`, `sms_annotate.py report`) write nothing and are
safe to run at any point.

Tests: `python3 -m unittest discover tests` — the page and `sms_transcribe.py` held to one list
of redaction cases, the screenshot route end to end, and the later stages to their invariants:
rotated slots group as one template, no template crosses a split, agreements finalize without an
adjudicator, and the projection ships exactly SCHEMA.md's columns.
