"""The two redaction routes must agree: redact.html on the contributor's phone and
sms_transcribe.py on the author's machine read one rules block, and are held here to one list of
cases. Run: python3 -m unittest discover tests
"""
import csv, io, json, os, shutil, subprocess, sys, tempfile, unittest, zipfile
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
import sms_transcribe as T  # noqa: E402

with open(os.path.join(HERE, "redact_cases.json"), encoding="utf-8") as _fh:
    CASES = json.load(_fh)

# Loads the page's own rules and Core block under node, without a browser, and redacts stdin.
NODE = r"""
const fs = require("fs");
const html = fs.readFileSync(process.argv[1], "utf8");
const pick = id => html.match(new RegExp('<script[^>]*id="' + id + '">([\\s\\S]*?)</script>'))[1];
const m = { exports: {} };
new Function("module", pick("core"))(m);
const Core = m.exports, rules = Core.compile(JSON.parse(pick("rules")));
const cases = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(cases.map(t => [Core.redact(t, rules), Core.problems(Core.redact(t, rules), rules).length])));
"""


class Redaction(unittest.TestCase):
    def test_python_matches_cases(self):
        rules = T.load_rules()
        for raw, want in CASES:
            with self.subTest(raw=raw):
                got = T.redact(raw, rules)
                self.assertEqual(got, want)
                self.assertEqual(T.problems(got, rules), [], "an expected output must satisfy SCHEMA.md rule 2")

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_page_matches_python(self):
        out = subprocess.run(["node", "-e", NODE, os.path.join(REPO, "redact.html")],
                             input=json.dumps([c[0] for c in CASES]), capture_output=True,
                             text=True, check=True).stdout
        for (raw, want), (got, nprob) in zip(CASES, json.loads(out)):
            with self.subTest(raw=raw):
                self.assertEqual(got, want)
                self.assertEqual(nprob, 0)

    def test_problems_catches_what_rule_2_forbids(self):
        rules = T.load_rules()
        self.assertTrue(T.problems("so 12345", rules))
        self.assertTrue(T.problems("a@b", rules))
        self.assertEqual(T.problems("Tk <ACCOUNT> luc <TIME>", rules), [])
        # Digits inside a kept link are the link's, not a leak.
        self.assertEqual(T.problems("Xem https://x.top/2027/05/nhan?id=88213", rules), [])
        self.assertTrue(T.problems("Xem https://x.top/a va goi 0912345678", rules))

    def test_links_are_kept(self):
        rules = T.load_rules()
        self.assertTrue(T.has_link("Truy cap vcb-xacminh.top ngay", rules))
        self.assertFalse(T.has_link("Tai khoan bi khoa.Xac minh ngay", rules))

    def test_broadcast_amounts_are_kept_own_money_is_masked(self):
        rules = T.load_rules()
        self.assertEqual(T.redact("Trung thuong 100.000.000d", rules), "Trung thuong 100.000.000d")
        self.assertEqual(T.redact("So du 12.345.678VND", rules), "So du <AMOUNT>")
        self.assertTrue(T.has_money("Trung thuong 100.000.000d", rules))
        self.assertTrue(T.has_money("So du <AMOUNT>", rules))
        self.assertFalse(T.has_money("Diem thi da co", rules))
        self.assertEqual(T.problems("Nap 20000d nhan qua", rules), [])


class Transcribe(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.priv = os.path.join(self.tmp, "private")
        self.p = mock.patch.object(T, "PRIVATE", self.priv)
        self.p.start()

    def tearDown(self):
        self.p.stop()
        shutil.rmtree(self.tmp)

    def _zip(self):
        from PIL import Image
        from PIL.PngImagePlugin import PngInfo
        buf = io.BytesIO()
        meta = PngInfo(); meta.add_text("Author", "someone identifiable")
        img = io.BytesIO(); Image.new("RGB", (40, 20), "white").save(img, "PNG", pnginfo=meta)
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("luadao_01.png", img.getvalue())
            z.writestr("Screenshot 2027-03-04 at 10.12.33.png", img.getvalue())
            z.writestr("../../escape.png", img.getvalue())
            z.writestr("__MACOSX/._luadao_01.png", b"junk")
            z.writestr("notes.txt", b"not an image")
        path = os.path.join(self.tmp, "sub.zip")
        with open(path, "wb") as fh:
            fh.write(buf.getvalue())
        return path

    def test_extract_then_finalize(self):
        with mock.patch.object(T, "ocr", return_value="Tai khoan 0123456789 se bi khoa. Xac minh tai abc.top"):
            T.extract(self._zip())
        (folder,) = [os.path.join(self.priv, "screenshots", d) for d in os.listdir(os.path.join(self.priv, "screenshots"))]
        files = sorted(os.listdir(folder))
        # Three images (the traversal name is read as bytes, never written where it points), renamed.
        self.assertEqual(files, ["draft.csv", "img_001.png", "img_002.png", "img_003.png"])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "escape.png")))
        from PIL import Image
        with Image.open(os.path.join(folder, "img_003.png")) as im:
            self.assertNotIn("Author", im.info, "metadata must not survive re-encoding")

        with open(os.path.join(folder, "draft.csv"), encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual([r["label_contributor"] for r in rows], ["", "", "phishing"])
        self.assertTrue(all(r["capture"] == "screenshot" for r in rows))

        # Unfilled sender_type: refused, and nothing deleted.
        with self.assertRaises(SystemExit):
            T.finalize(folder)
        self.assertTrue(os.path.exists(folder))

        for r in rows:
            r.update(sender="VCB-Bank", sender_type="brandname", received_month="2027-03")
        with open(os.path.join(folder, "draft.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        T.finalize(folder)
        self.assertFalse(os.path.exists(folder), "images and draft are deleted once finalized")
        (out,) = os.listdir(os.path.join(self.priv, "ingest"))
        with open(os.path.join(self.priv, "ingest", out), encoding="utf-8") as fh:
            got = list(csv.DictReader(fh))
        self.assertEqual(got[0]["text"], "Tai khoan <ACCOUNT> se bi khoa. Xac minh tai abc.top")
        self.assertEqual(list(got[0]), T.FIELDS)

    def test_refuses_before_approval(self):
        r = subprocess.run([sys.executable, os.path.join(REPO, "sms_transcribe.py"), "extract", "x.zip"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not permitted", r.stderr)


if __name__ == "__main__":
    unittest.main()
