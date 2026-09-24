# collection protocol — a Vietnamese SMS corpus from consenting contributors

**STATUS: DRAFT, NOT APPROVED.** Written 2026-09-24, before a single message was collected and
before anyone was asked to take part. It becomes a protocol when the author obtains written
ethics approval, fills the consent form, removes this status line and commits;
`sms_collect.py` refuses everything except `--check` until then, and `tests/test_sms_corpus.py`
checks that it does.

Nothing here can be repaired afterwards. Consent cannot be obtained retroactively, and a corpus
collected without it cannot be published, cited or fixed — only discarded. That is why this file
exists before the first message rather than beside the first draft.

---

## 1. What this corpus is, and what it deliberately is not

A **pilot** corpus of Vietnamese SMS, contributed by a small number of consenting adults. It is
called a pilot in the data article's abstract, not only in its limitations: **TO SET** contributors
at **TO SET** messages each is a few hundred to about fifteen hundred messages, which is enough to
study labelling, templates and splitting, and not enough to describe Vietnamese smishing.

**Only two kinds of message are collected.**

- **Scam and spam**, of any sender. These were broadcast to strangers by someone with no privacy
  interest in them.
- **Legitimate messages sent by a machine**: one-time codes, bank and telecommunications
  notifications, school and application notices — messages from a brandname or a service
  shortcode.

**Person-to-person messages are never collected.** A message a friend or a relative sent is
*theirs*, and they are not present to consent; a contributor can give away what is their own and
nobody can consent on a sender's behalf. This is also the right line for the problem: a message
from a friend teaches a smishing detector nothing. The rule the guideline states is mechanical —
**a message from a personal phone number is not collected, whatever it says.**

## 2. The consent design

Contributors may be students, and the author teaches. A student asked by a lecturer for phone data
is not free to refuse, and a consent form does not fix that by itself. The design removes the
asymmetry rather than documenting it:

1. **The invitation does not come from anyone who grades them.** A colleague with no assessment
   role over the cohort recruits.
2. **Nothing is attached to participation.** No marks, no credit, no bonus, no attendance, and no
   mention in class of who took part.
3. **Submission is anonymous.** The author never learns who participated, so declining costs
   nothing and cannot be noticed.
4. **Withdrawal needs no reason** and is possible until deposit, after which the author cannot
   identify which messages to remove — and the consent form says so in those words rather than
   promising a deletion that cannot be performed.

## 3. Redaction, on the contributor's device

On the primary route what leaves the phone is already redacted, and the raw text never reaches the
author. The redaction
tool is a single offline web page opened in the phone's own browser: the contributor copies a
message in their messaging app and pastes it in, so the text arrives character for character and
no screenshot or OCR is involved. The page makes no network request and works in airplane mode.
It replaces each of these with its placeholder, and the contributor reviews every message after
redaction and before sending. A message they are unsure about is not sent. `CONTRIBUTE_vi.md`
tells contributors how, step by step.

**The alternative route, screenshots.** A message that cannot be copied may be sent as a
screenshot, cropped to the sender and the message, with the contributor's own details blacked out
on the image, in a `.zip` file. On this route the author does see an unredacted image, and the
consent form says so in those words rather than promising otherwise. The author takes responsibility
for these images: file names and metadata are stripped on receipt, each image is transcribed by
OCR and checked by hand, the text is redacted as above, and the image is deleted once checked and
before publication. Every row records its route in `capture`, because OCR can normalise the
obfuscating spellings this section keeps on purpose, and a reader studying them needs to exclude
the transcribed rows.

```
<NAME> <PHONE> <ACCOUNT> <OTP> <EMAIL> <URL> <AMOUNT> <ADDRESS> <ID> <DATE> <TIME> <TRANSACTION_ID>
```

**Normalisation stops there.** Odd punctuation, capitalisation, missing diacritics, typos, unusual
Unicode and filter-evading spellings are *kept exactly*. They are among the strongest signals a
smishing message carries, and a corpus that tidies them away has removed the thing it exists to
measure.

## 4. Labels

Three classes, not two. A binary corpus cannot be made finer later; a three-class one collapses
in a line.

| label | what it means |
|---|---|
| `legitimate` | a genuine message from the organisation it appears to come from |
| `spam` | unsolicited or promotional, with no evidence of intent to obtain credentials, money or information by deception |
| `phishing` | impersonates an organisation or person, or seeks credentials, a one-time code, a payment, a call-back or an app install under a false pretext |

For a binary experiment: `legitimate` + `spam` → 0, `phishing` → 1. Both the three-class labels
and the collapse rule ship with the corpus, so a reader may disagree with the collapse.

`uncertain` is a fourth value an annotator may use and the corpus never carries: it marks a
message for adjudication. **A message is not made `phishing` because it looks suspicious.**
Evidence of deceptive intent is required, and where it is absent the message is `spam`.

## 5. Annotation, and what is reported about it

Two annotators label every message **independently**, neither seeing the other's labels nor the
contributor's own. Disagreements and every `uncertain` go to an adjudicator, whose decision is
`final_label`.

Three things are reported whatever they show: **Cohen's kappa** between the two annotators before
adjudication, the **disagreement rate per class pair**, and the share adjudicated. A low kappa is
a result about how separable these classes are in practice, and it is published as one rather
than repaired by relabelling until the annotators agree.

## 6. Templates

Scam SMS is sent by template, and after redaction fifty one-time-code messages become the same
string. Grouping them is what makes an honest split possible.

Grouping is **computed, not assigned by hand**: messages are lower-cased, placeholder tokens kept,
whitespace collapsed; each becomes the set of its word 4-shingles; pairs at or above Jaccard
**τ = 0.8** are linked and a template is a connected component. Results at **τ = 0.7 and 0.9** are
reported beside the primary so that chaining is visible. This is the method the kit-reuse study
registers, reused here because it is already written and already argued.

A hand-assigned `template_id` would be unreproducible, and template leakage is exactly the defect
this corpus exists to avoid.

## 7. Splits

**Every message of one template lies in one split.** The published Vietnamese corpus this project
already audits does not do this: 47 of its test rows, 7.9%, repeat a training text. A model tested
across a template boundary is being asked to remember, not to detect.

The primary evaluation is **cross-validation over template groups**. A fixed 70/15/15
template-disjoint split ships with the corpus for presentation, but with a pilot this size its
test half holds too few phishing messages to carry a conclusion, and the paper says so where it
reports it.

**Leave-one-contributor-out** is reported beside it: train on all contributors but one, test on
the one. With **TO SET** contributors that is as many folds, each a single person, so the folds
are reported **individually and never averaged** — it answers "does this transfer to an inbox it
has not seen" qualitatively, and estimates nothing.

## 8. What ships, and what does not

`sms_dataset.csv`: `message_id`, `text` (redacted), `capture`, `final_label`, `label_annotator_1`,
`label_annotator_2`, `template_id`, `sender_type`, `has_url`, `has_phone`, `has_otp`,
`has_money`, `split`. The derived flags are produced by a published regular expression, not by eye.

**`participant_id` does not ship.** With a handful of contributors it is pseudonymisation rather
than anonymisation: anyone who knows the group could read off which bank or which school each of
them uses. It is kept privately so the leave-one-contributor-out result can be computed, and the
paper reports that result without the mapping.

Raw, unredacted text and screenshots never ship. Screenshots are deleted once transcribed and
checked; everything else unredacted is deleted once the redacted corpus is fixed.

## 9. What the paper may claim

One small group, one window, volunteers. It is not a sample of Vietnamese smishing, and the
abstract says so. The corpus's contribution is that it is **labelled by two annotators with the
agreement reported, grouped by template, and split so that no template crosses the boundary** —
which the corpora it sits beside are not.

## 10. Ethics approval

**TO SET:** the approving body, the reference number and the date. If the university has no
process covering this, the written answer saying so is filed here in its place — an absent
process is not an absent question, and a data article's ethics statement has to say which of the
two it is.

## Amendments (dated, append-only)

*(none)*
