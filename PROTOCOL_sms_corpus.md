# collection protocol — a Vietnamese SMS corpus from consenting student inboxes

**STATUS: DRAFT, NOT APPROVED.** Written 2026-09-24, before a single message was collected and
before anyone was asked to take part. It becomes a protocol when the author obtains written
ethics approval, files the consent form below, removes this status line and commits;
`sms_collect.py` refuses everything except `--check` until then, and
`tests/test_sms_corpus.py` checks that it does.

Nothing here can be repaired afterwards. Consent cannot be obtained retroactively, and a corpus
collected without it cannot be published, cited or fixed — only discarded. That is why this file
exists before the first message rather than beside the first draft.

---

## What this corpus is, and what it deliberately is not

**It is:** scam and spam SMS, forwarded voluntarily by students who consent, redacted on their
own device before it reaches the researcher.

**It is not a copy of anyone's inbox.** Only the scam class is collected. The reason is not
squeamishness: an ordinary message in a student's phone was *written by someone else* — a friend,
a family member, a bank clerk — and that person is not present to consent. A student can consent
to give away what is theirs; nobody can consent on behalf of the sender. A scam message has no
such sender: it was broadcast to strangers by someone with no privacy interest in it.

**Where the negative class comes from instead.** Either the SIM honeypot (a line with no personal
traffic, so every message arriving on it was sent to a machine and not to a person), or the ham
half of an already published corpus under its licence, cited as such. Never a personal inbox.

## The consent problem this design is built around

The researcher teaches. A student asked by their lecturer to hand over phone data is not in a
position to refuse freely, and a consent form does not fix that by itself. The design therefore
removes the asymmetry rather than documenting it:

1. **The invitation does not come from anyone who grades them.** A colleague with no assessment
   role over the cohort recruits.
2. **Nothing is attached to participation.** No marks, no credit, no bonus, no attendance, no
   mention in class of who took part.
3. **Submission is anonymous.** The researcher never learns who participated, so declining costs
   nothing and cannot be noticed.
4. **Withdrawal needs no reason** and is possible until the corpus is deposited, after which the
   researcher can no longer identify which messages to remove — and the consent form says so in
   those words rather than promising a deletion that cannot be performed.

## Redaction happens on the student's device

What leaves the phone is already redacted. The researcher never holds the raw text. `sms_redact.py`
runs locally, strips phone numbers, e-mail addresses, account-like digit runs and personal names
the student marks, and shows the result for approval before anything is sent.

A redactor is not a guarantee. The student reviews each message after redaction and before
sending, and the form says plainly that a message they are unsure about should not be sent.

## What is recorded per message

Message text (redacted), the sender string as shown, the date, the student's own label, and a
participant token that is random per submission and never linked to a person. **No handset
identifier, no phone number, no name, no course, no cohort.**

## Labelling

The student labels each message they send as scam or not; a message they are unsure about is
not sent rather than sent unlabelled. The author reviews every label and adjudicates, and the
protocol registers an agreement measure between the two before any count is published. A
disagreement rate is a result about label quality, not a thing to silently resolve.

## What the paper may claim

The corpus is one cohort at one university over one window, gathered from volunteers. It is not
a sample of Vietnamese smishing and the data article says so in the abstract, not only in the
limitations. **TO SET before approval:** cohort size, the collection window, and the target
number of messages.

## Ethics approval

**TO SET:** the approving body, the reference number and the date. If the university has no
process covering this, the written answer saying so is filed here in its place — an absent
process is not an absent question, and a data article's ethics statement has to say which of the
two it is.

## Amendments (dated, append-only)

*(none)*
