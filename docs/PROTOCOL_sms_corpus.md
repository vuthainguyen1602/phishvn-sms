# collection protocol — a Vietnamese SMS corpus from consenting contributors

**STATUS: DRAFT, NOT APPROVED.** Written 2026-09-24, before a single message was collected and
before anyone was asked to take part. It becomes a protocol when the author obtains written
ethics approval, fills the consent form, removes this status line and commits;
`sms_collect.py` refuses everything except `--check` until then, and `tests/test_redact.py`
checks that it does.

Nothing here can be repaired afterwards. Consent cannot be obtained retroactively, and a corpus
collected without it cannot be published, cited or fixed — only discarded. That is why this file
exists before the first message rather than beside the first draft.

---

## 1. What this corpus is, and what it deliberately is not

A **pilot** corpus of Vietnamese SMS, contributed by a small number of consenting adults. It is
called a pilot in the data article's abstract, not only in its limitations: **30** contributors
at **around 100** messages each is about three thousand messages, which is enough to
study labelling, templates and splitting, and not enough to describe Vietnamese smishing.

The target mix is roughly **800 phishing, 450 spam and 1,800 legitimate** — a designed 1:2
malicious-to-legitimate ratio, not the prevalence of any inbox, and the paper reports per-class
metrics rather than anything that depends on this base rate. Messages are what is collected, but
templates are what the evaluation counts (§6–7): the figure that decides what the corpus can say
is **at least 100 distinct malicious templates**, because another copy of a template already held
adds nothing a template-disjoint split can use. Collection watches the template count as it goes,
and stops adding a contributor's near-duplicates before stopping their novel messages.

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

**Beside the contributed corpus sits an external benchmark, and `source` says which a row is.**
The rows of the *Quality-Assured Vietnamese SMS Phishing Dataset* (CC BY 4.0, credited) are taken
under its licence as a **held-out external test set** (§7): a model trained on the contributed
corpus is evaluated on them, and they are **not merged** into it. They keep the source's own
binary labels — this project does **not** re-annotate them, and does not treat its three-class
scheme as a correction of the source's two-class one; where the two schemes diverge is measured
(§7), not adjudicated. Using published rows this way is not collection and needs no consent chain
of its own; what it needs is honesty about provenance, so external rows carry `source = qavn`,
`capture = imported`, `split = external`, no participant, and the source's placeholder tokens
mapped mechanically to this corpus's. Rows that fail SCHEMA.md rule 2 after mapping are dropped
and counted, not repaired: in the event, 315 of 2,991, most carrying a one-time code the source's
anonymisation missed.

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
author. The redaction tool is a single offline web page opened in the phone's own browser: the
contributor copies a message in their messaging app and pastes it in, so the text arrives
character for character and no screenshot or OCR is involved. The page makes no network request
and works in airplane mode. It replaces each of these with its placeholder, and the contributor reviews every message after
redaction and before sending. A message they are unsure about is not sent. `CONTRIBUTE_vi.md`
tells contributors how, step by step.

```
<NAME> <PHONE> <ACCOUNT> <OTP> <EMAIL> <AMOUNT> <ADDRESS> <ID> <DATE> <TIME> <TRANSACTION_ID>
```

**Links are kept.** The domain and path of a link are the strongest evidence a smishing message
carries, and what the sibling `phishvn-infra` study collects; a link is not personal data, since
it was broadcast to strangers. Only personal data *inside* a link is masked: a phone number, an
e-mail address, or a name or account in its query string (`?sdt=`, `?ten=`, `?stk=`…). A path
segment that identifies the recipient without saying so (`/x7K9q`) cannot be recognised by rule;
the contributor is asked to check each link, and to drop a message whose link carries their own
details.

**Amounts are kept too, except the contributor's own.** A prize, a fee or a price in a scam or an
advert was broadcast to strangers, and the size of a lure is a signal; it stays. A balance, a signed
account movement (`+1.500.000VND`) and an amount beside a transaction (`GD`) are the contributor's
own money, which is sensitive personal data, and are masked as `<AMOUNT>`. An amount the rules cannot
place is kept, and the contributor is asked to check for their balance on review.

**Normalisation stops there.** Odd punctuation, capitalisation, missing diacritics, typos, unusual
Unicode and filter-evading spellings are *kept exactly*. They are among the strongest signals a
smishing message carries, and a corpus that tidies them away has removed the thing it exists to
measure.

**The alternative route, screenshots.** A message that cannot be copied may be sent as a
screenshot, cropped to the sender and the message, with the contributor's own details blacked out
on the image, in a `.zip` file. On this route the author does see an unredacted image, and the
consent form says so in those words rather than promising otherwise. The author takes responsibility
for these images: file names and metadata are stripped on receipt, each image is transcribed by
OCR and checked by hand, the text is redacted as above, and the image is deleted once checked and
before publication. Every row records its route in `capture`, because OCR can normalise the
obfuscating spellings this section keeps on purpose, and a reader studying them needs to exclude
the transcribed rows.

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

**This section is about the contributed corpus only.** The external benchmark (§1, §7) keeps the
source corpus's own labels and is not annotated here.

Two annotators, **both people**, label every contributed message **independently**, neither
seeing the other's labels nor the contributor's own. Disagreements and every `uncertain` go to an
adjudicator, whose decision is `final_label`.

Three things are reported whatever they show: **Cohen's kappa** between the two annotators before
adjudication, the **disagreement rate per class pair**, and the share adjudicated. A low kappa is
a result about how separable these classes are in practice, and it is published as one rather
than repaired by relabelling until the annotators agree.

## 6. Templates

Scam SMS is sent by template, and after redaction fifty one-time-code messages become the same
string. Grouping them is what makes an honest split possible.

Grouping is **computed, not assigned by hand**, and it runs on a **normalized view** of the text
that exists only for this step: messages are lower-cased, whitespace collapsed, placeholder tokens
kept, and every URL and money amount is replaced by a `<URL>` or `<AMT>` token. The published text
keeps both — a link is the strongest signal a phishing message carries, and the size of a lure is
a signal too — but for grouping they are the slots a campaign rotates, and leaving them in place
splits one template into many. The amount patterns for this step extend the redaction rules with
the short forms (one to three digits plus k/tr/tỷ) that redaction rightly ignores — two digits
identify nobody — but grouping must not. Each normalized message becomes the set of its word
4-shingles; pairs at or above Jaccard **τ = 0.8** are linked and a template is a connected
component. Results at **τ = 0.7 and 0.9** are reported beside the primary so that chaining is
visible.

The shingling, the thresholds and the connected components are the method the kit-reuse study
registers; the normalization is this protocol's one departure from it, adopted after a pilot
batch showed the failure it repairs. A scam sent twice with one edited character in the domain,
or with a different lure amount, fell below τ even at 0.7: in a message of eight words, one
changed word destroys four shingles. Counted as different templates, the two copies then land on
opposite sides of a template-disjoint split — the leakage §7 exists to prevent, back in through
another door.

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
the one. With **30** contributors that is as many folds, each a single person, so the folds
are reported **individually and never averaged** — it answers "does this transfer to an inbox it
has not seen" qualitatively, and estimates nothing.

**The external benchmark is a third evaluation, on data collected by no one here.** The
*Quality-Assured Vietnamese SMS Phishing Dataset* (§1) is held out entirely — `split = external`,
never train, validation or test — and a model trained on the contributed corpus is scored on it.
Because its labels are binary (`benign`/`scam`) and this corpus's are three classes, the model's
prediction is collapsed to the source's two classes (`legitimate` → benign, `spam`/`phishing` →
scam) before scoring; the paper reports performance against the source's own labels and does not
relabel them. It also reports, once, **how far the two label schemes diverge** — with a
model-assisted pass, about half the source's benign rows fall under `spam` in the three-class
sense (the operator promotions of §9), while its scam rows almost never read as `legitimate`.
That divergence is the reason the two are kept apart rather than merged: a single pooled label
column would bury it. A template-grouping check confirms **no external template coincides with a
training template**, so the benchmark is genuinely unseen.

## 8. What ships, and what does not

`sms_dataset.csv` (the contributed corpus): `message_id`, `text` (redacted), `source`, `capture`,
`final_label`, `label_annotator_1`, `label_annotator_2`, `template_id`, `sender_type`, `has_url`,
`has_phone`, `has_otp`, `has_money`, `split`. The derived flags are produced by a published
regular expression, not by eye.

`sms_external_qavn.csv` (the external benchmark) ships **separately**, with the source corpus's
own label and nothing this project added to it: `message_id` (a `QAV_` id that traces to the
original), `text` (tokens remapped), `label_source`, `template_id`, `sender_type` and the derived
flags. It carries no `final_label`, no annotator columns and no train split, because none of
those were produced for it (§5, §7).

**`participant_id` does not ship.** With a handful of contributors it is pseudonymisation rather
than anonymisation: anyone who knows the group could read off which bank or which school each of
them uses. It is kept privately so the leave-one-contributor-out result can be computed, and the
paper reports that result without the mapping.

Raw, unredacted text and screenshots never ship. Screenshots are deleted once transcribed and
checked; everything else unredacted is deleted once the redacted corpus is fixed.

## 9. What the paper may claim

One small group, one window, volunteers. It is not a sample of Vietnamese smishing, and the
abstract says so. The corpus's contribution is **method, not novelty of content**: two annotators
with the agreement reported, three classes with a published collapse rule, templates grouped by a
stated computation, and a split no template crosses.

The claim is made against what actually exists, stated precisely because a reviewer will check:

- The external benchmark — the *Quality-Assured Vietnamese SMS Phishing Dataset* (CC BY 4.0,
  2,991 messages, binary labels) — **keeps URLs**, including live phishing domains, and the paper
  must not claim otherwise. It is used as a held-out test set (§7), not corrected: its labels are
  its own. Two facts about it are reported as measurement, not as fault. First, its binary
  boundary is a different question from §4's: it separates *genuine sender* from *scam*, so its
  benign class carries the operators' own promotional messages — a model-assisted pass put about
  half of them under `spam` in the three-class sense, and a hand audit of a sample agreed — where
  §4 calls an unsolicited promotion `spam` whoever sent it. That is a difference of scheme, and
  the paper frames it as one; it is also why the benchmark is scored against its own labels rather
  than merged. Second, its anonymisation missed what a mechanical check catches: mapping it in
  (§1) dropped 315 of 2,991 rows for SCHEMA.md rule 2, most carrying an unmasked one-time code in
  a bank message its README declares clean — what "quality-assured by hand" looks like beside a
  rule a script can hold. Neither point is a claim that the corpus is wrong; both are stated with
  its authors credited, and its own labels shipped unchanged for anyone to check.
- The 2017 operator corpus (5,557 ham and 1,042 spam from Viettel and Vinaphone) is available on
  request only, and whether its texts keep URLs is undocumented; the paper says that and no more,
  unless its authors answer.

## 10. Ethics approval

**TO SET:** the approving body, the reference number and the date. If the university has no
process covering this, the written answer saying so is filed here in its place — an absent
process is not an absent question, and a data article's ethics statement has to say which of the
two it is.

## Amendments (dated, append-only)

*(none)*
