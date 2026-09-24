# Private schemas — the two files that never ship

`SCHEMA.md` describes `sms_dataset.csv`, the published file. Two files exist before it, and
neither is published. They are documented here because a corpus whose private stages are
undocumented cannot be audited by the person who built it a year later, and because the published
file is produced from the second one by dropping columns — a step that has to be mechanical.

Both live under `data/`, which is gitignored in full. Nothing in this section is ever committed,
deposited or attached to the article.

---

## 1. The submission file — what leaves the contributor's device

One file per submission, written by the redaction tool on the contributor's own phone or laptop.
This is the first thing the author ever sees; the unredacted message does not exist outside the
contributor's device.

| field | type | meaning |
|---|---|---|
| `submission_token` | string | random, generated per submission. **Not per person**: a contributor who sends twice produces two unrelated tokens, so submissions cannot be joined into a profile. |
| `text` | string | the message after redaction, reviewed and approved by the contributor |
| `sender` | string | the sender name or shortcode as displayed on the handset |
| `sender_type` | enum | `brandname` `shortcode` `unknown` — never a personal number, which is not collected |
| `received_at` | date | the date only, no time: a timestamp plus a sender narrows who a contributor is |
| `label_contributor` | enum | `legitimate` `spam` `phishing` — what the contributor thought it was |
| `redaction_reviewed` | 0/1 | the contributor confirmed they read the redacted text before sending. A row with `0` is not ingested. |

The contributor's own label is **not** one of the two annotator labels. It is kept as a third
opinion and reported only as a rate of agreement with the adjudicated label — a contributor
labels their own inbox knowing the context, which is exactly the knowledge an annotator lacks.

## 2. The working file — what the author holds

`data/private/sms_working.csv`. The submission rows plus everything added afterwards.

| field | added by | meaning |
|---|---|---|
| `message_id` | ingest | `SMS_00001`, assigned in ingest order |
| `participant_id` | ingest | `P001`. **The reason this file is private.** |
| *(all submission fields)* | | carried through unchanged |
| `label_annotator_1` | annotation | independent |
| `label_annotator_2` | annotation | independent |
| `adjudicated_by` | adjudication | who decided, where the two disagreed or either said `uncertain` |
| `adjudication_note` | adjudication | one line of reasoning, for the hard cases |
| `final_label` | adjudication | |
| `template_id` | grouping | computed |
| `split` | splitting | assigned per template, never per message |

`adjudication_note` never ships: it quotes the message and sometimes reasons about the sender.

## 3. The projection — how the published file is produced

Mechanically, by dropping columns. No value is edited in this step, and nothing is added.

```
sms_working.csv                          sms_dataset.csv
──────────────────────────────────────   ───────────────
message_id                            →  message_id
text                                  →  text
final_label                           →  final_label
label_annotator_1, label_annotator_2  →  (both, unchanged)
template_id, sender_type, split       →  (unchanged)
has_url, has_phone, has_otp, has_money   derived from text
──────────────────────────────────────   ───────────────
participant_id                        ✗  pseudonymisation with few contributors
submission_token                      ✗  links a contributor's submissions to each other
sender                                ✗  a rare brandname narrows who receives it
received_at                           ✗  a date plus a sender narrows it further
label_contributor                     ✗  the contributor's own reading of their own inbox
adjudicated_by, adjudication_note     ✗  quotes messages, reasons about senders
redaction_reviewed                    ✗  a process flag, not data
```

Four of the dropped columns are dropped for the same reason and it is worth saying once:
**with a handful of contributors, almost any column that varies per person is identifying.** The
question is not whether a field contains a name — none of them does — but whether somebody who
knows the group could use it to work out whose messages they are reading.

## 4. Example rows

Invented, as in `SCHEMA.md`. Nobody sent these. They are the same six messages as
`EXAMPLE_synthetic.csv`, one stage earlier: `EXAMPLE_submission_synthetic.csv` and
`EXAMPLE_working_synthetic.csv` hold them as files, and dropping the columns of §3 from the working
file gives the published example exactly.

**A submission file** (first two rows):

```
submission_token,text,sender,sender_type,received_at,label_contributor,redaction_reviewed
s7f3a91c,Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay.,VCB,brandname,2027-03-04,legitimate,1
s7f3a91c,Tai khoan cua quy khach se bi khoa. Xac minh tai <URL>,VCB-Bank,brandname,2027-03-04,phishing,1
```

**The working file, after annotation and adjudication** (first two rows):

```
message_id,participant_id,submission_token,text,sender,sender_type,received_at,label_contributor,redaction_reviewed,label_annotator_1,label_annotator_2,adjudicated_by,adjudication_note,final_label,template_id,split
SMS_00001,P001,s7f3a91c,Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay.,VCB,brandname,2027-03-04,legitimate,1,legitimate,legitimate,,,legitimate,T001,train
SMS_00002,P001,s7f3a91c,Tai khoan cua quy khach se bi khoa. Xac minh tai <URL>,VCB-Bank,brandname,2027-03-04,phishing,1,phishing,phishing,,,phishing,T017,test
```

Note the second row's sender: `VCB-Bank` against the real `VCB`. That is the kind of detail
`sender` carries and the published file drops — useful to the author while adjudicating, and a
narrowing field once it is public.

## 5. What happens to these files

The submission files are deleted once ingest is verified. The working file is kept by the author
for as long as the article is under review, so a reviewer's question about a label can be
answered, and is deleted when the article is published. Neither is deposited.
