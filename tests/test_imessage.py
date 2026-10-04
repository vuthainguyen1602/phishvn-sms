"""The author's-inbox route: only received SMS leave chat.db, the typedstream body decodes, senders
reduce the way the community batch did, and finalize refuses what rule 2 forbids.
Run: python3 -m unittest discover tests
"""
import contextlib, csv, io, os, sqlite3, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
import sms_imessage as I  # noqa: E402

NS = 10 ** 9
T0 = (24 * 365 * 86400) * NS  # some day in 2025, Apple epoch, nanoseconds


def body(text: str) -> bytes:
    """An attributedBody the way Messages archives it: the NSString marker, the '+' tag, a length."""
    raw = text.encode("utf-8")
    ln = bytes([len(raw)]) if len(raw) < 0x81 else b"\x81" + len(raw).to_bytes(2, "little")
    return b"\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x12NSAttributedString\x00\x84\x84\x08NSObject\x00\x85\x92\x84\x84\x84\x08NSString\x01\x94\x84\x01+" + ln + raw + b"\x86\x84\x02iI\x01"


def chat_db(path: str, rows) -> None:
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE handle (ROWID INTEGER PRIMARY KEY, id TEXT)")
    con.execute("CREATE TABLE message (ROWID INTEGER PRIMARY KEY, text TEXT, attributedBody BLOB, "
                "handle_id INTEGER, service TEXT, is_from_me INTEGER, date INTEGER)")
    handles = {}
    for handle, text, blob, service, from_me, date in rows:
        if handle not in handles:
            con.execute("INSERT INTO handle (id) VALUES (?)", (handle,))
            handles[handle] = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.execute("INSERT INTO message (text, attributedBody, handle_id, service, is_from_me, date) "
                    "VALUES (?,?,?,?,?,?)", (text, blob, handles[handle], service, from_me, date))
    con.commit()
    con.close()


class Decode(unittest.TestCase):
    def test_short_and_long_bodies(self):
        self.assertEqual(I.decode_body(body("Ma OTP cua ban la 482913")), "Ma OTP cua ban la 482913")
        long = "Khuyen mai " * 30
        self.assertEqual(I.decode_body(body(long)), long)
        self.assertEqual(I.decode_body(None), "")
        self.assertEqual(I.decode_body(b"no marker here"), "")

    def test_attachment_slot_is_not_text(self):
        self.assertEqual(I.clean("￼  Xem anh"), "Xem anh")

    def test_sender_shapes(self):
        self.assertEqual(I.sender("MobiFone"), ("MobiFone", "brandname", ""))
        self.assertEqual(I.sender("999"), ("999", "shortcode", ""))
        self.assertEqual(I.sender("+9221"), ("+9221", "shortcode", ""))
        self.assertEqual(I.sender("+84912345678"), ("+84-mobile", "unknown", "personal number"))
        self.assertEqual(I.sender("0912345678"), ("+84-mobile", "unknown", "personal number"))
        self.assertEqual(I.sender("+855123456789"), ("+855-mobile", "unknown", "personal number"))
        self.assertEqual(I.sender("+212612345678"), ("+212-mobile", "unknown", "personal number"))

    def test_month_from_nanoseconds_and_seconds(self):
        self.assertRegex(I.month(T0), r"^\d{4}-\d{2}$")
        self.assertEqual(I.month(T0), I.month(T0 // NS))
        self.assertEqual(I.month(None), "")


class Route(unittest.TestCase):
    def run_extract(self, d, rows, known=(), **kw):
        db = os.path.join(d, "chat.db")
        chat_db(db, rows)
        private = os.path.join(d, "private")
        sub = os.path.join(d, "submissions.csv")
        with open(sub, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=I.FIELDS)
            w.writeheader()
            for t in known:
                w.writerow({"submission_token": "zold", "text": t, "capture": "paste", "sender": "X",
                            "sender_type": "brandname", "received_month": "", "label_contributor": "spam",
                            "redaction_reviewed": 1})
        out = io.StringIO()
        with mock.patch.object(I, "PRIVATE", private), mock.patch.object(I, "SUBMISSIONS", sub), \
                contextlib.redirect_stdout(out):
            I.extract(db, kw.get("since"), kw.get("unique", False))
        (token,) = os.listdir(os.path.join(private, "imessage"))
        with open(os.path.join(private, "imessage", token, "draft.csv"), newline="", encoding="utf-8") as fh:
            draft = list(csv.DictReader(fh))
        return private, token, draft, out.getvalue()

    ROWS = [
        ("VietinBank", None, body("Ma OTP cua ban la 482913. Khong chia se."), "SMS", 0, T0),
        ("999", "KM 50% data, soan DK gui 999 hoac vao mobifone.vn/km", None, "SMS", 0, T0 + NS),
        ("999", "KM 50% data, soan DK gui 999 hoac vao mobifone.vn/km", None, "SMS", 0, T0 + 2 * NS),
        ("+84912345678", "Toi den roi, xuong nhe", None, "SMS", 0, T0 + 3 * NS),
        ("+84912345678", "Ok em", None, "SMS", 1, T0 + 4 * NS),                 # sent: never selected
        ("friend@icloud.com", "chuyen rieng", None, "iMessage", 0, T0 + 5 * NS),  # iMessage: never selected
        ("CucThue", "Da co trong corpus roi", None, "SMS", 0, T0 + 6 * NS),
        ("MMS", None, body("￼"), "SMS", 0, T0 + 7 * NS),                  # an attachment, no text
    ]

    def test_only_received_sms_and_dedupe_against_corpus(self):
        with tempfile.TemporaryDirectory() as d:
            _, _, draft, log = self.run_extract(d, self.ROWS, known=["Da co trong corpus roi"])
            texts = [r["text"] for r in draft]
            self.assertNotIn("Ok em", texts)
            self.assertNotIn("chuyen rieng", texts)
            self.assertNotIn("Da co trong corpus roi", texts)
            self.assertEqual(len(draft), 4)                        # OTP, KM ×2, the personal number
            otp = next(r for r in draft if r["sender"] == "VietinBank")
            self.assertEqual(otp["sender_type"], "brandname")
            self.assertEqual(otp["preview"], "Ma OTP cua ban la <OTP>. Khong chia se.")
            self.assertEqual(otp["problems"], "")
            self.assertRegex(otp["received_month"], r"^\d{4}-\d{2}$")
            km = [r for r in draft if r["sender"] == "999"]
            self.assertEqual({r["sender_type"] for r in km}, {"shortcode"})
            self.assertIn("mobifone.vn/km", km[0]["preview"])      # the link is kept
            person = next(r for r in draft if r["text"] == "Toi den roi, xuong nhe")
            self.assertEqual((person["sender"], person["sender_type"], person["problems"]),
                             ("+84-mobile", "unknown", "personal number"))
            self.assertIn("1 with no text, 1 already in submissions.csv, 1 exact repeat", log)
            self.assertTrue(all(r["capture"] == "paste" and r["redaction_reviewed"] == "1" for r in draft))

    def test_unique_and_since(self):
        with tempfile.TemporaryDirectory() as d:
            _, _, draft, _ = self.run_extract(d, self.ROWS, unique=True)
            self.assertEqual(sum(r["sender"] == "999" for r in draft), 1)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(SystemExit):           # an empty batch is refused, not written
                self.run_extract(d, self.ROWS, since="2099-01")

    def test_finalize_writes_ingest_and_records_the_token(self):
        with tempfile.TemporaryDirectory() as d:
            private, token, draft, _ = self.run_extract(d, self.ROWS)
            folder = os.path.join(private, "imessage", token)
            # The hand check: the author drops the person who texted them.
            draft = [r for r in draft if r["problems"] != "personal number"]
            draft[0]["label_contributor"] = "legitimate"
            with open(os.path.join(folder, "draft.csv"), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=I.DRAFT_FIELDS)
                w.writeheader()
                w.writerows(draft)
            out = io.StringIO()
            with mock.patch.object(I, "PRIVATE", private), contextlib.redirect_stdout(out):
                I.finalize(folder, "AUTHOR")
            self.assertFalse(os.path.exists(folder))
            with open(os.path.join(private, "ingest", f"{token}.csv"), newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 4)                         # OTP, KM ×2, CucThue
            self.assertEqual(list(rows[0].keys()), I.FIELDS)
            self.assertEqual(rows[0]["text"], "Ma OTP cua ban la <OTP>. Khong chia se.")
            self.assertEqual(rows[0]["label_contributor"], "legitimate")
            with open(os.path.join(private, "participants.csv"), newline="", encoding="utf-8") as fh:
                self.assertEqual(list(csv.DictReader(fh)), [{"submission_token": token, "participant_id": "AUTHOR"}])
            with open(os.path.join(private, "provenance.csv"), newline="", encoding="utf-8") as fh:
                (prov,) = list(csv.DictReader(fh))
            self.assertEqual(prov["submission_token"], token)
            self.assertIn("4 msgs", prov["file"])
            self.assertIn("author's own inbox", prov["provenance"])

    def test_finalize_refuses_a_leak_and_a_bad_label(self):
        with tempfile.TemporaryDirectory() as d:
            private, token, draft, _ = self.run_extract(d, self.ROWS)
            folder = os.path.join(private, "imessage", token)
            draft[0]["text"] = "Goi lai so 0912345678 hoac ghe nha 123456789 Le Loi"
            draft[1]["label_contributor"] = "scam"
            with open(os.path.join(folder, "draft.csv"), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=I.DRAFT_FIELDS)
                w.writeheader()
                w.writerows(draft)
            with mock.patch.object(I, "PRIVATE", private):
                with self.assertRaises(SystemExit) as cm:
                    I.finalize(folder, "AUTHOR")
            self.assertIn("row 2", str(cm.exception))
            self.assertIn("label_contributor", str(cm.exception))
            self.assertTrue(os.path.exists(os.path.join(folder, "draft.csv")))  # nothing deleted
            self.assertFalse(os.path.exists(os.path.join(private, "ingest", f"{token}.csv")))


if __name__ == "__main__":
    unittest.main()
