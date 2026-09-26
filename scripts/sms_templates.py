#!/usr/bin/env python3
"""
sms_templates.py — group messages into templates, the way PROTOCOL_sms_corpus.md §6 says.

Grouping runs on a normalized view of the text that exists only inside this script: lower-cased,
whitespace collapsed, placeholder tokens kept, every URL and money amount replaced by <URL> or
<AMT>. The published text keeps both; for grouping they are the slots a campaign rotates, and a
pilot batch showed what leaving them in place does — a scam re-sent with one edited character in
the domain, or a different lure amount, fell below τ even at 0.7, because in a message of eight
words one changed word destroys four shingles. The URL and amount patterns are read from
redact.html so the two views cannot drift; one grouping-only pattern is added for the short
amounts (60K, 128K) that redaction rightly ignores and grouping must not.

Each normalized message becomes the set of its word 4-shingles (a message shorter than four words
is its own single shingle); pairs at or above Jaccard τ = 0.8 are linked and a template is a
connected component. Pairwise comparison is O(n²), which at pilot scale (§1) is a few seconds and
not worth an index.

RUN:
  python3 scripts/sms_templates.py <file.csv>            report template counts at τ = 0.7/0.8/0.9
  python3 scripts/sms_templates.py --assign <file.csv>   also write template_id (T001…) at τ = 0.8

--assign numbers templates in order of first appearance and rewrites the file in place, replacing
any template_id column already there: the id is computed, so recomputing is the only honest way
to change it.
"""
from __future__ import annotations

import argparse, csv, os, re, sys
from itertools import combinations

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sms_transcribe import load_rules  # noqa: E402

# Grouping-only: one to three digits with a Vietnamese money unit. Redaction skips these because
# two digits identify nobody; grouping tokenizes them because they are the lure a campaign rotates.
SHORT_AMOUNT = re.compile(r"(^|[^A-Za-z0-9.,])\d{1,3}\s?(?:k|tr|trieu|triệu|ty|tỷ)(?![A-Za-z0-9])",
                          re.I)
TAUS = (0.7, 0.8, 0.9)
PRIMARY = 0.8


def normalize(text: str, rules: dict) -> str:
    """§6's normalized view. Substitution keeps any leading context group the pattern captured,
    as redact.html's own rules do."""
    keep = lambda tag: (lambda m: (m.group(1) if m.groups() else "") + f" {tag} ")
    for rx in rules["links"]:
        text = rx.sub(keep("<URL>"), text)
    for rx in rules["amounts"]:
        text = rx.sub(keep("<AMT>"), text)
    text = SHORT_AMOUNT.sub(keep("<AMT>"), text)
    return " ".join(text.lower().split())


def shingles(normalized: str) -> frozenset:
    words = normalized.split(" ")
    if len(words) < 4:
        return frozenset({tuple(words)})
    return frozenset(tuple(words[i:i + 4]) for i in range(len(words) - 3))


def components(sets: list, tau: float) -> list:
    """Union-find over pairs at or above tau; returns one root index per message."""
    parent = list(range(len(sets)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in combinations(range(len(sets)), 2):
        if len(sets[i] & sets[j]) / len(sets[i] | sets[j]) >= tau:
            parent[find(i)] = find(j)
    return [find(i) for i in range(len(sets))]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="a CSV with a text column (the working file, normally)")
    ap.add_argument("--assign", action="store_true",
                    help=f"write template_id at τ = {PRIMARY} back into the file")
    a = ap.parse_args()

    with open(a.csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields, rows = reader.fieldnames or [], list(reader)
    if "text" not in fields:
        raise SystemExit(f"[!] {a.csv} has no text column")

    rules = load_rules()
    sets = [shingles(normalize(r["text"], rules)) for r in rows]

    roots_at = {tau: components(sets, tau) for tau in TAUS}
    for tau in TAUS:
        n = len(set(roots_at[tau]))
        print(f"τ = {tau}: {n} template(s)"
              + ("  (primary)" if tau == PRIMARY else ""))
    counts = [len(set(roots_at[tau])) for tau in TAUS]
    if len(set(counts)) > 1:
        print("[i] the count moves with τ: chaining is present, look at the merged groups"
              " before trusting the primary")

    if not a.assign:
        return 0
    ids, order = {}, roots_at[PRIMARY]
    for root in order:
        if root not in ids:
            ids[root] = f"T{len(ids) + 1:03d}"
    if "template_id" not in fields:
        fields = fields + ["template_id"]
    for r, root in zip(rows, order):
        r["template_id"] = ids[root]
    with open(a.csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"[+] template_id written to {a.csv}: {len(ids)} template(s) over {len(rows)} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
