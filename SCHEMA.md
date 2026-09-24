# Dataset schema — `sms_dataset.csv`

One row per message. Every field below is in the published file; nothing else is. Fields the
project keeps privately are listed at the end, with the reason each is withheld.

## Published fields

| field | type | values | meaning |
|---|---|---|---|
| `message_id` | string | `SMS_00001` | stable identifier, assigned in ingest order and never reused |
| `text` | string | free text | the message **after redaction**, otherwise byte-for-byte as received |
| `final_label` | enum | `legitimate` `spam` `phishing` | the adjudicated label; the only label an experiment should train on |
| `label_annotator_1` | enum | + `uncertain` | first annotator, independent |
| `label_annotator_2` | enum | + `uncertain` | second annotator, independent |
| `template_id` | string | `T0031` | computed template group; every message of one template shares it |
| `sender_type` | enum | `brandname` `shortcode` `unknown` | how the sender appeared on the handset |
| `has_url` | 0/1 | | the redacted text contains `<URL>` |
| `has_phone` | 0/1 | | contains `<PHONE>` |
| `has_otp` | 0/1 | | contains `<OTP>` |
| `has_money` | 0/1 | | contains `<AMOUNT>` |
| `split` | enum | `train` `validation` `test` | the shipped template-disjoint split |

`label_annotator_1` and `label_annotator_2` ship **unmodified**, including where they disagree
and where either says `uncertain`. A reader who distrusts the adjudication can recompute from
them, and the agreement the paper reports can be checked rather than believed.

## Rules a valid file satisfies

1. `message_id` is unique.
2. `text` contains no digit run of four or more outside a placeholder, no `@`, and no `http`.
   Redaction failures are the one defect that cannot be repaired after publication.
3. `final_label` is never `uncertain`.
4. Every message sharing a `template_id` shares a `split`. **This is the rule the corpus exists
   to keep**, and it is checked rather than assumed.
5. `has_*` equals the presence of its placeholder in `text`; they are derived, not typed.
6. `sender_type` is never a phone number: messages from personal numbers are not collected.

## Withheld

| field | why |
|---|---|
| `participant_id` | with a handful of contributors it is pseudonymisation, not anonymisation: someone who knows the group could read off which bank or school each uses. Kept privately so leave-one-contributor-out can be computed; the paper reports that result without the mapping. |
| raw text | deleted once the redacted corpus is fixed. It never reaches the author in the first place: redaction runs on the contributor's device. |
| handset or SIM identifiers, dates of birth, contact names | never collected. |

## Example rows

**These messages are invented for this file.** They are not collected data, no contributor sent
them, and they exist to show the shape. `EXAMPLE_synthetic.csv` holds the same rows as a file.

```
message_id,text,final_label,label_annotator_1,label_annotator_2,template_id,sender_type,has_url,has_phone,has_otp,has_money,split
SMS_00001,Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay.,legitimate,legitimate,legitimate,T001,brandname,0,0,1,0,train
SMS_00002,Tai khoan cua quy khach se bi khoa. Xac minh tai <URL>,phishing,phishing,phishing,T017,brandname,1,0,0,0,test
SMS_00003,KHUYEN MAI 50% toan bo don hang. LH <PHONE>,spam,spam,spam,T029,shortcode,0,1,0,0,train
SMS_00004,Ban da trung thuong <AMOUNT>. Goi ngay <PHONE> de nhan.,phishing,phishing,spam,T041,unknown,0,1,0,1,validation
SMS_00005,Diem thi hoc ky da co tren cong thong tin sinh vien.,legitimate,legitimate,legitimate,T006,brandname,0,0,0,0,train
SMS_00006,Tk cua ban +<AMOUNT>. So du <AMOUNT>. ND: chuyen khoan.,legitimate,legitimate,legitimate,T002,brandname,0,0,0,1,train
```

`SMS_00004` is deliberately a disagreement: one annotator read a prize lure as `phishing`, the
other as `spam`. Adjudication made it `phishing` — there is a false pretext and a call-back, which
the guideline treats as evidence of deceptive intent. Both original labels stay in the file.
