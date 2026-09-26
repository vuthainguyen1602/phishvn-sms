# Dataset schema — `sms_dataset.csv`

One row per message. Every field below is in the published file; nothing else is. Fields the
project keeps privately are listed at the end, with the reason each is withheld.

## Published fields

| field | type | values | meaning |
|---|---|---|---|
| `message_id` | string | `SMS_00001`, `QAV_COM_0007` | stable identifier: `SMS_` in ingest order for contributed rows, `QAV_` plus the source corpus's own id for imported ones, so any imported row can be checked against its original |
| `text` | string | free text | the message **after redaction**; otherwise byte-for-byte as received where `capture` is `paste`, and a hand-checked OCR transcription where it is `screenshot` |
| `source` | enum | `contributed` `qavn` | which subset (PROTOCOL §1): collected under this protocol, or taken from the *Quality-Assured Vietnamese SMS Phishing Dataset* under its CC BY 4.0 licence and re-annotated here |
| `capture` | enum | `paste` `screenshot` `imported` | how the text was obtained. A study of obfuscating spellings or Unicode should use the `paste` rows only, since OCR may normalise exactly those; `imported` rows carry the source corpus's published text with its placeholder tokens mapped mechanically to this file's |
| `final_label` | enum | `legitimate` `spam` `phishing` | the adjudicated label; the only label an experiment should train on |
| `label_annotator_1` | enum | + `uncertain` | first annotator, independent |
| `label_annotator_2` | enum | + `uncertain` | second annotator, independent |
| `label_source` | enum | `benign` `scam` or empty | imported rows only: the source corpus's own binary label, shipped so the re-annotation disagreement the paper reports can be recomputed rather than believed |
| `template_id` | string | `T0031` | computed template group; every message of one template shares it |
| `sender_type` | enum | `brandname` `shortcode` `unknown` | how the sender appeared on the handset |
| `has_url` | 0/1 | | the text contains a link, as found by the link patterns in `redact.html`; the link itself is kept in `text` |
| `has_phone` | 0/1 | | contains `<PHONE>` |
| `has_otp` | 0/1 | | contains `<OTP>` |
| `has_money` | 0/1 | | the text contains an amount: a kept one, found by the amount patterns in `redact.html`, or a masked `<AMOUNT>` |
| `split` | enum | `train` `validation` `test` | the shipped template-disjoint split |

`label_annotator_1` and `label_annotator_2` ship **unmodified**, including where they disagree
and where either says `uncertain`. A reader who distrusts the adjudication can recompute from
them, and the agreement the paper reports can be checked rather than believed.

## Rules a valid file satisfies

1. `message_id` is unique.
2. `text` contains no digit run of four or more outside a placeholder, a link or an amount, and
   no `@`. Links and broadcast amounts are kept; personal data inside a link and the
   contributor's own balance and account movements are masked (PROTOCOL §3). Redaction failures are
   the one defect that cannot be repaired after publication.
3. `final_label` is never `uncertain` and never empty: a row outside the annotation queue
   (PROTOCOL §5) is not published at all.
4. Every message sharing a `template_id` shares a `split`. **This is the rule the corpus exists
   to keep**, and it is checked rather than assumed.
5. `has_*` are derived, not typed: `has_url` and `has_money` from the link and amount patterns in
   `redact.html`, the others from the presence of their placeholder in `text`.
6. `sender_type` is never a phone number: messages from personal numbers are not collected.
7. Only imported rows may carry `<NUMBER>`: the mechanical image of the source corpus's
   `[NUMBER]` and `[POINT]` tokens, which collapsed phones, shortcodes and quantities into one.
   The mapping keeps that collapse visible instead of guessing a distinction back, which is why
   `has_phone` stays 0 on such a row.

## Withheld

| field | why |
|---|---|
| `participant_id` | with a handful of contributors it is pseudonymisation, not anonymisation: someone who knows the group could read off which bank or school each uses. Kept privately so leave-one-contributor-out can be computed; the paper reports that result without the mapping. |
| raw text, screenshots | for `paste` rows the raw text never reaches the author: redaction runs on the contributor's device. For `screenshot` rows the author holds the image until its transcription is checked, then deletes it, before publication. Neither ever ships. |
| handset or SIM identifiers, dates of birth, contact names | never collected. |

## Example rows

**These messages are invented for this file.** They are not collected data, no contributor sent
them, and they exist to show the shape. `examples/EXAMPLE_synthetic.csv` holds the same rows as a file.

```
message_id,text,source,capture,final_label,label_annotator_1,label_annotator_2,label_source,template_id,sender_type,has_url,has_phone,has_otp,has_money,split
SMS_00001,Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay.,contributed,paste,legitimate,legitimate,legitimate,,T001,brandname,0,0,1,0,train
SMS_00002,Tai khoan cua quy khach se bi khoa. Xac minh tai http://vcb-xacminh.example/x7K9q,contributed,paste,phishing,phishing,phishing,,T017,brandname,1,0,0,0,test
SMS_00003,KHUYEN MAI 50% toan bo don hang. LH <PHONE>,contributed,screenshot,spam,spam,spam,,T029,shortcode,0,1,0,0,train
SMS_00004,Ban da trung thuong 100.000.000d. Goi ngay <PHONE> de nhan.,contributed,paste,phishing,phishing,spam,,T041,unknown,0,1,0,1,validation
SMS_00005,Diem thi hoc ky da co tren cong thong tin sinh vien.,contributed,paste,legitimate,legitimate,legitimate,,T006,brandname,0,0,0,0,train
SMS_00006,Tk cua ban +<AMOUNT>. So du <AMOUNT>. ND: chuyen khoan.,contributed,paste,legitimate,legitimate,legitimate,,T002,brandname,0,0,0,1,train
QAV_COM_0000,Soan KM gui <NUMBER> de nhan uu dai data cua tong dai.,qavn,imported,spam,spam,spam,benign,T054,unknown,0,0,0,0,train
```

`SMS_00004` is deliberately a disagreement: one annotator read a prize lure as `phishing`, the
other as `spam`. Adjudication made it `phishing` — there is a false pretext and a call-back, which
the guideline treats as evidence of deceptive intent. Both original labels stay in the file.

`QAV_COM_0000` is deliberately a flip: the source corpus called an operator's advert `benign`
(its boundary is genuine-sender vs scam), the re-annotation calls it `spam` (§4's boundary is the
nature of the message). Both labels ship, so the flip rate the paper reports is recomputable.
