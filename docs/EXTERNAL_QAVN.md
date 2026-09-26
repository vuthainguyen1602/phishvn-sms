# The external benchmark — provenance and version pin

The external test set (PROTOCOL §7) is a third party's published corpus, used here unchanged in
label and held out of training. A data article that evaluates on someone else's dataset has to say
*which* copy of it, to the byte, or the number it reports cannot be reproduced. This file is that
pin.

## Identity

| | |
|---|---|
| **Name** | Vietnamese Quality-Assured SMS Scam Dataset (Official Release) — *pretty_name:* Quality-Assured Vietnamese SMS Phishing Dataset |
| **Authors** | Tran Nguyen Thai Tuan (lead), Le Hoang Khang, Nguyen Minh Tai, Nguyen Van Thang, Mai Hoang Dinh (advisor) |
| **Licence** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Label reference** | the authors credit Team Chống Lừa Đảo's list of ~50,000 malicious URLs as their labelling reference |

**Citation** (the accompanying paper, as the dataset's own README gives it):

```bibtex
@article{tuan2026vietnamese_sms_phishing,
  title={Vietnamese SMS Dataset with Quality Assurance},
  author={Tran, Nguyen Thai Tuan and Le, Hoang Khang and Nguyen, Minh Tai and Nguyen, Van Thang and Mai, Hoang Dinh},
  journal={IEEE Access},
  year={2026}
}
```

## Version pin

No repository revision hash was captured when the copy was obtained, so the pin is the file's
**content hash** — the robust anchor regardless of where it is re-downloaded. A copy reproduces
this project's external benchmark **only if its `full_dataset.csv` has the SHA-256 below**.

| | |
|---|---|
| **File pinned** | `full_dataset.csv` |
| **SHA-256** | `8a29d50a6335c8938b8beef0a3daf57d276e880244394da453bc656f5a4c7847` |
| **Records** | 2,991 total — 2,193 `benign` (label 0), 798 `scam` (label 1) |
| *(the authors' own split, not used here)* | `train.csv` 2,394 · `test.csv` 597 |
| **Copy obtained** | 2026-08 (local file timestamp; exact download date not recorded) |
| **Source URL** | `https://huggingface.co/datasets/trannguyenthaituan/vietnamese_sms_dataset` |
| **Revision** | *not recorded; the SHA-256 above pins the exact `full_dataset.csv` regardless* |

Verify a copy before use:

```
shasum -a 256 full_dataset.csv
# must print: 8a29d50a6335c8938b8beef0a3daf57d276e880244394da453bc656f5a4c7847
```

## What this project does to it, and does not

- **Does not** relabel it: its `label` (0/1) is kept as `label_source` (`benign`/`scam`) and is the
  evaluation label (PROTOCOL §7). This project's three-class scheme is never imposed on it.
- **Maps** its placeholder tokens to this corpus's, mechanically, by the allowlist in
  `scripts/sms_import.py` (`[MONEY]`→`<AMOUNT>` and so on); `[TB]`/`[QC]` and brand prefixes are
  message text and are left alone.
- **Drops** rows that still fail SCHEMA.md rule 2 after mapping — 315 of 2,991 in this copy, most
  carrying an unmasked one-time code — counted, named by `sms_import.py`, never repaired. So the
  benchmark loaded here is **2,676 rows** (1,907 `benign`, 769 `scam`).
- **Holds it out**: every row is `split = external`, never in train/validation/test; a
  template-grouping check confirms no external template coincides with a training template.

## Reproduce

```
python3 scripts/sms_annotate.py init --map data/private/participants.csv
python3 scripts/sms_import.py <path>/full_dataset.csv   # the file whose SHA-256 matches above
python3 scripts/sms_templates.py --assign data/private/sms_working.csv
python3 scripts/sms_split.py --assign data/private/sms_working.csv
python3 scripts/sms_publish.py            # -> data/sms_external_qavn.csv
```
