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
  python scripts/studies/sms_corpus/sms_collect.py --check
  python scripts/studies/sms_corpus/sms_collect.py --ingest <dir of submissions>
"""
from __future__ import annotations
import argparse, csv, glob, json, os, re, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
try:
    from _path import ROOT
except ImportError:                                   # flat public-mirror layout
    ROOT = os.path.dirname(_HERE)

# The documents sit under papers/ in this repository and beside the script in the public
# mirror, which is flat. Resolve both rather than carry two copies of the file: the gate has to
# read the real documents wherever they are, and a mirror whose gate cannot find them would pass.
def _doc(name: str) -> str:
    for c in (os.path.join(ROOT, "papers", "sms_corpus", name), os.path.join(_HERE, name),
              os.path.join(ROOT, name)):
        if os.path.exists(c):
            return c
    return os.path.join(ROOT, "papers", "sms_corpus", name)


PROTOCOL = _doc("PROTOCOL_sms_corpus.md")
CONSENT = _doc("CONSENT_vi.md")
OUT = os.path.join(ROOT, "data", "raw", "sms_corpus")
FIELDS = ["submission_token", "text", "sender", "received_at", "label_student", "label_author"]


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
        holes = c.count("[…]") + len(re.findall(r"\[\.\.\.\]", c))
        if "BẢN NHÁP" in c:
            bad.append("the consent form still carries its draft banner")
        if holes:
            bad.append(f"the consent form has {holes} unfilled placeholder(s): the researcher, "
                       "the ethics contact, the approval number and the publication date")
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
    rows = []
    for f in sorted(glob.glob(os.path.join(a.ingest, "*.csv"))):
        rows += list(csv.DictReader(open(f, newline="", encoding="utf-8")))
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
