#!/usr/bin/env python3
"""
sms_imessage.py — the author's own inbox, read from Messages on the author's Mac.

A third route beside the paste page and the screenshot zip, for one contributor only: the author,
whose iPhone forwards its SMS to the Mac, where Messages keeps them in ~/Library/Messages/chat.db.
Nothing is received from anybody, so nothing here is collection in the protocol's sense and the
gate of sms_collect.py is not applied; what IS open is whether this batch may enter the corpus at
all (PROTOCOL, amendment of 2026-10-04; the paper's "included / excluded"), and that question is
answered in the documents, not by this script. It writes an ingest file and stops; appending to submissions.csv is
sms_collect.py's job and stays gated.

What leaves the database, and no more: received SMS. iMessage rows are personal conversations and
the query never selects them; messages the author sent are not selected either. The sender is kept
as the handset shows it when it is a brandname or a shortcode, and reduced to a country prefix
(`+84-mobile`) when it is a number — the convention of the community batch. The date becomes a
month. The text is redacted by the same rules as every other route (one rules block, in redact.html).

Two steps, because the hand check sits between them:

  python3 scripts/sms_imessage.py extract [--db ~/Library/Messages/chat.db] [--since YYYY-MM] [--unique]
      Copies the database (with its WAL) to a temporary folder, reads the received SMS, deletes the
      copy, and writes data/private/imessage/<token>/draft.csv: the raw `text`, the redaction
      `preview`, and `problems` naming what the rules would still leave in. Read the preview, mask
      by hand in `text` (with <ID>, <ACCOUNT>, <NAME> and the like) where the rules missed, fill
      `label_contributor` if you want your own reading recorded, delete rows that should not go
      (a person who texted you from a number; a message about you alone). --unique drops exact
      repeats within the batch — MobiFone sends the same promotion many times.

  python3 scripts/sms_imessage.py finalize data/private/imessage/<token> [--participant AUTHOR]
      Redacts `text`, refuses any row that still fails SCHEMA.md rule 2, writes
      data/private/ingest/<token>.csv, records the token in provenance.csv and participants.csv,
      and deletes the draft. The participant code is not C-MIX: this batch is attributable, to the
      author, and leave-one-contributor-out must see that.
"""
from __future__ import annotations

import argparse, csv, datetime as dt, os, re, secrets, shutil, sqlite3, sys, tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sms_collect import FIELDS, MONTH, ROOT, gates  # noqa: E402
from sms_transcribe import PRIVATE, load_rules, problems, redact  # noqa: E402

DB = os.path.expanduser("~/Library/Messages/chat.db")
SUBMISSIONS = os.path.join(ROOT, "data", "raw", "sms_corpus", "submissions.csv")
DRAFT_FIELDS = ["n"] + FIELDS + ["preview", "problems"]
LABELS = ("", "legitimate", "spam", "phishing")
# Apple's epoch is 2001-01-01; rows written since macOS 10.13 store nanoseconds, older ones seconds.
APPLE_EPOCH = 978307200
# Country codes seen in a Vietnamese inbox, longest first so +855 is not read as +85. Anything
# else is reported as "+?" and left to the hand check rather than guessed.
COUNTRY = ("855", "856", "852", "853", "880", "886", "971", "966", "965", "974", "212",
           "84", "86", "81", "82", "60", "62", "63", "65", "66", "91", "92", "61", "64", "44", "49",
           "33", "39", "34", "31", "46", "47", "48", "20", "27", "90", "98",
           "1", "7")
_SHORT = re.compile(r"\+?\d{1,7}")
_NUMBER = re.compile(r"\+?\d{8,}")


def decode_body(blob: bytes | None) -> str:
    """The text of a row whose `text` column is NULL: Messages stores it in `attributedBody`, an
    NSAttributedString archived as a typedstream. The string sits right after the NSString class
    marker as a '+' tag, a length (one byte, or 0x81 + two bytes, or 0x82 + four, little-endian)
    and that many bytes of UTF-8. Nothing else in the stream is wanted."""
    if not blob:
        return ""
    i = blob.find(b"NSString")
    if i < 0:
        return ""
    j = blob.find(b"+", i)
    if j < 0:
        return ""
    k = j + 1
    ln = blob[k]
    if ln == 0x81:
        ln, k = int.from_bytes(blob[k + 1:k + 3], "little"), k + 3
    elif ln == 0x82:
        ln, k = int.from_bytes(blob[k + 1:k + 5], "little"), k + 5
    else:
        k += 1
    return blob[k:k + ln].decode("utf-8", "replace")


def clean(text: str) -> str:
    """U+FFFC marks an attachment slot in an attributed string; it is not text."""
    return " ".join(text.replace("￼", " ").split())


def month(date: int | None) -> str:
    if not date:
        return ""
    secs = date / 1e9 if date > 1e12 else date
    return dt.datetime.fromtimestamp(secs + APPLE_EPOCH).strftime("%Y-%m")


def sender(handle: str) -> tuple[str, str, str]:
    """(sender, sender_type, note). A handle with a letter is a brandname; up to seven digits is a
    shortcode; a longer number is a personal number, reduced to its country prefix with a note so
    the hand check sees it — PROTOCOL §1 collects none under the protocol, and the author decides
    for their own inbox."""
    h = (handle or "").strip()
    if not h:
        return "", "unknown", "no sender on the row"
    if _SHORT.fullmatch(h):
        return h, "shortcode", ""
    if _NUMBER.fullmatch(h):
        digits = h.lstrip("+")
        if h.startswith("0"):
            cc = "84"
        else:
            cc = next((c for c in COUNTRY if digits.startswith(c)), "?")
        return f"+{cc}-mobile", "unknown", "personal number"
    return h, "brandname", ""


def _norm(text: str) -> str:
    return " ".join(text.split()).lower()


def read_received_sms(db: str, since: str | None):
    """Copy the database beside its WAL, read it immutable, delete the copy. The copy exists for
    the seconds this function runs: a live Messages database is locked and mid-write, and the
    copy is as private as the original."""
    tmp = tempfile.mkdtemp(prefix="imsg-")
    try:
        for ext in ("", "-wal", "-shm"):
            if os.path.exists(db + ext):
                shutil.copy2(db + ext, os.path.join(tmp, "chat.db" + ext))
        con = sqlite3.connect(f"file:{os.path.join(tmp, 'chat.db')}?mode=ro", uri=True)
        try:
            rows = con.execute(
                "SELECT m.ROWID, h.id, m.text, m.attributedBody, m.date FROM message m "
                "LEFT JOIN handle h ON h.ROWID = m.handle_id "
                "WHERE m.service = 'SMS' AND m.is_from_me = 0 ORDER BY m.date").fetchall()
        finally:
            con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = []
    for _rowid, handle, text, body, date in rows:
        m = month(date)
        if since and m and m < since:
            continue
        out.append((handle, clean(text or decode_body(body)), m))
    return out


def extract(db: str, since: str | None, unique: bool) -> int:
    if since and not MONTH.fullmatch(since):
        raise SystemExit("[!] --since takes YYYY-MM")
    if not os.path.exists(db):
        raise SystemExit(f"[!] {db} does not exist. Messages on this Mac must hold the iPhone's SMS "
                         "(Settings > Messages > Text Message Forwarding), and the terminal needs "
                         "Full Disk Access to read it.")
    rules = load_rules()
    known = set()
    if os.path.exists(SUBMISSIONS):
        with open(SUBMISSIONS, newline="", encoding="utf-8") as fh:
            known = {_norm(r["text"]) for r in csv.DictReader(fh)}
    token = "z" + secrets.token_hex(6)
    folder = os.path.join(PRIVATE, "imessage", token)
    rows, seen = [], set()
    empty = dup_known = dup_batch = personal = 0
    for handle, text, m in read_received_sms(db, since):
        if not text:
            empty += 1
            continue
        preview = redact(text, rules)
        key = _norm(preview)
        if key in known:
            dup_known += 1
            continue
        if key in seen:
            dup_batch += 1
            if unique:
                continue
        seen.add(key)
        s, stype, note = sender(handle)
        personal += note == "personal number"
        why = problems(preview, rules) + ([note] if note else [])
        rows.append({"n": len(rows) + 1, "submission_token": token, "text": text, "capture": "paste",
                     "sender": s, "sender_type": stype, "received_month": m, "label_contributor": "",
                     # The author reads every preview before finalize; that is what the flag records.
                     "redaction_reviewed": 1, "preview": preview, "problems": "; ".join(why)})
    if not rows:
        raise SystemExit("[!] no received SMS to write")
    os.makedirs(folder)
    with open(os.path.join(folder, "draft.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=DRAFT_FIELDS)
        w.writeheader()
        w.writerows(rows)
    flagged = sum(1 for r in rows if r["problems"])
    rel = os.path.relpath(folder, ROOT)
    print(f"[+] {len(rows)} received SMS -> {rel}/draft.csv")
    print(f"    skipped: {empty} with no text, {dup_known} already in submissions.csv, "
          f"{dup_batch} exact repeat(s) within the batch{' (dropped)' if unique else ' (kept; --unique drops them)'}")
    print(f"    {flagged} row(s) carry a note in `problems` ({personal} from a personal number); "
          "fix `text` by hand or delete the row")
    print(f"    then: python3 scripts/sms_imessage.py finalize {rel}")
    return 0


def _append(path: str, header: list, row: dict) -> None:
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        if new:
            w.writeheader()
        w.writerow(row)


def finalize(folder: str, participant: str) -> int:
    rules = load_rules()
    draft = os.path.join(folder, "draft.csv")
    if not os.path.exists(draft):
        raise SystemExit(f"[!] no draft.csv in {folder}")
    with open(draft, newline="", encoding="utf-8") as fh:
        draft_rows = list(csv.DictReader(fh))
    rows, bad = [], []
    for r in draft_rows:
        r["text"] = redact(r["text"].strip(), rules)
        why = problems(r["text"], rules)
        if r["sender_type"] not in ("brandname", "shortcode", "unknown"):
            why.append("no sender_type (brandname, shortcode or unknown)")
        if r["received_month"] and not MONTH.fullmatch(r["received_month"]):
            why.append("received_month is not YYYY-MM")
        if r.get("label_contributor", "") not in LABELS:
            why.append("label_contributor is not legitimate, spam, phishing or empty")
        if not r["text"]:
            why.append("empty text")
        (bad.append((r["n"], why)) if why else rows.append(r))
    if bad:
        # Nothing is written and nothing deleted: fix the draft and run again.
        raise SystemExit("[!] not finalized:\n" + "".join(f"    row {i}: {', '.join(w)}\n" for i, w in bad))
    token = os.path.basename(os.path.normpath(folder))
    os.makedirs(os.path.join(PRIVATE, "ingest"), exist_ok=True)
    dest = os.path.join(PRIVATE, "ingest", f"{token}.csv")
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    months = sorted(m for m in {r["received_month"] for r in rows} if m)
    span = f"{months[0]}..{months[-1]}" if months else "undated"
    _append(os.path.join(PRIVATE, "provenance.csv"), ["submission_token", "ingested", "file", "provenance"],
            {"submission_token": token, "ingested": dt.date.today().isoformat(),
             "file": f"Messages chat.db ({len(rows)} msgs, {span})",
             "provenance": "author's own inbox: SMS forwarded from the author's iPhone to Messages on the "
                           "author's Mac, read by sms_imessage.py; received SMS only, iMessage and sent "
                           "messages never selected; brandname/shortcode senders as shown, numbers "
                           "reduced to a country prefix; attributable to the author"})
    _append(os.path.join(PRIVATE, "participants.csv"), ["submission_token", "participant_id"],
            {"submission_token": token, "participant_id": participant})
    shutil.rmtree(folder)
    print(f"[+] {len(rows)} row(s) -> {os.path.relpath(dest, ROOT)}; draft deleted; "
          f"token recorded as participant {participant}")
    missing = gates()
    if missing:
        print("    sms_collect.py --ingest is still gated (" + "; ".join(missing) + ").\n"
              "    Whether the author's own inbox enters the corpus is the open question of the protocol's\n"
              "    amendment of 2026-10-04; answer it there before appending.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("--db", default=DB)
    e.add_argument("--since", default=None, help="keep messages from this month on (YYYY-MM)")
    e.add_argument("--unique", action="store_true", help="drop exact repeats within the batch")
    f = sub.add_parser("finalize")
    f.add_argument("folder")
    f.add_argument("--participant", default="AUTHOR")
    a = ap.parse_args()
    return extract(a.db, a.since, a.unique) if a.cmd == "extract" else finalize(a.folder, a.participant)


if __name__ == "__main__":
    sys.exit(main())
