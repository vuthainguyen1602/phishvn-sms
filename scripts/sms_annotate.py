#!/usr/bin/env python3
"""
sms_annotate.py — the working file and its labels, the way PROTOCOL_sms_corpus.md §4–5 say.

Four steps, because the independence sits between them:

  init        build data/private/sms_working.csv from the submissions file: message_id in ingest
              order, participant_id per submission token (or per --map, when the author knows two
              tokens are one person). The file this creates is the reason data/ is private.
  label       one annotator labels every unlabelled message, shown THE TEXT AND NOTHING ELSE:
              not the other annotator's label, not the contributor's, not the sender. The blind
              is procedural — the columns are in the file — so the tool shows none of them, and
              annotators use the tool.
  adjudicate  rows where the two agree become final_label with no adjudicator; disagreements and
              every `uncertain` are decided one by one, with the full row visible and a one-line
              note recorded. §4's rule is printed where it is needed: a message is not made
              phishing because it looks suspicious — evidence of deceptive intent, or it is spam.
  report      Cohen's kappa before adjudication, the disagreement rate per class pair, and the
              share adjudicated — reported whatever they show (§5), so computed by one script
              rather than by hand the night the numbers are needed.

RUN:
  python3 scripts/sms_annotate.py init [submissions.csv] [--map tokens.csv]
  python3 scripts/sms_annotate.py label --annotator 1     (then, separately, --annotator 2)
  python3 scripts/sms_annotate.py adjudicate --by <name>
  python3 scripts/sms_annotate.py report
"""
from __future__ import annotations

import argparse, csv, os, sys
from collections import Counter
from itertools import combinations

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sms_collect import FIELDS, ROOT  # noqa: E402

SUBMISSIONS = os.path.join(ROOT, "data", "raw", "sms_corpus", "submissions.csv")
WORKING = os.path.join(ROOT, "data", "private", "sms_working.csv")
# SCHEMA_raw.md §2, in its order. template_id and split are carried if the source has them and
# left empty otherwise: sms_templates.py and sms_split.py fill them on this file later.
W_FIELDS = (["message_id", "participant_id"] + FIELDS
            + ["label_annotator_1", "label_annotator_2", "adjudicated_by", "adjudication_note",
               "final_label", "template_id", "split"])
LABELS = {"1": "legitimate", "2": "spam", "3": "phishing"}
RULE = "§4: not phishing because it looks suspicious — evidence of deceptive intent, or it is spam"


def _read(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames or [], list(r)


def _write(path: str, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=W_FIELDS)
        w.writeheader()
        w.writerows(rows)


def init(sub: str, map_path: str | None) -> int:
    if os.path.exists(WORKING):
        # Labels live in this file; a silent rebuild would discard them.
        raise SystemExit(f"[!] {os.path.relpath(WORKING, ROOT)} exists; delete it yourself first")
    _, rows = _read(sub)
    pid = {}
    if map_path:
        _, m = _read(map_path)
        pid = {r["submission_token"]: r["participant_id"] for r in m}
    out = []
    for i, r in enumerate(rows, start=1):
        tok = r["submission_token"]
        if tok not in pid:
            pid[tok] = f"P{len(set(pid.values())) + 1:03d}"
        out.append({**{f: r.get(f, "") for f in W_FIELDS},
                    "message_id": f"SMS_{i:05d}", "participant_id": pid[tok]})
    os.makedirs(os.path.dirname(WORKING), exist_ok=True)
    _write(WORKING, out)
    per = Counter(r["participant_id"] for r in out)
    print(f"[+] {len(out)} row(s) -> {os.path.relpath(WORKING, ROOT)}; "
          f"{len(per)} participant(s): " + ", ".join(f"{p}={n}" for p, n in sorted(per.items())))
    if not map_path and len(per) > 1:
        print("    One participant per token. If one person sent twice, rerun init with --map "
              "(submission_token,participant_id): leave-one-contributor-out folds depend on it.")
    return 0


def label(annotator: str) -> int:
    col = f"label_annotator_{annotator}"
    _, rows = _read(WORKING)
    todo = [r for r in rows if not r[col].strip()]
    print(f"{len(todo)} message(s) to label as annotator {annotator}. {RULE}.")
    done = 0
    for r in todo:
        print(f"\n--- {r['message_id']} " + "-" * 40)
        print(r["text"])
        while True:
            k = input("[1] legitimate  [2] spam  [3] phishing  [u] uncertain  "
                      "[s] skip  [q] save and quit > ").strip().lower()
            if k in LABELS or k in ("u", "s", "q"):
                break
        if k == "q":
            break
        if k == "s":
            continue
        r[col] = "uncertain" if k == "u" else LABELS[k]
        done += 1
    _write(WORKING, rows)
    left = sum(1 for r in rows if not r[col].strip())
    print(f"\n[+] {done} labelled this session, {left} still empty for annotator {annotator}")
    return 0


def adjudicate(by: str) -> int:
    _, rows = _read(WORKING)
    agreed = queue = 0
    for r in rows:
        a, b = r["label_annotator_1"].strip(), r["label_annotator_2"].strip()
        if not a or not b or r["final_label"].strip():
            continue
        if a == b and a != "uncertain":
            r["final_label"] = a          # no adjudicator: the agreement is the decision
            agreed += 1
        else:
            queue += 1
    print(f"[+] {agreed} agreement(s) finalized, {queue} row(s) to adjudicate. {RULE}.")
    for r in rows:
        a, b = r["label_annotator_1"].strip(), r["label_annotator_2"].strip()
        if not a or not b or r["final_label"].strip() or (a == b and a != "uncertain"):
            continue
        print(f"\n--- {r['message_id']} " + "-" * 40)
        print(r["text"])
        print(f"    sender: {r['sender'] or '(none)'} ({r['sender_type']}), capture: {r['capture']}")
        print(f"    annotator 1: {a}   annotator 2: {b}   contributor: {r['label_contributor']}")
        while True:
            k = input("final [1] legitimate  [2] spam  [3] phishing  [q] save and quit > ").strip().lower()
            if k in LABELS or k == "q":
                break
        if k == "q":
            break
        r["final_label"] = LABELS[k]
        r["adjudicated_by"] = by
        r["adjudication_note"] = input("one line of reasoning > ").strip()
    _write(WORKING, rows)
    left = sum(1 for r in rows if r["label_annotator_1"].strip() and r["label_annotator_2"].strip()
               and not r["final_label"].strip())
    print(f"\n[+] saved; {left} row(s) still awaiting adjudication")
    return 0


def report() -> int:
    _, rows = _read(WORKING)
    both = [(r["label_annotator_1"].strip(), r["label_annotator_2"].strip())
            for r in rows if r["label_annotator_1"].strip() and r["label_annotator_2"].strip()]
    if not both:
        print("[i] nothing labelled by both annotators yet")
        return 0
    n = len(both)
    po = sum(a == b for a, b in both) / n
    c1, c2 = Counter(a for a, _ in both), Counter(b for _, b in both)
    pe = sum(c1[k] * c2[k] for k in set(c1) | set(c2)) / (n * n)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    sent = sum(a != b or a == "uncertain" for a, b in both)
    print(f"labelled by both: {n}")
    print(f"Cohen's kappa (before adjudication): {kappa:.3f}  (po {po:.3f}, pe {pe:.3f})")
    print(f"sent to adjudication: {sent} ({100 * sent / n:.1f}%)")
    pairs = Counter(tuple(sorted((a, b))) for a, b in both if a != b)
    if pairs:
        print("disagreements per class pair:")
        for (a, b), c in pairs.most_common():
            print(f"  {a} / {b}: {c}")
    final = Counter(r["final_label"].strip() for r in rows if r["final_label"].strip())
    if final:
        print(f"final labels so far: {dict(final)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("submissions", nargs="?", default=SUBMISSIONS)
    p.add_argument("--map", default=None, help="CSV of submission_token,participant_id")
    p = sub.add_parser("label")
    p.add_argument("--annotator", required=True, choices=("1", "2"))
    p = sub.add_parser("adjudicate")
    p.add_argument("--by", required=True)
    sub.add_parser("report")
    a = ap.parse_args()
    if a.cmd == "init":
        return init(a.submissions, a.map)
    if a.cmd == "label":
        return label(a.annotator)
    if a.cmd == "adjudicate":
        return adjudicate(a.by)
    return report()


if __name__ == "__main__":
    sys.exit(main())
