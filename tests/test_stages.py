"""The stages after collection, held to their invariants: grouping merges what a campaign
rotates, the split never cuts a template and reproduces from its constants, agreements finalize
without an adjudicator, and the projection ships exactly SCHEMA.md's columns and nothing else.
Run: python3 -m unittest discover tests
"""
import contextlib, csv, io, os, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import sms_annotate as A    # noqa: E402
import sms_import as I      # noqa: E402
import sms_publish as P     # noqa: E402
import sms_split as S       # noqa: E402
import sms_templates as T   # noqa: E402

RULES = T.load_rules()


def _write(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        fn(*args)
    return out.getvalue()


class Templates(unittest.TestCase):
    def _jac(self, a, b):
        sa = T.shingles(T.normalize(a, RULES))
        sb = T.shingles(T.normalize(b, RULES))
        return len(sa & sb) / len(sa | sb)

    def test_rotated_url_is_one_template(self):
        # One edited character in the domain is the slot a campaign rotates, not a new template.
        self.assertGreaterEqual(self._jac(
            "Xin vui long tra tien phat giao thong: www.finepay-a.cc/vn",
            "Xin vui long tra tien phat giao thong: www.finepay-b.cc/vn"), 0.9)

    def test_rotated_short_amount_is_one_template(self):
        # 60K/128K are below the redaction amount patterns on purpose; grouping must still merge.
        self.assertGreaterEqual(self._jac(
            "Khuyen mai lon tang ban 128K cho lan nap dau tien, bonus 100%",
            "Khuyen mai lon tang ban 60K cho lan nap dau tien, bonus 100%"), 0.9)

    def test_different_messages_stay_apart(self):
        self.assertLess(self._jac(
            "Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay.",
            "Lop hoc mien phi dang ky ngay hom nay de nhan uu dai"), 0.3)

    def test_assign_writes_template_ids(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "w.csv")
            _write(p, ["text"], [
                {"text": "Xin vui long tra tien phat giao thong: www.finepay-a.cc/vn"},
                {"text": "Xin vui long tra tien phat giao thong: www.finepay-b.cc/vn"},
                {"text": "Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay."}])
            with mock.patch.object(sys, "argv", ["x", "--assign", p]):
                _quiet(T.main)
            rows = _read(p)
            self.assertEqual(rows[0]["template_id"], rows[1]["template_id"])
            self.assertNotEqual(rows[0]["template_id"], rows[2]["template_id"])


class Split(unittest.TestCase):
    def _file(self, d):
        # 20 templates, sizes 1..5, two labels: enough mass for the fractions to mean something.
        p = os.path.join(d, "w.csv")
        rows = []
        for t in range(20):
            for _ in range(t % 5 + 1):
                rows.append({"text": f"m{t}", "template_id": f"T{t:03d}",
                             "label_contributor": "phishing" if t % 2 else "spam"})
        _write(p, ["text", "template_id", "label_contributor"], rows)
        return p

    def test_template_disjoint_and_near_target(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._file(d)
            with mock.patch.object(sys, "argv", ["x", "--assign", p]):
                _quiet(S.main)
            rows = _read(p)
            per_tpl = {}
            for r in rows:
                per_tpl.setdefault(r["template_id"], set()).add(r["split"])
            for t, splits in per_tpl.items():
                self.assertEqual(len(splits), 1, f"{t} crosses a split boundary")
            n = len(rows)
            frac = {s: sum(r["split"] == s for r in rows) / n for s in S.FRACTIONS}
            self.assertGreater(frac["train"], 0.6)
            for s in ("validation", "test"):
                self.assertGreater(frac[s], 0.08)
            self.assertEqual(set(frac), {"train", "validation", "test"})

    def test_reproducible_from_constants(self):
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = self._file(d), None
            d2 = os.path.join(d, "again")
            os.makedirs(d2)
            p2 = self._file(d2)
            for p in (p1, p2):
                with mock.patch.object(sys, "argv", ["x", "--assign", p]):
                    _quiet(S.main)
            self.assertEqual([r["split"] for r in _read(p1)],
                             [r["split"] for r in _read(p2)])


class Annotate(unittest.TestCase):
    def _submissions(self, d):
        p = os.path.join(d, "sub.csv")
        from sms_collect import FIELDS
        rows = [{f: "" for f in FIELDS} | {"submission_token": tok, "text": f"t{i}",
                                           "capture": "screenshot", "sender_type": "unknown",
                                           "label_contributor": "spam", "redaction_reviewed": "1"}
                for i, tok in enumerate(["za", "za", "zb"])]
        _write(p, FIELDS, rows)
        return p

    def test_init_ids_map_and_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            w = os.path.join(d, "working.csv")
            m = os.path.join(d, "map.csv")
            _write(m, ["submission_token", "participant_id"],
                   [{"submission_token": "za", "participant_id": "P001"},
                    {"submission_token": "zb", "participant_id": "P001"}])
            with mock.patch.object(A, "WORKING", w):
                _quiet(A.init, self._submissions(d), m)
                rows = _read(w)
                self.assertEqual([r["message_id"] for r in rows],
                                 ["SMS_00001", "SMS_00002", "SMS_00003"])
                self.assertEqual({r["participant_id"] for r in rows}, {"P001"})
                with self.assertRaises(SystemExit):
                    A.init(self._submissions(d), m)  # labels would be lost; must refuse

    def test_agreements_finalize_without_adjudicator(self):
        with tempfile.TemporaryDirectory() as d:
            w = os.path.join(d, "working.csv")
            rows = [{f: "" for f in A.W_FIELDS} | {"message_id": f"SMS_0000{i}", "text": "t",
                                                   "label_annotator_1": lab,
                                                   "label_annotator_2": lab}
                    for i, lab in enumerate(["spam", "phishing"], start=1)]
            _write(w, A.W_FIELDS, rows)
            with mock.patch.object(A, "WORKING", w):
                _quiet(A.adjudicate, "nobody")
            rows = _read(w)
            self.assertEqual([r["final_label"] for r in rows], ["spam", "phishing"])
            self.assertEqual([r["adjudicated_by"] for r in rows], ["", ""])

    def test_report_kappa(self):
        # 4 rows, 3 agreements: po = 0.75, pe = (2*3 + 2*1)/16 = 0.5, kappa = 0.5.
        with tempfile.TemporaryDirectory() as d:
            w = os.path.join(d, "working.csv")
            pairs = [("phishing", "phishing"), ("phishing", "phishing"),
                     ("spam", "spam"), ("spam", "phishing")]
            rows = [{f: "" for f in A.W_FIELDS} | {"message_id": f"SMS_0000{i}", "text": "t",
                                                   "label_annotator_1": a, "label_annotator_2": b}
                    for i, (a, b) in enumerate(pairs, start=1)]
            _write(w, A.W_FIELDS, rows)
            with mock.patch.object(A, "WORKING", w):
                out = _quiet(A.report)
            self.assertIn("kappa (before adjudication): 0.500", out)
            self.assertIn("sent to adjudication: 1 (25.0%)", out)


class RedactBoundary(unittest.TestCase):
    def test_vietnamese_letter_does_not_end_an_amount_unit(self):
        # "0004100000779007 Trần" once read as digit-run + unit "tr" because the lookahead
        # excluded only ASCII letters: the account number slipped rule 2 behind a person's name.
        from sms_transcribe import problems
        self.assertTrue(problems("ck giup e nha, ocb 0004100000779007 Trần thị thu vân", RULES))
        for kept in ("Nap 500k nhan uu dai", "Chi 5.000d/ngay", "Vay den 20 trieu"):
            self.assertEqual(problems(kept, RULES), [], kept)


class Import(unittest.TestCase):
    def test_token_mapping_is_an_allowlist(self):
        # PII tokens map; [TB]/[QC] and brand prefixes are message text and must survive.
        self.assertEqual(I.convert("[TB] Tang [MONEY] ngay [DATE], soan KM gui [NUMBER]"),
                         "[TB] Tang <AMOUNT> ngay <DATE>, soan KM gui <NUMBER>")

    def test_append_skip_and_rerun_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            w, src = os.path.join(d, "working.csv"), os.path.join(d, "src.csv")
            _write(w, A.W_FIELDS, [{f: "" for f in A.W_FIELDS}
                                   | {"message_id": "SMS_00001", "text": "t"}])
            _write(src, ["message_id", "date", "message", "label"], [
                {"message_id": "COM_1", "date": "28/05/2026",
                 "message": "Tang [MONEY] khi soan KM gui 191", "label": "0"},
                {"message_id": "COM_2", "date": "",
                 "message": "Ma OTP la 066595", "label": "0"}])  # rule 2: dropped, not repaired
            with mock.patch.object(I, "WORKING", w), \
                 mock.patch.object(sys, "argv", ["x", src]):
                out = _quiet(I.main)
            rows = _read(w)
            self.assertEqual([r["message_id"] for r in rows], ["SMS_00001", "QAV_COM_1"])
            imported = rows[1]
            self.assertEqual(imported["text"], "Tang <AMOUNT> khi soan KM gui 191")
            self.assertEqual((imported["source"], imported["capture"], imported["label_source"],
                              imported["received_month"], imported["participant_id"]),
                             ("qavn", "imported", "benign", "2026-05", ""))
            self.assertIn("COM_2", out)
            with mock.patch.object(I, "WORKING", w), \
                 mock.patch.object(sys, "argv", ["x", src]), self.assertRaises(SystemExit):
                _quiet(I.main)  # appending twice would duplicate the subset


class Publish(unittest.TestCase):
    def _row(self, i, text, **kw):
        return ({f: "" for f in A.W_FIELDS}
                | {"message_id": f"SMS_0000{i}", "text": text, "capture": "paste",
                   "sender_type": "unknown", "final_label": "phishing",
                   "label_annotator_1": "phishing", "label_annotator_2": "phishing",
                   "template_id": f"T00{i}", "split": "train"} | kw)

    def test_projection_and_derived_flags(self):
        with tempfile.TemporaryDirectory() as d:
            w, out = os.path.join(d, "w.csv"), os.path.join(d, "out.csv")
            _write(w, A.W_FIELDS, [
                self._row(1, "Ma OTP la <OTP>. Xem tai http://x.example/a"),
                self._row(2, "Goi <PHONE> nhan ngay 1.880.000 VND", final_label="spam",
                          label_annotator_1="spam", label_annotator_2="spam", split="test")])
            with mock.patch.object(sys, "argv", ["x", w, "--out", out]):
                _quiet(P.main)
            rows = _read(out)
            self.assertEqual(list(rows[0]), P.PUB_FIELDS)  # nothing else ships
            self.assertEqual([rows[0][f] for f in ("has_url", "has_otp", "has_phone", "has_money")],
                             ["1", "1", "0", "0"])
            self.assertEqual([rows[1][f] for f in ("has_url", "has_otp", "has_phone", "has_money")],
                             ["0", "0", "1", "1"])

    def test_refuses_holes(self):
        for hole in ({"final_label": "uncertain"}, {"template_id": ""}, {"split": "dev"}):
            with tempfile.TemporaryDirectory() as d:
                w, out = os.path.join(d, "w.csv"), os.path.join(d, "out.csv")
                _write(w, A.W_FIELDS, [self._row(1, "t", **hole)])
                with mock.patch.object(sys, "argv", ["x", w, "--out", out]), \
                     self.assertRaises(SystemExit):
                    _quiet(P.main)
                self.assertFalse(os.path.exists(out), f"published despite {hole}")


if __name__ == "__main__":
    unittest.main()
