#!/usr/bin/env python3
"""
sms_publish.py — produce sms_dataset.csv from the working file, by dropping columns.

SCHEMA_raw.md §3 promises this step is mechanical, and a promise about a manual step is worth
nothing: no value is edited, nothing is added except the four derived flags SCHEMA.md defines,
and the columns that do not ship are simply not written. What is dropped, and why each column is
dropped, is SCHEMA_raw's §3 table; this script only enforces the projection it states.

The derived flags come from one place each: `has_url` and `has_money` from the link and amount
patterns of redact.html — the same single copy of the rules every other stage reads — and
`has_phone` and `has_otp` from the presence of their placeholder in the text.

It refuses a working file with holes rather than publishing around them: every row must carry a
final_label that is one of the three classes (`uncertain` never ships), a template_id and a
split. A partially adjudicated corpus is not a publishable one, and the refusal names each row.

RUN:
  python3 scripts/sms_publish.py                        # working file -> data/sms_dataset.csv
  python3 scripts/sms_publish.py <working.csv> --out <dataset.csv>
"""
from __future__ import annotations

import argparse, csv, os, sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sms_collect import ROOT  # noqa: E402
from sms_transcribe import has_link, has_money, load_rules  # noqa: E402

WORKING = os.path.join(ROOT, "data", "private", "sms_working.csv")
OUT = os.path.join(ROOT, "data", "sms_dataset.csv")
EXT_OUT = os.path.join(ROOT, "data", "sms_external_qavn.csv")
# SCHEMA.md, in its order. Everything in the working file and not here is dropped, unnamed:
# naming the dropped columns twice would let the two lists drift.
PUB_FIELDS = ["message_id", "text", "source", "capture", "final_label", "label_annotator_1",
              "label_annotator_2", "template_id", "sender_type", "has_url",
              "has_phone", "has_otp", "has_money", "split"]
# The external benchmark ships separately (PROTOCOL §7): its evaluation label is the source
# corpus's own `label_source`, and it carries no final_label, annotator labels or train split.
EXT_FIELDS = ["message_id", "text", "label_source", "template_id", "sender_type", "has_url",
              "has_phone", "has_otp", "has_money"]
LABELS = ("legitimate", "spam", "phishing")
SPLITS = ("train", "validation", "test")


def project(row: dict, rules: dict, fields: list = PUB_FIELDS) -> dict:
    out = {f: row[f] for f in fields if f in row}
    text = row["text"]
    for flag, present in (("has_url", has_link(text, rules)), ("has_phone", "<PHONE>" in text),
                          ("has_otp", "<OTP>" in text), ("has_money", has_money(text, rules))):
        if flag in fields:
            out[flag] = int(present)
    return out


def holes(row: dict) -> list:
    why = []
    if row.get("final_label", "").strip() not in LABELS:
        why.append(f"final_label {row.get('final_label', '')!r} is not one of {'/'.join(LABELS)}")
    if not row.get("template_id", "").strip():
        why.append("no template_id: run sms_templates.py --assign")
    if row.get("split", "").strip() not in SPLITS:
        why.append(f"split {row.get('split', '')!r} is not one of {'/'.join(SPLITS)}")
    if row.get("sender_type", "").strip() not in ("brandname", "shortcode", "unknown"):
        why.append("sender_type is not brandname/shortcode/unknown")
    return why


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("working", nargs="?", default=WORKING)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--ext-out", default=EXT_OUT)
    a = ap.parse_args()

    with open(a.working, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rules = load_rules()

    # The external benchmark ships to its own file with the source's own label; it is never
    # annotated and never in the train/validation/test split (PROTOCOL §7).
    external = [r for r in rows if r.get("split", "").strip() == "external"]

    # The primary corpus is the train/validation/test rows; each must be whole. Any other row
    # (an unannotated leftover) is left out and counted, not treated as a hole.
    primary = [r for r in rows if r.get("split", "").strip() in SPLITS]
    leftover = len(rows) - len(external) - len(primary)
    bad = [(r.get("message_id", f"row {i}"), holes(r)) for i, r in enumerate(primary, start=2)]
    bad = [(m, w) for m, w in bad if w]
    if bad:
        raise SystemExit("[!] not published, the primary corpus has holes:\n"
                         + "".join(f"    {m}: {'; '.join(w)}\n" for m, w in bad))

    out = [project(r, rules) for r in primary]
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=PUB_FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"[+] {len(out)} row(s) -> {os.path.relpath(a.out, ROOT)}; "
          f"labels {dict(Counter(r['final_label'] for r in out))}; "
          f"splits {dict(Counter(r['split'] for r in out))}"
          + (f"; {leftover} unannotated row(s) left out" if leftover else ""))

    if external:
        ext = [project(r, rules, EXT_FIELDS) for r in external]
        with open(a.ext_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=EXT_FIELDS)
            w.writeheader()
            w.writerows(ext)
        print(f"[+] {len(ext)} row(s) -> {os.path.relpath(a.ext_out, ROOT)} "
              f"(external benchmark); source labels {dict(Counter(r['label_source'] for r in ext))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
