#!/usr/bin/env python3
"""
sms_split.py — assign the fixed 70/15/15 template-disjoint split of PROTOCOL_sms_corpus.md §7.

**Every message of one template lies in one split.** The unit assigned is the template, never the
message, so the fixed split cannot ask a model to remember a training text and call it detection.
The primary evaluation stays cross-validation over template groups; this split ships for
presentation, and with a pilot corpus its test slice is small and the paper says so where it
reports it.

Assignment is deterministic and recorded here rather than in anyone's shell history: templates
are dealt greedily, largest first with seeded random tie-breaking, to the split furthest under
its message target; this is repeated over a fixed number of seeded restarts, and the kept
assignment is the one closest to both the 70/15/15 message fractions and, in each split, the
label mix of the whole file. Seed and restart count are constants below, so the split is
reproducible from the working file alone.

The label balanced against is, per row, the first of `final_label`, `label_contributor`,
`label_source` that holds a value — adjudicated when it exists, the contributor's or the source
corpus's opinion before then. Vocabularies mix across those columns; for balancing that is fine,
proportions of each value are held even, and none of this feeds any label that ships.

RUN:
  python3 scripts/sms_split.py <file.csv>            report the split it would assign
  python3 scripts/sms_split.py --assign <file.csv>   also write the split column into the file
"""
from __future__ import annotations

import argparse, csv, random, sys
from collections import Counter, defaultdict

FRACTIONS = {"train": 0.70, "validation": 0.15, "test": 0.15}
SEED = 1602        # fixed forever once the corpus ships; changing it is a new split, not a rerun
RESTARTS = 200     # cheap at any plausible template count, and the score plateaus long before


def deal(templates: list, sizes: dict, rng: random.Random) -> dict:
    """One greedy deal: largest template first (seeded tie-break), each to the split furthest
    under its target share of messages."""
    order = sorted(templates, key=lambda t: (-sizes[t], rng.random()))
    filled = {s: 0 for s in FRACTIONS}
    total = sum(sizes.values())
    out = {}
    for t in order:
        s = min(FRACTIONS, key=lambda s: filled[s] / (FRACTIONS[s] * total))
        out[t] = s
        filled[s] += sizes[t]
    return out

def score(assign: dict, sizes: dict, labels_of: dict) -> float:
    """Distance from the ideal: message fractions off 70/15/15, plus each split's label mix off
    the whole file's. Both terms are sums of absolute proportion errors, comparable by design."""
    total = sum(sizes.values())
    whole = Counter()
    for t, c in labels_of.items():
        whole.update(c)
    err = 0.0
    for s, frac in FRACTIONS.items():
        tpls = [t for t in assign if assign[t] == s]
        n = sum(sizes[t] for t in tpls)
        err += abs(n / total - frac)
        if whole:
            mix = Counter()
            for t in tpls:
                mix.update(labels_of[t])
            for lab in whole:
                err += abs((mix[lab] / n if n else 0) - whole[lab] / total)
    return err


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="a CSV with a template_id column (the working file, normally)")
    ap.add_argument("--assign", action="store_true", help="write the split column into the file")
    a = ap.parse_args()

    with open(a.csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields, rows = reader.fieldnames or [], list(reader)
    if "template_id" not in fields:
        raise SystemExit(f"[!] {a.csv} has no template_id column: run sms_templates.py --assign first")
    # Per row, the first label column that holds a value: a working file before adjudication has
    # an empty final_label column, and an imported row carries label_source instead of a
    # contributor's label. Balancing against emptiness balances nothing.
    cols = [c for c in ("final_label", "label_contributor", "label_source") if c in fields]
    label = lambda r: next((r[c].strip() for c in cols if r[c].strip()), "")

    # Rows already marked split=external are the held-out benchmark (PROTOCOL §7): they are not
    # part of the train/validation/test split and keep their split untouched.
    external = [i for i, r in enumerate(rows) if r.get("split", "").strip() == "external"]

    by_tpl = defaultdict(list)
    for i, r in enumerate(rows):
        if i not in set(external):
            by_tpl[r["template_id"]].append(i)
    sizes = {t: len(m) for t, m in by_tpl.items()}
    labels_of = {t: Counter(x for x in (label(rows[i]) for i in m) if x)
                 for t, m in by_tpl.items()}

    best, best_err = None, None
    for restart in range(RESTARTS):
        cand = deal(list(by_tpl), sizes, random.Random(SEED + restart))
        err = score(cand, sizes, labels_of)
        if best_err is None or err < best_err:
            best, best_err = cand, err

    total = sum(len(m) for m in by_tpl.values())
    print(f"{'split':6} {'tin':>4} {'%':>6} {'template':>9}  labels")
    for s in FRACTIONS:
        tpls = sorted(t for t in best if best[t] == s)
        idx = [i for t in tpls for i in by_tpl[t]]
        mix = dict(Counter(x for x in (label(rows[i]) for i in idx) if x))
        print(f"{s:6} {len(idx):>4} {100 * len(idx) / total:>5.1f} {len(tpls):>9}  {mix}")
    if external:
        mix = dict(Counter(x for x in (label(rows[i]) for i in external) if x))
        print(f"{'external':6} {len(external):>4} {'':>6} {'':>9}  {mix}  (held out, PROTOCOL §7)")

    if not a.assign:
        return 0
    if "split" not in fields:
        fields = fields + ["split"]
    for t, members in by_tpl.items():
        for i in members:
            rows[i]["split"] = best[t]
    with open(a.csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"[+] split written to {a.csv} (seed {SEED}, {RESTARTS} restarts, error {best_err:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
