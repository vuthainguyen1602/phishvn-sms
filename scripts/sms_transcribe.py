#!/usr/bin/env python3
"""
sms_transcribe.py — turn a contributor's .zip of screenshots into submission rows.

The alternative route of PROTOCOL_sms_corpus.md §3. On this route the author sees unredacted
images, so the script's job is to keep that exposure short and on one machine: images are
re-encoded from their pixels on receipt (no file name, no metadata survives), transcribed, checked
by hand, redacted by the same rules as redact.html, and deleted.

Two steps, because the hand check sits between them:

  python3 scripts/sms_transcribe.py extract <submission.zip>
      Re-encodes every image into data/private/screenshots/<token>/, OCRs it (tesseract, Vietnamese),
      and writes draft.csv there with the raw OCR text. Open each image beside draft.csv, correct
      `text` to what the image shows (spelling as in the image, not as it should be), and fill
      `sender`, `sender_type` and, where the image shows a date, `received_month`.

  python3 scripts/sms_transcribe.py finalize data/private/screenshots/<token>
      Redacts `text`, refuses any row that still fails SCHEMA.md rule 2 or lacks a sender type,
      writes data/private/ingest/<token>.csv for `scripts/sms_collect.py --ingest data/private/ingest`,
      and deletes the images and the draft.

Refuses everything, as sms_collect.py does, until the protocol is approved: receiving screenshots
is collecting.
"""
from __future__ import annotations

import argparse, csv, io, json, os, re, secrets, shutil, subprocess, sys, zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sms_collect import FIELDS, MONTH, ROOT, gates  # noqa: E402

PAGE = os.path.join(_HERE, "redact.html")
PRIVATE = os.path.join(ROOT, "data", "private")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".heic", ".webp")
# CONTRIBUTE_vi.md §6: the contributor may name an image after what they think it is.
LABEL_HINT = {"that": "legitimate", "rac": "spam", "luadao": "phishing"}


def load_rules(page: str = PAGE) -> dict:
    """The rules block of redact.html. One copy of the rules, so the two routes cannot drift."""
    with open(page, encoding="utf-8") as fh:
        html = fh.read()
    m = re.search(r'<script type="application/json" id="rules">(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit(f"[!] no rules block in {page}")
    r = json.loads(m.group(1))
    tagged = lambda xs: [(x["tag"], re.compile(x["re"], re.I)) for x in xs]
    plain = lambda xs: [re.compile(x, re.I) for x in xs]
    return {"before": tagged(r["before"]), "links": plain(r["links"]), "in_links": tagged(r["in_links"]),
            "private_amounts": tagged(r["private_amounts"]), "amounts": plain(r["amounts"]),
            "text": tagged(r["text"])}


def _apply(text: str, rules: list) -> str:
    for tag, rx in rules:
        text = rx.sub(lambda m, t=tag: "".join(g or "" for g in m.groups()) + f"<{t}>", text)
    return text


def _protect(text: str, patterns: list, kept: list, fn=None) -> str:
    """Core.protect in redact.html: set each span aside behind a marker no text rule can match."""
    def keep(m):
        pre = m.group(1) or ""
        span = m.group(0)[len(pre):]
        kept.append(fn(span) if fn else span)
        return pre + "\x01" + chr(0xE000 + len(kept) - 1) + "\x01"
    for rx in patterns:
        text = rx.sub(keep, text)
    return text


def redact(text: str, rules: dict) -> str:
    """Core.redact in redact.html: links and broadcast amounts are kept, personal data inside a
    link and the contributor's own balance and movements are masked, the rest goes through the
    text rules."""
    kept = []
    text = _protect(_apply(text, rules["before"]), rules["links"], kept, lambda l: _apply(l, rules["in_links"]))
    text = _protect(_apply(text, rules["private_amounts"]), rules["amounts"], kept)
    text = _apply(text, rules["text"])
    return re.sub("\x01([\ue000-\uf8ff])\x01", lambda m: kept[ord(m.group(1)) - 0xE000], text)


def _outside(text: str, rules: dict):
    links, amounts = [], []
    text = _protect(_protect(text, rules["links"], links), rules["amounts"], amounts)
    return text, len(links), len(amounts)


def problems(text: str, rules: dict) -> list:
    """SCHEMA.md rule 2, as Core.problems checks it: outside the links and amounts a text keeps."""
    rest = re.sub(r"<[A-Z_]+>", "", _outside(text, rules)[0])
    p = []
    if re.search(r"\d{4,}", rest):
        p.append("a digit run of four or more outside a link or an amount")
    if "@" in re.sub(r"<[A-Z_]+>", "", text):
        p.append("an @")
    return p


def has_link(text: str, rules: dict) -> bool:
    return _outside(text, rules)[1] > 0


def has_money(text: str, rules: dict) -> bool:
    return "<AMOUNT>" in text or _outside(text, rules)[2] > 0


def ocr(path: str) -> str:
    if not shutil.which("tesseract"):
        raise SystemExit("[!] tesseract is not installed: brew install tesseract tesseract-lang")
    langs = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True).stdout.split()
    if "vie" not in langs:
        raise SystemExit("[!] tesseract has no Vietnamese model (vie): brew install tesseract-lang")
    out = subprocess.run(["tesseract", path, "stdout", "-l", "vie", "--psm", "6"],
                         capture_output=True, text=True, check=True).stdout
    return " ".join(out.split())


def reencode(data: bytes, dest: str) -> None:
    """A new PNG from the pixels alone: EXIF, device model, capture time and the original file name
    do not survive, because nothing but the pixel array is copied."""
    from PIL import Image
    with Image.open(io.BytesIO(data)) as im:
        im = im.convert("RGB")
        clean = Image.new("RGB", im.size)
        clean.putdata(list(im.getdata()))
        clean.save(dest, "PNG")


def extract(zpath: str) -> int:
    token = "z" + secrets.token_hex(6)
    out = os.path.join(PRIVATE, "screenshots", token)
    os.makedirs(out)
    rows = []
    with zipfile.ZipFile(zpath) as z:
        # Read members as bytes and never extract them: a crafted path or a symlink in the archive
        # cannot write anywhere, and the original files never touch the disk.
        members = [i for i in z.infolist() if not i.is_dir()
                   and os.path.splitext(i.filename)[1].lower() in IMAGE_EXT
                   and not os.path.basename(i.filename).startswith(".")]
        for n, info in enumerate(sorted(members, key=lambda i: i.filename), start=1):
            name = f"img_{n:03d}.png"
            reencode(z.read(info), os.path.join(out, name))
            stem = os.path.splitext(os.path.basename(info.filename))[0].lower()
            hint = next((v for k, v in LABEL_HINT.items() if stem.startswith(k)), "")
            rows.append({"image": name, "submission_token": token, "text": ocr(os.path.join(out, name)),
                         "capture": "screenshot", "sender": "", "sender_type": "", "received_month": "",
                         "label_contributor": hint,
                         # The contributor cropped, blacked out and reviewed the image before sending
                         # it (CONTRIBUTE_vi.md §6); that is what this flag records on this route.
                         "redaction_reviewed": 1})
    with open(os.path.join(out, "draft.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["image"] + FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"[+] {len(rows)} image(s) -> {os.path.relpath(out, ROOT)}")
    print(f"    Correct draft.csv against each image, then: python3 scripts/sms_transcribe.py finalize {os.path.relpath(out, ROOT)}")
    print(f"    Delete {zpath} now: its contents exist re-encoded, and the original is not needed.")
    return 0


def finalize(folder: str) -> int:
    rules = load_rules()
    draft = os.path.join(folder, "draft.csv")
    rows, bad = [], []
    with open(draft, newline="", encoding="utf-8") as fh:
        draft_rows = list(csv.DictReader(fh))
    for r in draft_rows:
        r["text"] = redact(r["text"].strip(), rules)
        why = problems(r["text"], rules)
        if r["sender_type"] not in ("brandname", "shortcode", "unknown"):
            why.append("no sender_type (brandname, shortcode or unknown)")
        if r["received_month"] and not MONTH.fullmatch(r["received_month"]):
            why.append("received_month is not YYYY-MM")
        if not r["text"]:
            why.append("empty text")
        (bad.append((r["image"], why)) if why else rows.append(r))
    if bad:
        # Nothing is written and nothing deleted: fix the draft (mask by hand with <ID> and the like
        # where the rules missed something) and run again.
        raise SystemExit("[!] not finalized:\n" + "".join(f"    {i}: {', '.join(w)}\n" for i, w in bad))
    token = os.path.basename(os.path.normpath(folder))
    os.makedirs(os.path.join(PRIVATE, "ingest"), exist_ok=True)
    dest = os.path.join(PRIVATE, "ingest", f"{token}.csv")
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    shutil.rmtree(folder)
    print(f"[+] {len(rows)} row(s) -> {os.path.relpath(dest, ROOT)}; images and draft deleted")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("extract").add_argument("zip")
    sub.add_parser("finalize").add_argument("folder")
    a = ap.parse_args()
    bad = gates()
    if bad:
        raise SystemExit("[!] collection is not permitted yet, and receiving screenshots is collecting:\n"
                         + "".join(f"    - {b}\n" for b in bad))
    return extract(a.zip) if a.cmd == "extract" else finalize(a.folder)


if __name__ == "__main__":
    sys.exit(main())
