# phishvn-sms

A Vietnamese SMS corpus of scam messages, contributed by consenting students.

## Nothing has been collected

**No message exists in this repository, and none has been collected anywhere else.** There is no
ethics approval yet, the collection protocol is still a draft, and the consent form still has
blanks in it. `sms_collect.py` reads those two documents and refuses to collect while any of that
is true; `--check` prints what is missing.

```
$ python3 sms_collect.py --check
{
  "ready_to_collect": false,
  "missing": [
    "the protocol still carries its DRAFT status line",
    "the protocol has 2 unfilled 'TO SET' field(s) ...",
    "the consent form still carries its draft banner",
    "the consent form has 5 unfilled placeholder(s) ..."
  ]
}
```

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

**Redaction happens on the contributor's device.** What leaves the phone is already redacted, and
the contributor reviews each message before sending it. The raw text never reaches the researcher.

## The consent design

The researcher teaches, and a student asked by their lecturer for phone data is not free to
refuse. The protocol removes that asymmetry rather than documenting it: recruitment by someone
with no assessment role over the cohort, nothing attached to participation, anonymous submission
so that declining cannot be noticed, and withdrawal without reason until deposit.

The consent form states in plain Vietnamese that publication is permanent and that withdrawal is
impossible afterwards, because the researcher will not know which messages are whose. It asks for
no signature: a signature would turn an anonymous submission into an identified one.

## Files

| file | what it is |
|---|---|
| `PROTOCOL_sms_corpus.md` | the collection protocol; carries its DRAFT status line until approved |
| `CONSENT_vi.md` | the participant consent form, in Vietnamese — the operative document |
| `CONSENT_en.md` | its English translation, so a reviewer who does not read Vietnamese can check what contributors were told; the Vietnamese governs |
| `sms_collect.py` | the collector; refuses everything but `--check` until both documents are real |
| `SCHEMA.md` | the published file's fields, the rules a valid file satisfies, and what is withheld |
| `EXAMPLE_synthetic.csv` | six invented rows showing the shape; not collected data, nobody sent them |
| `data/` | empty, and stays empty until there is approval |
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
