# Data article — outline

A skeleton for the data-descriptor paper, structured after the *Data in Brief* template (the same
sections an IEEE Access data article uses). Design facts are filled in; every number that depends
on annotation or ethics approval is a bracketed placeholder `[FILL: …]`, never invented. Prose in
the repo it draws on: `PROTOCOL_sms_corpus.md` (design and rationale), `SCHEMA.md` /
`SCHEMA_raw.md` (fields), `EXTERNAL_QAVN.md` (the benchmark's pin), `CONSENT_vi.md` (consent).

---

## Title

*A working title:* **PhishVN-SMS: a template-disjoint, three-class Vietnamese SMS corpus with
consent-first collection and an external benchmark.**

## Abstract (≤ 150 words)

One paragraph: what the dataset is (a Vietnamese SMS corpus, three classes), how it was built
(consent-first from volunteers; redaction on the contributor's device; two independent annotators
with adjudication), what makes it methodologically distinct (URLs kept as signal; templates
grouped by a reproducible computation; a split no template crosses), and that a published corpus
is used as a **held-out external benchmark** with its own labels. State plainly it is a **pilot**,
not a sample of Vietnamese smishing. Close with the number of messages and the licence.
*Draft last — after the numbers exist.*

## Specifications Table

| | |
|---|---|
| Subject | Computer Science — Security and Privacy; NLP |
| Specific subject area | SMS spam/scam (smishing) detection, Vietnamese |
| Type of data | Table (CSV); redacted text with derived flags and labels |
| How data were acquired | Volunteer contribution (paste via an offline redaction page, or blacked-out screenshots); external benchmark from a published corpus (`EXTERNAL_QAVN.md`) |
| Data format | Redacted, analysed (labelled, grouped, split) |
| Description of data collection | Consent-first; only machine-sent messages (scam/spam and legitimate brandname/shortcode traffic); never person-to-person; redaction before the raw text leaves the device |
| Data source location | Vietnam; contributors' own handsets. External benchmark: [FILL: QAVN source URL] |
| Data accessibility | Repository: `https://github.com/vuthainguyen1602/phishvn-sms`; dataset deposited at [FILL: deposit DOI/URL] under [FILL: corpus licence] |
| Related research article | [FILL: none / the analysis paper if any] |

## Value of the Data (bullet points)

- Vietnamese-language smishing data is scarce; this one **keeps URLs** (including live phishing
  domains) as a first-class signal rather than stripping them, while masking personal data.
- **Three classes** (`legitimate`/`spam`/`phishing`) with a published collapse rule, so a reader
  who wants a binary task can derive it, but a finer one is available and cannot be recovered from
  a binary corpus.
- **Template-disjoint splits** and a stated grouping computation let others evaluate without the
  train/test template leakage common to existing corpora.
- Shipped with an **independent external benchmark** (a published corpus, unchanged) for
  cross-dataset generalization testing.
- Two-annotator labels ship **unmodified** with the agreement reported, so the labelling can be
  audited rather than trusted.

## Data Description

- **Files.** `sms_dataset.csv` (the contributed corpus) and `sms_external_qavn.csv` (the external
  benchmark). Fields and types: reproduce the tables from `SCHEMA.md`.
- **Size.** Contributed: [FILL: N messages], [FILL: T templates]; class balance [FILL: legitimate/
  spam/phishing counts]. External benchmark: 2,676 messages (1,907 benign, 769 scam) after 315 of
  2,991 dropped by the redaction rule (`EXTERNAL_QAVN.md`).
- **Splits.** Fixed template-disjoint 70/15/15 (train/validation/test) over the contributed
  corpus; the benchmark is entirely `split = external`. Report per-split message and template
  counts and class balance. Note (§7) the pilot's test slice is small.
- **Derived flags.** `has_url`, `has_phone`, `has_otp`, `has_money`, computed by the published
  regular expressions in `scripts/redact.html`.

## Experimental Design, Materials and Methods

Condense `PROTOCOL_sms_corpus.md`:

1. **Scope** (§1) — pilot; only machine-sent messages; two subsets, one of them an external
   benchmark; target [FILL: 30] contributors × ~[FILL: 100] messages.
2. **Consent design** (§2) — recruitment by someone with no assessment role; anonymous submission;
   withdrawal until deposit; no signature. Summarise `CONSENT_vi.md`.
3. **Collection and redaction** (§3) — the two routes; redaction on the contributor's device;
   what is kept (links, broadcast amounts) and masked (personal data in links, own balance).
4. **Label scheme** (§4) — the three classes and the rule that suspicion alone is not phishing.
5. **Annotation** (§5) — two independent human annotators, adjudication, and the reported
   **Cohen's kappa = [FILL]**, per-class-pair disagreement [FILL], share adjudicated [FILL].
6. **Templates** (§6) — normalized view (URLs/amounts tokenized for grouping only), word
   4-shingles, Jaccard τ = 0.8, connected components; counts reported at τ = 0.7/0.9.
7. **Splits** (§7) — template-disjoint; leave-one-contributor-out reported per fold; the external
   benchmark scored with predictions collapsed to the source's binary labels.
8. **External benchmark** (§7, `EXTERNAL_QAVN.md`) — provenance, SHA-256 pin, and the measured
   **scheme divergence**: [FILL: benign→spam %] of the source's benign rows read as `spam` under
   the three-class scheme, [FILL: scam→legitimate %] of its scam rows as `legitimate`; no external
   template coincides with a training template.

## Limitations

- A pilot from a small volunteer group in one window: **not** a representative sample of Vietnamese
  smishing; the designed class ratio is not any inbox's prevalence.
- The external benchmark inherits its source's collection bias (sources, period, heavy operator
  traffic); it tests generalization, it does not remove bias.
- `screenshot`-route rows are OCR transcriptions; obfuscating spellings may not survive them
  (excluded via `capture` for character-level study).
- [FILL: any other, e.g. annotator pool size, single adjudicator].

## Ethics Statement

- [FILL: approving body, reference number, date — or the filed written answer that no process
  covers this], per `PROTOCOL_sms_corpus.md` §10.
- Consent obtained before collection; the protocol and consent form were public and timestamped
  before the first message (repository history).
- No personal data collected; redaction before raw text leaves the device; screenshots deleted
  after transcription. The pilot batch from the author's own inbox is [FILL: included / excluded]
  per the ethics application.
- External benchmark reused under CC BY 4.0 with attribution; its own labels shipped unchanged.

## CRediT author statement

[FILL: per author — Conceptualization, Methodology, Software, Data curation, Writing, Supervision.]

## Acknowledgments

The authors of the *Quality-Assured Vietnamese SMS Phishing Dataset* (`EXTERNAL_QAVN.md`) for the
benchmark under CC BY 4.0; [FILL: contributors, funders]. An AI coding assistant (Claude) was used
to help develop the processing scripts; all data labels are human-assigned.

## Declaration of competing interest

[FILL: none, or as applicable.]

## References

- The external benchmark's citation (BibTeX in `EXTERNAL_QAVN.md`).
- [FILL: the 2017 operator corpus; related smishing/dataset work; the kit-reuse grouping method
  §6 reuses.]
