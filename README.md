# phishvn-sms

[![tests](https://github.com/vuthainguyen1602/phishvn-sms/actions/workflows/tests.yml/badge.svg)](https://github.com/vuthainguyen1602/phishvn-sms/actions/workflows/tests.yml)

Tools and a protocol for a **private** Vietnamese SMS corpus of scam and machine-sent messages,
used only to evaluate scam-detection models.

**The data are not published (2026-10-17).** No message collected here, under the protocol or
before it, is released as a file, a quotation or a per-message output. The corpus is an evaluation
set: models are scored on it and only aggregate numbers are reported (protocol §8 and the
amendment of that date). The documents, the redaction tools and the tests are public so that how
the data were gathered and handled can be checked.

## Nothing has been collected under the protocol

**No message in this repository was collected under the protocol, and no contributor has been
asked through its consent form.** There is no ethics approval yet, the collection protocol is
still a draft, and the consent form still has blanks in it. `sms_collect.py` reads those two documents and refuses to collect while any of that
is true; `--check` prints what is missing.

```
$ python3 scripts/sms_collect.py --check
{
  "ready_to_collect": false,
  "missing": [
    "the protocol still carries its DRAFT status line",
    "the protocol has 1 unfilled 'TO SET' field(s) ...",
    "the consent form still carries its draft banner",
    "the consent form has 2 unfilled placeholder(s) ..."
  ]
}
```

A **community batch** does exist, and it predates the protocol: 465 messages gathered through a
Google Form, direct requests, hand-copied public Facebook and Threads posts, and a few from the
author's own inbox, with nothing kept about any contributor (protocol, amendment of 2026-10-04).
It is held only on the author's machine, never committed, redacted and ingested by the same
pipeline, and used to exercise it end to end. It is not the corpus: whether any of it may enter
the corpus is a question the ethics application asks explicitly, and until then it counts for
having run the pipeline and for what it taught (the rule-2 amendment of the same date). Since 2026-10-17 one narrower use is allowed: another study may score a
model on it and report aggregate numbers only, never its text (protocol, amendment of that date).

## Why the documents are public before the data

Since 2026-10-17 the data themselves will never be published, and the documents stay public for
the reason below, which still holds for the studies that score models on the data. A data article's ethics statement is a claim about the order events happened in: that the
protocol and the consent form existed *before* the first message, not after. Publishing them now
makes that checkable by anyone, with a timestamp nobody has to take on trust — the same reason a
pre-specification is committed before its analysis. The emptiness of `data/` is the point, not an
oversight.

## What is collected, and what is deliberately not

**Never a message a person wrote.** A message from a friend, a relative or a colleague was
written by somebody who is not present to consent; a contributor can give away what is their own,
and nobody can consent on a sender's behalf. Two kinds of message clear that line and are
collected: **scam and spam** — broadcast to strangers by someone with no privacy interest in
them — and **legitimate messages sent by a machine**: one-time codes, bank and operator
notifications, messages with a brandname or shortcode where there is no human author to ask. The
rule contributors are given is mechanical: a message from a personal phone number is not sent,
whatever it says.

Beside the contributed corpus sits an **external benchmark** (protocol §1, §7): the rows of a
published Vietnamese SMS corpus, taken under its CC BY 4.0 licence and held out as an independent
test set. It is **not** merged in and **not** re-labelled — it keeps the source's own labels, a
model trained here is scored on it, and how far the two label schemes diverge is reported rather
than their labels corrected. Like everything else here it is not redistributed: a reader obtains
it from its publisher.

**Redaction happens on the contributor's device.** The contributor copies each message into an
offline page on their own phone, reviews the redacted text, and sends only that; the raw text never
reaches the researcher. A message that cannot be copied may instead be sent as a cropped,
blacked-out screenshot. On that route the researcher does see the image, the consent form says so,
and the image is deleted once transcribed. Every row records which route it came by.

## The consent design

The researcher teaches, and a student asked by their lecturer for phone data is not free to
refuse. The protocol removes that asymmetry rather than documenting it: recruitment by someone
with no assessment role over the cohort, nothing attached to participation, anonymous submission
so that declining cannot be noticed, and withdrawal without reason until deposit.

The consent form states in plain Vietnamese that publication is permanent and that withdrawal is
impossible afterwards, because the researcher will not know which messages are whose. It asks for
no signature: a signature would turn an anonymous submission into an identified one.

## Files

The written documents live in `docs/`, the code in `scripts/`, and the invented sample rows in
`examples/`.

| file | what it is |
|---|---|
| `docs/PROTOCOL_sms_corpus.md` | the collection protocol; carries its DRAFT status line until approved |
| `docs/CONSENT_vi.md` | the participant consent form, in Vietnamese — the operative document |
| `docs/CONTRIBUTE_vi.md` | how a contributor sends messages, step by step: copy and paste, or screenshots in a `.zip` |
| `docs/CONTRIBUTE_en.md` | its English translation, for the same reason as the consent form's; the Vietnamese governs |
| `docs/CONSENT_en.md` | its English translation, so a reviewer who does not read Vietnamese can check what contributors were told; the Vietnamese governs |
| `docs/SCHEMA.md` | the corpus file's fields and the rules a valid row satisfies (redaction rule 2 among them); written for a publication that will not happen, kept because the pipeline enforces its rules |
| `docs/SCHEMA_raw.md` | the submissions file and the working file, the two files the pipeline actually keeps |
| `docs/FORM_community_vi.md` | the Google Form the community batch came through, verbatim, with an English gloss and what it does and does not promise beside the consent form |
| `docs/EXTERNAL_QAVN.md` | the external benchmark's provenance: its authors, licence, citation, and a SHA-256 pinning the exact copy evaluated |
| `scripts/redact.html` | the redaction page contributors open on their phone; one offline file, no network access, holds the redaction rules |
| `scripts/sms_transcribe.py` | the author's side of the screenshot route: re-encodes images, OCRs them, redacts by the page's rules, deletes the images |
| `scripts/sms_collect.py` | the collector; refuses everything but `--check` until both documents are real |
| `scripts/sms_annotate.py` | the working file and its labels: blind labelling by two annotators, adjudication with a recorded note, and the agreement report |
| `scripts/sms_templates.py` | template grouping on a normalized view of the text, per protocol §6 |
| `scripts/sms_split.py` | the fixed template-disjoint 70/15/15 split, per protocol §7 |
| `scripts/sms_import.py` | the external benchmark: a published corpus's rows mapped into the working file, held out (`split=external`), never annotated, its own label kept |
| `scripts/README.md` | the pipeline in the order it runs, and what each stage refuses |
| `tests/` | the redaction routes held to one list of cases, and the later stages to their invariants — template-disjointness, seeded reproducibility, the projection's exact columns: `python3 -m unittest discover tests` |
| `examples/EXAMPLE_synthetic.csv` | six invented rows showing the shape; not collected data, nobody sent them |
| `examples/EXAMPLE_submission_synthetic.csv`, `examples/EXAMPLE_working_synthetic.csv` | the same six messages at the two private stages; also invented |
| `data/` | private, never committed; `.gitignore` keeps everything but its README out of git. Holds the community batch and the working file on the author's machine only |
| `LICENSE-CODE` | MIT, for the code |
| `LICENSE` | where the corpus licence will go; not one yet, and says why |

## Related

Part of the PhishVN work: [`phishvn`](https://github.com/vuthainguyen1602/phishvn) (corpus and
analysis code), [`phishvn-infra`](https://github.com/vuthainguyen1602/phishvn-infra)
(infrastructure collection), [`phishvn-edge`](https://github.com/vuthainguyen1602/phishvn-edge)
(on-device detector).

## Licence

Code: MIT, in `LICENSE-CODE`, the same file name the sibling repositories use for it.

`LICENSE` is where those repositories keep the **data** licence, and here it is deliberately not
one yet. No corpus exists, and a licence granted now would be a grant over messages nobody has
been asked about. The terms contributors agree to belong in the consent form *before* it is handed
out, not chosen afterwards to fit what was gathered. The corpus licence is settled at deposit,
written into `CONSENT_vi.md` first, and replaces that file then.
