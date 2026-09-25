#!/usr/bin/env python3
"""
sms_collect.py — ingest redacted scam SMS submitted by consenting students.

WHAT IT REFUSES, AND WHY THAT IS THE POINT. Consent cannot be obtained afterwards. A corpus
gathered before approval cannot be repaired, published or cited -- only discarded -- so the
expensive failure is not "the script stopped", it is "the script ran". Until the protocol is
approved this does nothing but --check.

Three conditions, all read from the files rather than from a flag:
  1. PROTOCOL_sms_corpus.md no longer carries its DRAFT status line;
  2. CONSENT_vi.md has no unfilled [...] placeholder left;
  3. the protocol records an ethics approval reference, or a written answer that the institution
     has no process covering this -- an absent process is not an absent question.

RUN:
  python3 scripts/sms_collect.py --check
  python3 scripts/sms_collect.py --ingest <dir of submissions>
"""
from __future__ import annotations
import argparse, csv, glob, json, os, re, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
try:
    from _path import ROOT
except ImportError:
    # Public-mirror layout: this script lives in scripts/, so the repository root -- where data/
    # and docs/ sit -- is its parent. OUT and _doc() resolve against it, so the private files land
    # inside the repository, under its .gitignore and SCHEMA_raw.md's account of them.
    ROOT = os.path.dirname(_HERE)

# The documents sit under papers/ in the monorepo and under docs/ in the public mirror. Resolve
# both rather than carry two copies of the file: the gate has to read the real documents wherever
# they are, and a mirror whose gate cannot find them would refuse rather than pass.
def _doc(name: str) -> str:
    for c in (os.path.join(ROOT, "papers", "sms_corpus", name), os.path.join(ROOT, "docs", name),
              os.path.join(ROOT, name)):
        if os.path.exists(c):
            return c
    return os.path.join(ROOT, "docs", name)


PROTOCOL = _doc("PROTOCOL_sms_corpus.md")
CONSENT = _doc("CONSENT_vi.md")          # the operative document; contributors read this one
CONSENT_EN = _doc("CONSENT_en.md")       # a translation, for reviewers who do not read Vietnamese
OUT = os.path.join(ROOT, "data", "raw", "sms_corpus")
# The submission schema of SCHEMA_raw.md §1 -- what leaves a contributor's device, and no more.
# It carried label_author before the design was written, which put the author's own label in the
# file contributors produce; the author labels at the annotation stage, in the working file.
MONTH = re.compile(r"\d{4}-(0[1-9]|1[0-2])")
FIELDS = ["submission_token", "text", "capture", "sender", "sender_type", "received_month",
          "label_contributor", "redaction_reviewed"]


def _blanks(text: str) -> int:
    """Unfilled [...] placeholders left in a consent form. The draft banner is a blockquote whose
    own `[…]` names the placeholders rather than being one to fill, so blockquote lines are excluded:
    counting it would keep the gate one short forever, even once every real blank was filled."""
    body = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">"))
    return body.count("[…]") + len(re.findall(r"\[\.\.\.\]", body))


def gates() -> list:
    """Every unmet condition, in the order a reader should fix them. Empty means collection may
    begin. Read from the documents: a flag would let somebody skip the part that matters."""
    bad = []
    if not os.path.exists(PROTOCOL):
        return [f"{os.path.relpath(PROTOCOL, ROOT)} does not exist"]
    p = open(PROTOCOL, encoding="utf-8").read()
    if re.search(r"STATUS:\s*DRAFT|NOT APPROVED", p, re.I):
        bad.append("the protocol still carries its DRAFT status line")
    if "TO SET" in p:
        bad.append(f"the protocol has {p.count('TO SET')} unfilled 'TO SET' field(s) "
                   "(cohort, window, target, and the ethics reference)")
    if not os.path.exists(CONSENT):
        bad.append(f"{os.path.relpath(CONSENT, ROOT)} does not exist")
    else:
        c = open(CONSENT, encoding="utf-8").read()
        holes = _blanks(c)
        if "BẢN NHÁP" in c:
            bad.append("the consent form still carries its draft banner")
        if holes:
            bad.append(f"the consent form has {holes} unfilled placeholder(s): the researcher, "
                       "the ethics contact, the approval number and the publication date")
    # The English text is a translation, and a translation drifts silently: the operative form
    # gets filled in and the copy a reviewer reads keeps the blanks, or vice versa. Nobody would
    # notice, because the two are read by different people. Hold them to the same count.
    if not os.path.exists(CONSENT_EN):
        bad.append(f"{os.path.relpath(CONSENT_EN, ROOT)} does not exist: an ethics committee or a "
                   "reviewer who does not read Vietnamese cannot check what contributors were told")
    elif os.path.exists(CONSENT):
        e = open(CONSENT_EN, encoding="utf-8").read()
        v = open(CONSENT, encoding="utf-8").read()
        if "NOT IN USE" in e.upper() and "BẢN NHÁP" not in v:
            bad.append("the English translation still says DRAFT while the Vietnamese form does not")
        he, hv = _blanks(e), _blanks(v)
        if he != hv:
            bad.append(f"the two consent forms disagree: {hv} placeholder(s) left in the "
                       f"Vietnamese, {he} in the English translation")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="say what is still missing; collect nothing")
    ap.add_argument("--ingest", default="", help="directory of redacted submissions")
    a = ap.parse_args()

    bad = gates()
    if a.check:
        print(json.dumps({"ready_to_collect": not bad, "missing": bad}, indent=2, ensure_ascii=False))
        return 0
    if bad:
        raise SystemExit("[!] collection is not permitted yet:\n" +
                         "".join(f"    - {b}\n" for b in bad) +
                         "    Nothing was read and nothing was written. Consent cannot be\n"
                         "    obtained afterwards, so this refusal is the cheap failure.")
    if not a.ingest:
        raise SystemExit("[!] pass --ingest <dir>")

    os.makedirs(OUT, exist_ok=True)
    rows, unreviewed, personal, badmonth, nocapture = [], 0, 0, 0, 0
    for f in sorted(glob.glob(os.path.join(a.ingest, "*.csv"))):
        for r in csv.DictReader(open(f, newline="", encoding="utf-8")):
            # SCHEMA_raw.md §1: the contributor confirms they read the redacted text before
            # sending. A row that says otherwise was not reviewed by the one person who could
            # see what the redactor missed, and no later step can substitute for that.
            if str(r.get("redaction_reviewed", "")).strip() not in ("1", "true", "True"):
                unreviewed += 1
                continue
            # A personal number is not collected, whatever the message says: the sender did not
            # consent and cannot be asked. The rule is in the consent form in this form too.
            if str(r.get("sender_type", "")).strip() not in ("brandname", "shortcode", "unknown"):
                personal += 1
                continue
            # SCHEMA_raw.md §1: the month only. A full date is not trimmed here, because trimming
            # would mean the author had already seen it; the row is refused instead.
            # Empty is allowed for a screenshot that shows no date.
            m = str(r.get("received_month", "")).strip()
            if m and not MONTH.fullmatch(m):
                badmonth += 1
                continue
            # Every row says how its text was obtained; SCHEMA.md tells readers to trust only
            # `paste` rows character by character, which is meaningless if the field can be blank.
            if str(r.get("capture", "")).strip() not in ("paste", "screenshot"):
                nocapture += 1
                continue
            rows.append(r)
    if unreviewed or personal or badmonth or nocapture:
        print(f"[i] skipped {unreviewed} unreviewed, {personal} non-brandname, {badmonth} "
              f"not-a-month and {nocapture} no-capture row(s)")
    out = os.path.join(OUT, "submissions.csv")
    new = not os.path.exists(out)
    with open(out, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[+] {len(rows)} submission(s) -> {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
