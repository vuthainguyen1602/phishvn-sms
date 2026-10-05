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
and counted, not repaired: in the event, 310 of 2,991, most carrying a one-time code the source's
anonymisation missed. The exact copy used — its authors, licence, citation and a SHA-256 that
pins it to the byte — is recorded in `docs/EXTERNAL_QAVN.md`, so the benchmark number the paper
reports can be reproduced against the same data.

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
| `legitimate` | a genuine message from the organisation it appears to come from, about a service the recipient has: a one-time code, a transaction, a bill, a delivery, a public notice |
| `spam` | promotional or unsolicited, with no evidence of intent to obtain credentials, money or information by deception — **including a genuine promotion from a genuine sender**, such as a carrier's data offer to its own subscriber |
| `phishing` | impersonates an organisation or person, or seeks credentials, a one-time code, a payment, a call-back or an app install under a false pretext |

For a binary experiment: `legitimate` + `spam` → 0, `phishing` → 1. Both the three-class labels
and the collapse rule ship with the corpus, so a reader may disagree with the collapse.

**Tie-break between `legitimate` and `spam`:** the label follows the *content*, not the sender. A
genuine brandname advertising to its own customers is `spam`; `legitimate` is reserved for service
and transactional messages. The sender is masked for annotators and withheld from the published
file, so a rule that turned on who sent the message could not be applied by the people applying it.
(Amendment of 2026-10-04: the author's-inbox batch is some 1,260 carrier promotions sent to the
author's own number, which fit both rows of the table as first written.)

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
  (§1) dropped 310 of 2,991 rows for SCHEMA.md rule 2, most carrying an unmasked one-time code in
  a bank message its README declares clean — what "quality-assured by hand" looks like beside a
  rule a script can hold. Neither point is a claim that the corpus is wrong; both are stated with
  its authors credited (`docs/EXTERNAL_QAVN.md`: names, licence, citation, and a SHA-256 pinning
  the exact copy) and its own labels shipped unchanged for anyone to check.
- The 2017 operator corpus (5,557 ham and 1,042 spam from Viettel and Vinaphone) is available on
  request only, and whether its texts keep URLs is undocumented; the paper says that and no more,
  unless its authors answer.

## 10. Ethics approval

**TO SET:** the approving body, the reference number and the date. The application also asks,
explicitly, whether the community batch of the 2026-10-04 amendment may enter the corpus and
under which statement. If the university has no
process covering this, the written answer saying so is filed here in its place — an absent
process is not an absent question, and a data article's ethics statement has to say which of the
two it is.

## Amendments (dated, append-only)

- **2026-10-04 — SCHEMA.md rule 2, the `@` clause.** The rule banned every `@` as a proxy for an
  e-mail address. The first pilot batch from the author's inbox held 26 obfuscated gambling
  messages that use `@` as a letter (`th@nh`, `tay@ae`), which the rule threw out: exactly the
  obfuscating spellings §3 keeps on purpose. The clause now bans an e-mail address (`name@domain.tld`,
  with or without spaces, or `@` before a mail provider) and nothing else, in `redact.html`,
  `sms_transcribe.py` and the tests alike. Consequence for the external benchmark (§1, §7): five
  source rows dropped under the old wording pass under the new one, so the benchmark is 2,681 rows
  (1,910 benign, 771 scam; 310 dropped), not 2,676 (315 dropped). `EXTERNAL_QAVN.md` records both.
- **2026-10-04 — a community batch exists that predates this protocol.** Between **[FILL: start]**
  and 2026-10-04, before approval and before the consent form was in use, the author gathered
  **465 messages** (after exact-duplicate removal) from four channels: a Google Form inviting people
  to submit SMS for research (its text, verbatim, and what it does and does not promise:
  `docs/FORM_community_vi.md` — purpose and anonymity, not permanent publication or withdrawal);
  screenshots and texts people were asked for directly; public Facebook and Threads posts in which
  people showed scam SMS they had received, copied by hand, never crawled; and a few messages from
  the author's own inbox. The batch is held privately (`data/private/provenance.csv` names each
  submission's channel), was redacted and ingested by the same pipeline as everything else, and
  **nothing about any contributor or poster was kept**: no name, handle, post link or image; sender
  numbers were reduced to a country prefix; the screenshots were deleted once transcribed. The batch
  is **not attributable per message** to a person or a channel, so its `participant_id` is the single
  code `C-MIX` and it contributes **nothing to leave-one-contributor-out** (§7). The guideline of §1
  (no messages from personal numbers) was not in force for it, and it is mostly messages from
  personal numbers. Whether it may enter the published corpus, and under which ethics statement,
  is a question the ethics application asks explicitly (§10); until it is answered the batch counts
  for having exercised the pipeline, and the data article describes it as what it is: collected
  before the protocol, from the community, with its provenance recorded but not its consent.
- **2026-10-04 — the author's own inbox, read as a batch.** The author's iPhone forwards its SMS to
  Messages on the author's Mac, and `scripts/sms_imessage.py` read them out of that database:
  **2,894 received SMS**, 2023-01 to 2026-10, almost all from brandnames and shortcodes (1,035 and
  1,857; two from personal numbers, obfuscated gambling spam, reduced to `+84-mobile`). iMessage rows
  and messages the author sent were never selected by the query. The text went through the same
  redaction rules as every other route, and the author read the redacted preview before finalizing;
  that reading found what the rules do not cover and fixed it by hand: the author's name on flight
  and subscriber-registration notices masked as `<NAME>`, booking codes as `<ID>`, and **seven
  messages deleted** rather than masked — one other person's flight booking, five health-care
  messages addressed to the author (appointments and test results), one clinic-app OTP. It also
  tightened two rules for everyone (an own balance stated with words between "số dư" and the figure;
  an own top-up "đã nạp" + amount), with cases in the tests. **Exact repeats were dropped** (1,293 of
  2,894, leaving **1,601**; carriers resend the same promotion many times, and the key is the redacted
  text with whitespace collapsed and case folded, first occurrence kept — `data/private/provenance.csv`
  records both counts). Nobody but the author
  is a data subject here, so this is not collection and nothing was gated; the batch **is attributable**,
  to the author alone, so its `participant_id` is `AUTHOR`, never `C-MIX`, and leave-one-contributor-out
  (§7) must hold it out as one contributor. It was appended to `submissions.csv` and the working file
  on 2026-10-04, as the community batch was (2,072 contributed rows; templates and the split
  recomputed over all of them): whether the author's own inbox enters the *published* corpus — the
  paper's "included / excluded" — is answered in §10 and the ethics statement, not here.
- **2026-10-04 — §4, the `legitimate`/`spam` tie-break.** The table as first written put a genuine
  promotion from a genuine sender in both rows. The author's-inbox batch is mostly such messages
  (MobiFone data offers to the author's own number). Decision: the label follows the content —
  promotional is `spam` whoever sends it; `legitimate` is the service and transactional message.
  The reason is procedural as much as conceptual: annotators never see the sender, so a rule that
  depended on it could not be applied. The on-screen rule of `sms_annotate.py` and the annotators'
  guide (§6, "vài ca khó") say the same.
- **2026-10-04 — a seventh community screenshot batch, and what a collage is worth.** 88 images
  arrived in one evening, 75 distinct (13 were byte-identical copies), and many were collages or
  threads holding two to six messages, so the unit of transcription is the message, not the file:
  every bubble that is complete in the image becomes a row, a bubble cut off at the edge becomes
  nothing. **79 rows** after redaction and text dedupe (63 provisional phishing, 10 legitimate,
  6 spam; 61 templates), none already in `submissions.csv`; a text seen in several images is kept
  once, with the sender and the month taken from whichever image shows them. Six images were not
  transcribed and stay in the folder for the author to rule on: two Shopee in-app chats (not SMS),
  two messages cut off mid-text, one with the brand blacked out by the person who posted it, one
  too small to read. Three kinds of hand masking were needed beyond the rules: a recipient's or a
  courier's name as `<NAME>`, a card holder's own spend and remaining limit as `<AMOUNT>` (the rules
  mask a balance introduced by "số dư", not one introduced by "hạn mức còn lại"), and an
  alphanumeric OTP as `<OTP>` (the rule expects digits). Same token conventions as the earlier
  screenshot batches: participant `C-MIX`, provenance "same as the screenshot batches". The
  working file was rebuilt over all of it: **2,151 contributed rows** (550 community, 1,601 author's
  inbox), 1,940 templates, split 1,505/323/323; the community side now carries 101 provisional
  phishing in 72 templates, against the ≥100-template floor of §2.
- **2026-10-05 — the author's-inbox batch given provisional labels, and what reading it found.**
  The 1,601 `AUTHOR` rows were appended with `label_contributor` empty. On this date they were
  labelled under §4 by the author's assistant (Claude), from the text and the sender, as a draft
  for the author to confirm: **1,293 `spam`, 308 `legitimate`, 0 `phishing`**. The method was a
  rule pass (codes, top-ups, balances, package confirmations, policy notices and public-sector
  senders to `legitimate`; `[TB]`/`[QC]`, "soạn X gửi", offers, packages, loans and insurance to
  `spam`) followed by a reading of every row the rules could not settle or settled on weak
  grounds, which changed 125 of them. Decisions worth knowing: an advance-credit offer ("ứng
  tiền", 1255/1256/5110/9070) is `spam`; a top-up or bonus confirmation with an offer attached is
  `legitimate`, the transaction being the message; a charity appeal from a public body is
  `legitimate` and borderline; a store-opening announcement sent as `(QC)` is `spam` and
  borderline; the two obfuscated gambling texts from personal numbers are `spam` and unreadable.
  The draft with its basis per row and a flag column is kept at
  `data/private/author_inbox_draft_labels_2026-10-05.csv`; the labels went into the working file
  and `submissions.csv`, and the backups of both carry the suffix `2026-10-05a`. Annotators still
  label from the masked text alone (§5), so none of this reaches a final label.
  **Reading found what the rules and the author's own review had missed**, ten rows: a WhatsApp
  code written as two groups of three digits (the OTP rule expected one run of four or more — it
  now takes `ddd-ddd` as well, with the case in `tests/redact_cases.json`); an account-provisioning
  message carrying a password, masked `<PASSWORD>` by hand; the author's name in two job-site
  messages, masked `<NAME>`; and six links whose path identifies the recipient (an invoice, a
  survey, two vouchers, two job confirmations), the path masked `<ID>`, the domain kept.
  **The split was recomputed** (`sms_split.py --assign`, same seed): it now balances against
  2,151 provisional labels rather than 550, so 990 rows moved between train, validation and test;
  the totals stay 1,505/323/323 and the template partition is unchanged.
