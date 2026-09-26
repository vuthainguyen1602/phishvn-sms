#!/usr/bin/env python3
"""
sms_import.py — the imported subset: rows of a published corpus, brought in for re-annotation.

The corpus imported is the *Quality-Assured Vietnamese SMS Phishing Dataset* (CC BY 4.0),
credited in the paper. Its rows are already public, so nothing here is collection and no gate
applies; what applies instead is §5 of the protocol — every imported row is re-labelled by the
same two annotators, blind, and the paper reports how often they disagree with the source's
binary label. To keep that comparison honest:

- the source's label goes to `label_source` (`benign`/`scam`) and nowhere an annotator sees;
- `source` = `qavn`, `capture` = `imported`, `participant_id` stays empty, so the
  leave-one-contributor-out folds never see these rows;
- the source's PII tokens are mapped to this corpus's placeholders by the table below, and only
  those: `[TB]`, `[QC]` and brand prefixes are message text, not placeholders. `[NUMBER]` and
  `[POINT]` become `<NUMBER>`, a token only imported rows carry, because the source collapsed
  phones, shortcodes and quantities into one token and inventing the distinction back would be
  labelling by wishful thinking;
- `message_id` is `QAV_` plus the source's own id, so any row can be checked against the
  original;
- a row that fails SCHEMA.md rule 2 after mapping is skipped and named, never repaired by hand:
  repairing it would put untracked judgment inside a step documented as mechanical.

RUN:
  python3 scripts/sms_import.py <full_dataset.csv>     append to the working file (once)
"""
from __future__ import annotations

import argparse, csv, os, re, sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sms_annotate import WORKING, W_FIELDS  # noqa: E402
from sms_transcribe import load_rules, problems  # noqa: E402

# Source token -> this corpus's placeholder. An allowlist, because in the source a bracketed
# word is usually text: [TB] and [QC] are how operators prefix a message.
MAP = {"PHONE": "PHONE", "BANK_ACC": "ACCOUNT", "MONEY": "AMOUNT", "DATE": "DATE",
       "TIME": "TIME", "NAME": "NAME", "OTP": "OTP", "URL": "URL",
       "NUMBER": "NUMBER", "POINT": "NUMBER"}
DATE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")


def convert(text: str) -> str:
    text = re.sub(r"\[([A-Z_]+)\]",
                  lambda m: f"<{MAP[m.group(1)]}>" if m.group(1) in MAP else m.group(0), text)
    return " ".join(text.split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="the source corpus's full_dataset.csv")
    a = ap.parse_args()

    with open(WORKING, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if any(r["message_id"].startswith("QAV_") for r in rows):
        raise SystemExit("[!] the working file already holds imported rows; delete them first "
                         "if this is a redo — appending twice would duplicate the subset")

    rules = load_rules()
    added, skipped = [], []
    with open(a.csv, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            text = convert(r["message"])
            why = problems(text, rules)
            if why:
                skipped.append((r["message_id"], why))
                continue
            m = DATE.fullmatch(r.get("date", "").strip())
            added.append({f: "" for f in W_FIELDS} | {
                "message_id": f"QAV_{r['message_id']}", "source": "qavn",
                "text": text, "capture": "imported", "sender_type": "unknown",
                "received_month": f"{m.group(3)}-{m.group(2)}" if m else "",
                "label_source": "benign" if r["label"].strip() == "0" else "scam"})
    with open(WORKING, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=W_FIELDS)
        w.writeheader()
        w.writerows(rows + added)
    labels = Counter(r["label_source"] for r in added)
    print(f"[+] {len(added)} imported row(s) appended ({dict(labels)}); "
          f"working file now {len(rows) + len(added)} row(s)")
    if skipped:
        print(f"[i] {len(skipped)} row(s) skipped for SCHEMA.md rule 2, kept out, not repaired:")
        for mid, why in skipped:
            print(f"    {mid}: {', '.join(why)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
