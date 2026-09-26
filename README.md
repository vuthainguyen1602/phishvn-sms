# phishvn-sms

A Vietnamese SMS corpus of scam messages, contributed by consenting students.

## Nothing has been collected

**No message exists in this repository, and no contributor has been asked for one.** There is no
ethics approval yet, the collection protocol is still a draft, and the consent form still has
blanks in it. `sms_collect.py` reads those two documents and refuses to collect while any of that
is true; `--check` prints what is missing.

```
$ python3 scripts/sms_collect.py --check
{
  "ready_to_collect": false,
  "missing": [
    "the protocol still carries its DRAFT status line",
    "the protocol has 1 unfilled 'TO SET' field(s) ...",
    "the consent form still carries its draft banner",
    "the consent form has 3 unfilled placeholder(s) ..."
  ]
}
```

The author's own inbox supplied a small pilot batch, held only on the author's machine and never
committed, used to exercise the pipeline end to end. It is not the corpus: whether any of it may
enter the corpus is a question the ethics application asks explicitly, and until then it counts
for nothing but the pipeline having been run.

## Why the documents are public before the data

A data article's ethics statement is a claim about the order events happened in: that the
protocol and the consent form existed *before* the first message, not after. Publishing them now
makes that checkable by anyone, with a timestamp nobody has to take on trust — the same reason a
pre-specification is committed before its analysis. The emptiness of `data/` is the point, not an
oversight.

## What is collected, and what is deliberately not

**Only the scam class.** An ordinary message in a student's phone was written by somebody else —
a friend, a relative, a bank clerk — who is not present to consent. A student can give away what
is theirs; nobody can consent on behalf of a sender. A scam message has no such sender: it was
broadcast to strangers by someone with no privacy interest in it.

The negative class therefore comes from a SIM honeypot, a line with no personal traffic, or from
the ham half of an already published corpus under its licence. Never from a personal inbox.

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
| `docs/SCHEMA.md` | the published file's fields, the rules a valid file satisfies, and what is withheld |
| `docs/SCHEMA_raw.md` | the two files that come before it and never ship, and the exact columns dropped to produce the published one |
| `scripts/redact.html` | the redaction page contributors open on their phone; one offline file, no network access, holds the redaction rules |
| `scripts/sms_transcribe.py` | the author's side of the screenshot route: re-encodes images, OCRs them, redacts by the page's rules, deletes the images |
| `scripts/sms_collect.py` | the collector; refuses everything but `--check` until both documents are real |
| `scripts/sms_annotate.py` | the working file and its labels: blind labelling by two annotators, adjudication with a recorded note, and the agreement report |
| `scripts/sms_templates.py` | template grouping on a normalized view of the text, per protocol §6 |
| `scripts/sms_split.py` | the fixed template-disjoint 70/15/15 split, per protocol §7 |
| `scripts/sms_publish.py` | the projection of SCHEMA_raw §3: the published file from the working file, by dropping columns; refuses a working file with holes |
| `scripts/README.md` | the pipeline in the order it runs, and what each stage refuses |
| `tests/` | the redaction routes held to one list of cases, and the later stages to their invariants — template-disjointness, seeded reproducibility, the projection's exact columns: `python3 -m unittest discover tests` |
| `examples/EXAMPLE_synthetic.csv` | six invented rows showing the shape; not collected data, nobody sent them |
| `examples/EXAMPLE_submission_synthetic.csv`, `examples/EXAMPLE_working_synthetic.csv` | the same six messages at the two private stages; also invented |
| `data/` | empty, and stays empty until there is approval; `.gitignore` keeps everything but its README out of git |
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
