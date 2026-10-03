# PhishVN-SMS: a template-disjoint, three-class Vietnamese SMS corpus with consent-first collection and an external benchmark

*Data article — full draft, structured after the* Data in Brief *template. It expands
`DATA_ARTICLE_outline.md`. Every design fact is written out; every number that depends on
annotation, collection or ethics approval is a bracketed placeholder `[FILL: …]` and is not
invented. The abstract is drafted with the same placeholders and is rewritten last, once the
counts exist. Source documents: `PROTOCOL_sms_corpus.md` (§ numbers below refer to it),
`SCHEMA.md`, `SCHEMA_raw.md`, `EXTERNAL_QAVN.md`, `CONSENT_vi.md`, `scripts/README.md`.*

---

**Authors.** [FILL: author list and affiliations.]

**Corresponding author.** [FILL: name, e-mail.]

**Keywords.** Smishing; SMS phishing; spam detection; Vietnamese; text corpus; data annotation;
template leakage; consent; privacy-preserving data collection.

---

## Abstract

PhishVN-SMS is a pilot corpus of Vietnamese SMS messages labelled in three classes
(`legitimate`, `spam`, `phishing`), contributed by consenting volunteers from their own handsets.
Only machine-sent messages were collected: scam and spam broadcasts, and legitimate traffic from
brandnames and service shortcodes; no person-to-person message was taken. Personal data was
redacted on the contributor's device before any text reached the researchers, while links and
broadcast amounts were kept as signal. Two annotators labelled every message independently and
disagreements were adjudicated; both original labels ship unmodified with the agreement
reported. Messages are grouped into templates by a stated, reproducible computation, and a fixed
70/15/15 split is template-disjoint. A published Vietnamese SMS corpus is shipped alongside,
unchanged in label, as a held-out external benchmark. The corpus holds [FILL: N] messages in
[FILL: T] templates; the benchmark holds 2,676. It is a pilot from one small group, not a sample
of Vietnamese smishing. Released under [FILL: corpus licence].

*[FILL: trim to ≤ 150 words once counts are in.]*

## Specifications Table

| | |
|---|---|
| **Subject** | Computer Science — Security and Privacy; Natural Language Processing |
| **Specific subject area** | SMS spam and scam (smishing) detection in Vietnamese; corpus construction, annotation agreement, and leakage-free evaluation splits |
| **Type of data** | Table (CSV, UTF-8). Redacted message text with derived flags, three-class labels, template groups and a fixed split. A second table: an external benchmark with its source's labels. |
| **Data collection** | **Contributed corpus:** volunteers paste messages into an offline redaction page on their own phone and submit the redacted text, or send cropped, blacked-out screenshots that are OCR-transcribed, hand-checked, redacted and then deleted. Only machine-sent messages (brandname or shortcode senders). Two independent human annotators per message, adjudication of disagreements. Templates by word 4-shingle Jaccard clustering on a normalized view; split assigned per template. **External benchmark:** the *Quality-Assured Vietnamese SMS Phishing Dataset* (CC BY 4.0), placeholder tokens remapped, rows failing the redaction rule dropped and counted, labels kept as published, held out entirely. |
| **Data source location** | Vietnam. Contributors' own handsets; institution: [FILL]. External benchmark: `https://huggingface.co/datasets/trannguyenthaituan/vietnamese_sms_dataset`, file `full_dataset.csv`, SHA-256 `8a29d50a6335c8938b8beef0a3daf57d276e880244394da453bc656f5a4c7847`. |
| **Data accessibility** | Repository name: [FILL: Zenodo / Mendeley Data]. Data identification number: [FILL: DOI]. Direct URL to data: [FILL]. Protocol, consent form, schema and all processing code: `https://github.com/vuthainguyen1602/phishvn-sms` (code MIT; corpus [FILL: licence]). |
| **Related research article** | [FILL: none / citation of the analysis paper, if any.] |

## Value of the Data

- **Vietnamese smishing data with links intact.** Public Vietnamese SMS corpora are few. This
  one keeps URLs, including live phishing domains, as a first-class signal, and masks personal
  data instead of stripping everything that looks like a token. The domain and path are the
  strongest evidence a smishing message carries; a corpus that removes them has removed the thing
  it exists to measure.
- **Three classes with a published collapse rule.** `legitimate`, `spam` and `phishing` are
  labelled separately. A reader who wants a binary task collapses them in one line
  (`legitimate` + `spam` → 0, `phishing` → 1); a reader who disagrees with that collapse can
  choose another. A binary corpus cannot be made finer afterwards.
- **A split no template crosses.** Scam SMS is sent by template, and after redaction fifty
  one-time-code messages become one string. Messages are grouped by a stated computation and the
  70/15/15 split is assigned per template, so a model tested here is asked to detect, not to
  remember. The published corpus this project audits puts 7.9% of its test texts in its training
  set; this one, by construction, puts none.
- **An independent external benchmark, shipped alongside.** A published Vietnamese corpus is
  held out entirely, with its own labels unchanged, for cross-dataset generalization testing. The
  exact copy is pinned by content hash, and the measured divergence between the two label schemes
  is reported rather than corrected.
- **Labels that can be audited.** Both annotators' labels ship unmodified, including every
  disagreement and every `uncertain`, with Cohen's κ, per-class-pair disagreement and the share
  adjudicated. The agreement can be recomputed, not believed.
- **A consent and privacy design that is checkable.** The protocol and the consent form were
  committed, publicly and timestamped, before the first message was collected. Redaction ran on
  the contributor's device, so raw text never reached the researchers on the primary route. The
  design is reusable by anyone collecting message data from a population they teach or supervise.

## Data Description

The dataset consists of two CSV files (UTF-8, comma-separated, header row, one message per row),
a schema document and the code that produced them.

### `sms_dataset.csv` — the contributed corpus

| field | type | values | meaning |
|---|---|---|---|
| `message_id` | string | `SMS_00001` | stable identifier, assigned in ingest order and never reused |
| `text` | string | free text | the message **after redaction**; byte-for-byte as received where `capture` is `paste`, a hand-checked OCR transcription where it is `screenshot` |
| `source` | enum | `contributed` | which corpus a row belongs to; every row of this file is `contributed` |
| `capture` | enum | `paste`, `screenshot` | how the text was obtained |
| `final_label` | enum | `legitimate`, `spam`, `phishing` | the adjudicated label; the only label an experiment should train on |
| `label_annotator_1` | enum | the three labels + `uncertain` | first annotator, independent, unmodified |
| `label_annotator_2` | enum | the three labels + `uncertain` | second annotator, independent, unmodified |
| `template_id` | string | `T0031` | computed template group; every message of one template shares it |
| `sender_type` | enum | `brandname`, `shortcode`, `unknown` | how the sender appeared on the handset |
| `has_url` | 0/1 | | the text contains a link; the link itself is kept in `text` |
| `has_phone` | 0/1 | | the text contains `<PHONE>` |
| `has_otp` | 0/1 | | the text contains `<OTP>` |
| `has_money` | 0/1 | | the text contains an amount, kept or masked as `<AMOUNT>` |
| `split` | enum | `train`, `validation`, `test` | the shipped template-disjoint split |

Redaction placeholders that may appear in `text`:

```
<NAME> <PHONE> <ACCOUNT> <OTP> <EMAIL> <AMOUNT> <ADDRESS> <ID> <DATE> <TIME> <TRANSACTION_ID>
```

Everything else in `text` is as received. Odd punctuation, capitalisation, missing diacritics,
typos, unusual Unicode and filter-evading spellings are kept exactly, because they are among the
strongest signals a smishing message carries. Rows with `capture = screenshot` are OCR
transcriptions and may have normalised such spellings; a study of them should use `paste` rows
only.

A valid file satisfies six rules, each checked by the publishing script rather than assumed:
`message_id` is unique; `text` contains no digit run of four or more outside a placeholder, a
link or an amount, and no `@`; `final_label` is never `uncertain` or empty; every message
sharing a `template_id` shares a `split`; the four `has_*` flags are derived from the published
patterns, never typed; `sender_type` is never a phone number.

**Size and balance.** [FILL: N] messages from [FILL: n] contributors, grouped into [FILL: T]
templates at the primary threshold (τ = 0.8); [FILL: T₀.₇] and [FILL: T₀.₉] templates at
τ = 0.7 and τ = 0.9. Class balance: [FILL: legitimate / spam / phishing counts and
percentages]. [FILL: M] distinct malicious (`spam` + `phishing`) templates, against the
protocol's floor of 100. Capture route: [FILL: paste / screenshot counts]. Sender type:
[FILL: brandname / shortcode / unknown counts].

**Split.** A fixed template-disjoint 70/15/15 split, assigned per template by a seeded greedy
search over 200 restarts (seed 1602), scored on size and label mix. Per-split counts:

| split | messages | templates | legitimate | spam | phishing |
|---|---|---|---|---|---|
| train | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |
| validation | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |
| test | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |

The test slice of a pilot this size holds too few phishing messages to carry a conclusion on its
own; it ships for presentation, and the primary evaluation is cross-validation over template
groups (see *Methods*, Splits).

**Annotation agreement.** Cohen's κ between the two annotators before adjudication:
[FILL]. Disagreement rate per class pair: legitimate–spam [FILL], legitimate–phishing [FILL],
spam–phishing [FILL]. Rows marked `uncertain` by at least one annotator: [FILL]. Share of rows
adjudicated: [FILL].

### `sms_external_qavn.csv` — the external benchmark

The rows of the *Quality-Assured Vietnamese SMS Phishing Dataset* [1] (CC BY 4.0), mapped into
this corpus's placeholder vocabulary and held out as an independent test set. It is **not** part
of `sms_dataset.csv`, is **not** annotated by this project, and carries the source's own binary
label.

| field | type | values | meaning |
|---|---|---|---|
| `message_id` | string | `QAV_COM_0000` | traces to the source row |
| `text` | string | free text | the source text with placeholder tokens remapped (`[MONEY]` → `<AMOUNT>`, and so on); `[TB]`, `[QC]` and brand prefixes are message text and left alone |
| `label_source` | enum | `benign`, `scam` | the source's label (0 / 1), unchanged; the evaluation label |
| `template_id` | string | | computed by the same method as the contributed corpus |
| `sender_type` | enum | | as above |
| `has_url`, `has_phone`, `has_otp`, `has_money` | 0/1 | | derived as above |

It has no `final_label`, no annotator columns and no train split: none were produced for it.
`<NUMBER>` appears only in this file, as the mechanical image of the source's `[NUMBER]` and
`[POINT]` tokens, which collapsed phones, shortcodes and quantities into one; `has_phone` stays 0
on such a row.

**Size.** 2,676 messages (1,907 `benign`, 769 `scam`), after 315 of the source's 2,991 rows were
dropped by the redaction rule (most carried an unmasked one-time code). Templates: [FILL: count
at τ = 0.8]. No external template coincides with any training template of the contributed corpus
(checked by the grouping script).

### Supporting files

`SCHEMA.md` and `SCHEMA_raw.md` (fields, validity rules, what is withheld and why);
`EXTERNAL_QAVN.md` (benchmark provenance and version pin); `PROTOCOL_sms_corpus.md`;
`CONSENT_vi.md` with its English translation `CONSENT_en.md`; `CONTRIBUTE_vi.md` /
`CONTRIBUTE_en.md` (contributor instructions); the processing scripts in `scripts/`; the test
suite in `tests/`.

**What is withheld.** `participant_id` is kept privately and does not ship: with a handful of
contributors it is pseudonymisation, not anonymisation, since someone who knows the group could
read off which bank or school each uses. It exists so the leave-one-contributor-out result can be
computed, and that result is reported without the mapping. Raw text and screenshots never ship;
screenshots were deleted once their transcription was checked, before publication. No handset or
SIM identifier, date of birth or contact name was collected.

## Experimental Design, Materials and Methods

### Scope and design

PhishVN-SMS is a **pilot**: [FILL: 30] contributors at around [FILL: 100] messages each, about
three thousand messages, enough to study labelling, templates and splitting, and not enough to
describe Vietnamese smishing. The target mix (roughly 800 phishing, 450 spam, 1,800 legitimate)
is a designed 1:2 malicious-to-legitimate ratio, not the prevalence of any inbox; all reported
metrics are per class, and nothing depends on this base rate. Messages are what is collected,
but templates are what the evaluation counts: the figure that decides what the corpus can say is
the number of distinct malicious templates (floor: 100), because another copy of a template
already held adds nothing a template-disjoint split can use. Collection watched the template
count as it went and stopped adding a contributor's near-duplicates before stopping their novel
messages.

Two kinds of message were collected, and only two. **Scam and spam** of any sender, broadcast to
strangers by someone with no privacy interest in them; and **legitimate messages sent by a
machine** (one-time codes, bank and telecommunications notifications, school and application
notices) from a brandname or a service shortcode. **Person-to-person messages were never
collected.** A message a friend or relative sent is theirs, and they are not present to consent;
a contributor can give away what is their own and nobody can consent on a sender's behalf. The
rule contributors were given is mechanical: a message from a personal phone number is not sent,
whatever it says, even when it is plainly a scam.

### Consent design

Contributors may be students, and the lead researcher teaches. A student asked by a lecturer for
phone data is not free to refuse, and a consent form does not fix that by itself. The design
removes the asymmetry instead of documenting it:

1. The invitation came from a colleague with no assessment role over the cohort.
2. Nothing was attached to participation: no marks, credit, bonus or attendance, and no mention in
   class of who took part.
3. Submission was anonymous. The researchers never learn who participated, so declining costs
   nothing and cannot be noticed.
4. Withdrawal needed no reason and was possible until deposit. After deposit the researchers
   cannot identify which messages to remove, and the consent form says so in those words instead
   of promising a deletion that cannot be performed.

The consent form (`CONSENT_vi.md`, in Vietnamese; the English translation is for reviewers and
the Vietnamese governs) states in plain language what is asked for and what is not, that
publication is permanent, that the screenshot route exposes the image to the researcher, and the
principal risk (a personal detail the filter missed and the contributor did not notice on
review). It asks for no signature, since a signature would turn an anonymous submission into an
identified one.

### Collection and redaction

**Primary route: paste.** The contributor opens a single offline HTML page (`redact.html`) in the
phone's own browser. The page makes no network request and works in airplane mode. Each message
is copied from the messaging app and pasted in, so the text arrives character for character with
no screenshot or OCR involved. The page replaces personal data with the placeholders listed under
*Data Description*; the contributor reviews every message after redaction and before sending, and
drops any they are unsure about. The raw text never leaves the phone.

**What is kept, and what is masked.** Links are kept. A link was broadcast to strangers and is
not personal data; only personal data *inside* a link is masked: a phone number, an e-mail
address, or a name or account in a query string (`?sdt=`, `?ten=`, `?stk=`…). A path segment that
identifies the recipient without saying so cannot be recognised by rule, so contributors were
asked to check each link and drop a message whose link carries their own details. Broadcast
amounts are kept: a prize, a fee or a price in a scam or an advert is a signal. The contributor's
own money is masked: a balance, a signed account movement (`+1.500.000VND`) and an amount beside a
transaction marker are sensitive personal data and become `<AMOUNT>`. Normalisation stops there;
spelling, punctuation and Unicode are untouched.

**Alternative route: screenshots.** A message that cannot be copied may be sent as a screenshot,
cropped to the sender and the message, with the contributor's own details blacked out on the
image, in one `.zip` file. On this route the researcher does see an unredacted image, and the
consent form says so. On receipt, images are re-encoded from pixels alone so that no file name or
metadata survives, transcribed by OCR, checked by hand against each image, redacted by the same
rules as the paste route (the transcription script reads the rules out of `redact.html`, so the
two routes cannot drift), and deleted once checked. `capture = screenshot` marks every such row.

**Ingest.** Each submission row is validated (reviewed flag, sender type, month format, capture
route) before being appended to the submissions file. The collector refuses to run until the
protocol carries no draft status and the consent form has no unfilled blank; a test asserts that
it does.

### Label scheme

Three classes, defined for annotators as follows.

| label | definition |
|---|---|
| `legitimate` | a genuine message from the organisation it appears to come from |
| `spam` | unsolicited or promotional, with no evidence of intent to obtain credentials, money or information by deception |
| `phishing` | impersonates an organisation or person, or seeks credentials, a one-time code, a payment, a call-back or an app install under a false pretext |

**A message is not made `phishing` because it looks suspicious.** Evidence of deceptive intent is
required; where it is absent the message is `spam`. `uncertain` is a fourth value an annotator
may use and the published `final_label` never carries: it sends a message to adjudication. For a
binary experiment the published collapse rule is `legitimate` + `spam` → 0, `phishing` → 1.

### Annotation

Two human annotators labelled every contributed message independently. The labelling tool shows
an annotator the text and nothing else: not the other annotator's label, not the contributor's
own label, not the sender or any metadata. Every disagreement and every `uncertain` went to an
adjudicator, whose decision is `final_label` and is recorded with a name and a one-line note.
Agreements were finalised without an adjudicator.

Three things are reported whatever they show: Cohen's κ between the two annotators before
adjudication ([FILL]), the disagreement rate per class pair ([FILL]), and the share adjudicated
([FILL]). A low κ is a result about how separable these classes are in practice; it is published
as one and not repaired by relabelling until the annotators agree. Both original labels ship
unmodified so the agreement can be recomputed.

[FILL: annotator background and training; whether the adjudicator was one of the annotators or a
third person; whether a pre-annotation hint column (`label_ai`) was shown to annotators. Per the
annotation tool's design it is not shown and is excluded from κ; state this.]

### Templates

Grouping is computed, not assigned by hand. It runs on a **normalized view** of the text that
exists only for this step: lower-cased, whitespace collapsed, placeholders kept, and every URL and
money amount replaced by a `<URL>` or `<AMT>` token. The published text keeps both, but for
grouping they are the slots a campaign rotates, and leaving them in place splits one template into
many. The amount patterns for this step extend the redaction rules with short forms (one to three
digits plus *k*, *tr*, *tỷ*) that redaction rightly ignores, since two digits identify nobody, but
grouping must not.

Each normalized message becomes the set of its word 4-shingles. Pairs at or above Jaccard
similarity **τ = 0.8** are linked, and a template is a connected component of that graph.
Results at τ = 0.7 and τ = 0.9 are reported beside the primary so that chaining is visible.
The shingling, thresholds and connected components are the method the sibling kit-reuse study
registers [FILL: ref]; the normalization is this protocol's one departure from it, adopted after
a pilot batch showed the failure it repairs: a scam sent twice with one edited character in the
domain, or a different lure amount, fell below τ even at 0.7, because in a message of eight words
one changed word destroys four shingles. Counted as different templates, the two copies then land
on opposite sides of a template-disjoint split, which is the leakage the split exists to prevent.

### Splits

**Every message of one template lies in one split.** The published corpus this project audits
does not do this: 47 of its 597 test rows (7.9%) repeat a training text. A fixed 70/15/15
template-disjoint split ships with the corpus. It is assigned per template, never per message, by
a greedy search over 200 seeded restarts (seed 1602), scored on split size and label mix; the seed
and restart count are constants in the script, so the split reproduces from the working file
alone, and a unit test asserts that no template crosses a split.

Three evaluations are specified for the paper that uses the corpus, in decreasing order of what
they can support:

1. **Cross-validation over template groups** is the primary evaluation. The fixed split is for
   presentation; with a pilot this size its test slice holds too few phishing messages to carry a
   conclusion, and the paper says so where it reports it.
2. **Leave-one-contributor-out**: train on all contributors but one, test on the one. With
   [FILL: n] contributors that is as many folds, each a single person, so the folds are reported
   individually and never averaged. It answers "does this transfer to an inbox it has not seen"
   qualitatively and estimates nothing. It is computed from the private `participant_id` and
   reported without the mapping.
3. **The external benchmark**, below.

### The external benchmark

The *Quality-Assured Vietnamese SMS Phishing Dataset* [1] (CC BY 4.0; 2,991 messages; binary
labels, 2,193 `benign` and 798 `scam`) is held out entirely: every row is `split = external`,
never train, validation or test. The copy used is pinned by the SHA-256 of its `full_dataset.csv`
(see *Specifications Table*); a copy reproduces this benchmark only if its hash matches. No
repository revision was recorded at download (2026-08), so the content hash is the anchor.

Its placeholder tokens were mapped to this corpus's by an allowlist in the import script. Rows
that still failed the redaction rule after mapping were dropped and counted, never repaired: 315
of 2,991, most carrying an unmasked one-time code in a bank message. The loaded benchmark is
therefore 2,676 rows (1,907 `benign`, 769 `scam`). Its labels are its own; this project does not
re-annotate them and does not treat its three-class scheme as a correction of the source's
two-class one.

A model trained on `sms_dataset.csv` is scored on the benchmark after collapsing its prediction
to the source's two classes (`legitimate` → `benign`; `spam`, `phishing` → `scam`), against the
source's own labels. The paper also reports, once, **how far the two label schemes diverge**. The
source's boundary separates *genuine sender* from *scam*, so its `benign` class carries the
operators' own promotional messages, which this corpus's scheme calls `spam` whoever sent them.
In a model-assisted pass confirmed by a hand audit of a sample, [FILL: ≈ 50%] of the source's
`benign` rows read as `spam` under the three-class scheme, while [FILL: ≈ 0%] of its `scam` rows
read as `legitimate`. That divergence is the reason the two corpora are kept in separate files
rather than merged: a single pooled label column would bury it. A template-grouping check
confirms that no external template coincides with a training template, so the benchmark is
genuinely unseen.

### Publishing

The two published files are a mechanical projection of the private working file: the publishing
script keeps exactly the schema's columns, derives the four `has_*` flags from the patterns in
`redact.html`, and refuses to ship a train/validation/test row with an `uncertain` or empty
`final_label`, a missing `template_id` or a missing `split`. Every stage reads files and writes
files, so the whole pipeline can be rerun and checked; a test suite holds the redaction routes to
one list of cases and the later stages to their invariants (rotated slots group as one template,
no template crosses a split, agreements finalise without an adjudicator, the projection ships
exactly the schema's columns).

### Software

Python 3 standard library only for the pipeline; [FILL: OCR engine and version for the screenshot
route]. All scripts, the redaction page and the tests are in the repository at the tagged release
[FILL: tag / commit].

## Limitations

- **A pilot, not a sample.** One small volunteer group, one collection window, one institution.
  The corpus is not a representative sample of Vietnamese smishing, and its designed class ratio
  is not any inbox's prevalence. Per-class metrics are meaningful; anything that depends on the
  base rate is not.
- **Small test slice.** The fixed split's test half holds [FILL] phishing messages. It ships for
  presentation; conclusions should rest on cross-validation over template groups.
- **Sender-type filter excludes a real part of the problem.** Many scam messages in Vietnam come
  from personal numbers. They were not collected, for consent reasons, so the corpus
  under-represents that channel by design.
- **Screenshot rows are OCR transcriptions.** Obfuscating spellings and unusual Unicode may not
  survive OCR even after a hand check; a character-level study should filter on
  `capture = paste`.
- **The external benchmark inherits its source's biases**: its collection sources and period, and
  its heavy operator traffic. It tests generalization to a differently-collected corpus; it does
  not remove bias. Its 315 dropped rows are not a random subset (most are bank messages with a
  one-time code), so the loaded benchmark is slightly skewed against that message type.
- **Scheme divergence is measured, not resolved.** About [FILL] of the benchmark's `benign` rows
  are `spam` under this corpus's scheme; a model trained here will be penalised on them by the
  source's labels. The reported benchmark score is therefore a lower bound on agreement with the
  three-class scheme, and should be read beside the divergence figure.
- **Annotation.** [FILL: two annotators and one adjudicator from the research group; κ as
  reported; any class pair with notably low agreement.]
- **Links may die.** Phishing domains are short-lived; `has_url` and the URL text remain, but the
  destinations will not resolve for long.

## Ethics Statement

[FILL: Ethics approval was granted by (approving body), reference (number), on (date). / The
institution's written answer that no review process covers this study is filed in the repository
in place of an approval, per protocol §10.]

Informed consent was obtained from every contributor before collection. The collection protocol
and the consent form were published and timestamped in the public repository before the first
message was collected, so the order of events can be verified independently of the authors.
Participation was anonymous, voluntary, unconnected to any assessment, and recruited by a person
with no assessment role over the contributors; withdrawal needed no reason and was possible until
deposit.

No personal data was collected. On the primary route, redaction ran on the contributor's device
and raw text never reached the researchers. On the screenshot route, images were stripped of
metadata on receipt, transcribed, checked, redacted and deleted before publication. The contributor
identifier is withheld from the published files. The pilot batch from the lead author's own inbox,
used to exercise the pipeline, is [FILL: included / excluded] from the corpus, as stated in the
ethics application.

The external benchmark is a published dataset reused under its CC BY 4.0 licence with attribution;
its labels are shipped unchanged and no additional data about any person was derived from it.

## Data Availability

The dataset (`sms_dataset.csv`, `sms_external_qavn.csv`, `SCHEMA.md`, `EXTERNAL_QAVN.md`) is
deposited at [FILL: repository, DOI] under [FILL: licence]. The protocol, consent form,
contributor instructions, redaction page, processing scripts and tests are at
`https://github.com/vuthainguyen1602/phishvn-sms` (code: MIT), release [FILL: tag].

## CRediT authorship contribution statement

[FILL per author.] **Thai Nguyen Vu:** Conceptualization, Methodology, Software, Data curation,
Writing – original draft. [FILL: annotators: Data curation (annotation), Validation.]
[FILL: recruiter / supervisor: Investigation, Supervision, Writing – review & editing.]

## Acknowledgments

We thank the contributors, who cannot be named because they are anonymous to us, and
[FILL: the colleague who recruited] for recruiting without any assessment role. We thank the
authors of the *Quality-Assured Vietnamese SMS Phishing Dataset* for releasing it under CC BY 4.0,
which made the external benchmark possible. An AI coding assistant (Claude, Anthropic) was used
to help develop and test the processing scripts and to edit this manuscript; all data labels were
assigned by human annotators, and the authors take full responsibility for the content.
[FILL: funding, or "This research did not receive any specific grant from funding agencies in the
public, commercial, or not-for-profit sectors."]

## Declaration of Competing Interest

The authors declare that they have no known competing financial interests or personal
relationships that could have appeared to influence the work reported in this paper.
[FILL: amend if applicable.]

## References

[1] N. T. T. Tran, H. K. Le, M. T. Nguyen, V. T. Nguyen, H. D. Mai, Vietnamese SMS Dataset with
Quality Assurance, *IEEE Access* (2026). Dataset: *Vietnamese Quality-Assured SMS Scam Dataset
(Official Release)*, `https://huggingface.co/datasets/trannguyenthaituan/vietnamese_sms_dataset`,
CC BY 4.0. [FILL: volume, pages, DOI once available.]

[2] [FILL: the 2017 Vietnamese operator SMS corpus (5,557 ham, 1,042 spam; Viettel and
Vinaphone) — full citation. Available on request only; whether its texts keep URLs is
undocumented, and the paper says that and no more unless its authors answer.]

[3] [FILL: the sibling PhishVN kit-reuse study whose shingling / Jaccard / connected-components
grouping method §6 reuses.]

[4] J. Cohen, A coefficient of agreement for nominal scales, *Educational and Psychological
Measurement* 20 (1960) 37–46.

[5] [FILL: related smishing / SMS spam dataset work cited for context, e.g. the UCI SMS Spam
Collection and any Vietnamese-language SMS corpora besides [1] and [2].]
