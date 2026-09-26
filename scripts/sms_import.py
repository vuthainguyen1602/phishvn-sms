#!/usr/bin/env python3
"""
sms_import.py — the external test set: a published corpus, kept as an independent benchmark.

The corpus imported is the *Quality-Assured Vietnamese SMS Phishing Dataset* (CC BY 4.0),
credited in the paper. It is NOT merged into this corpus and NOT re-annotated: it is a held-out
**external benchmark**, kept with its own binary labels, on which a model trained on the
contributed corpus is evaluated (PROTOCOL §7). Two label schemes meet here — the source's
genuine-sender-vs-scam and this project's three classes — so the evaluation collapses a model's
prediction to the source's binary space rather than pretending the labels are the same.

What import does, and only this:
- re-encodes each row's placeholder tokens into this corpus's (`[MONEY]`→`<AMOUNT>` and so on, by
  the allowlist below; `[TB]`/`[QC]` and brand prefixes are message text, not placeholders);
- keeps the source's own label in `label_source` (`benign`/`scam`), which is the evaluation
  label, unchanged;
- marks the row `source = qavn`, `capture = imported`, `split = external`, `queued = 0` — it is
  never in the annotation queue (§5) and never in the train/validation/test split (§7);
- refuses a row that still fails SCHEMA.md rule 2 after mapping, dropped and named, never
  repaired by hand.

`message_id` is `QAV_` plus the source's own id, so any row can be checked against the original.

RUN:
  python3 scripts/sms_import.py <full_dataset.csv>     load the external set into the working file
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
        raise SystemExit("[!] the working file already holds the external set; delete those rows "
                         "first if this is a redo — appending twice would duplicate it")

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
                "label_source": "benign" if r["label"].strip() == "0" else "scam",
                "queued": "0", "split": "external"})
    with open(WORKING, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=W_FIELDS)
        w.writeheader()
        w.writerows(rows + added)
    labels = Counter(r["label_source"] for r in added)
    print(f"[+] {len(added)} external row(s) appended ({dict(labels)}); "
          f"split=external, not annotated, not in train/val/test; "
          f"working file now {len(rows) + len(added)} row(s)")
    if skipped:
        print(f"[i] {len(skipped)} row(s) skipped for SCHEMA.md rule 2, kept out, not repaired:")
        for mid, why in skipped:
            print(f"    {mid}: {', '.join(why)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
