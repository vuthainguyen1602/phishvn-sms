# Private schemas — the two files that never ship

`SCHEMA.md` describes `sms_dataset.csv`, the published file. Two files exist before it, and
neither is published. They are documented here because a corpus whose private stages are
undocumented cannot be audited by the person who built it a year later, and because the published
file is produced from the second one by dropping columns — a step that has to be mechanical.

Both live under `data/`, which is gitignored in full. Nothing in this section is ever committed,
deposited or attached to the article.

---

## 1. The submission file — what leaves the contributor's device

One file per submission. A message arrives by one of two routes (`CONTRIBUTE_vi.md`), and the
`capture` field records which:

- **`paste`** — the contributor copied the message into the redaction page on their own phone,
  reviewed the redacted text, and the page wrote this row. The unredacted message does not exist
  outside the contributor's device.
- **`screenshot`** — for a message that cannot be copied, the contributor cropped a screenshot to
  the sender and the message, blacked out their own details on the image, and sent the images in a
  `.zip`. **The author sees the image as sent**, including anything not blacked out; the consent
  form says so. The author strips file names and image metadata on receipt, transcribes each image
  by OCR, corrects the transcription by hand against the image, applies the same redaction as the
  page, and writes this row. `received_month` comes from the image where it shows a date, and is
  left empty otherwise.

| field | type | meaning |
|---|---|---|
| `submission_token` | string | random, generated per submission. **Not per person**: a contributor who sends twice produces two unrelated tokens, so submissions cannot be joined into a profile. |
| `text` | string | the message after redaction. For `paste`, reviewed and approved by the contributor, character for character as received. For `screenshot`, a hand-checked OCR transcription: obfuscating spellings, homoglyphs and spacing may not survive it. |
| `capture` | enum | `paste` `screenshot` — how the text was obtained, and so how far it can be trusted character by character |
| `sender` | string | the sender name or shortcode as displayed on the handset |
| `sender_type` | enum | `brandname` `shortcode` `unknown` — never a personal number, which is not collected |
| `received_month` | `YYYY-MM` or empty | the month only: a date, and still more a time, plus a sender narrows who a contributor is. The month is enough to state the collection window, and it is what a contributor can recall without looking the message up. |
| `label_contributor` | enum | `legitimate` `spam` `phishing` — what the contributor thought it was |
| `redaction_reviewed` | 0/1 | the contributor confirmed they reviewed what they sent: the redacted text for `paste`, the cropped and blacked-out image for `screenshot`. A row with `0` is not ingested. |

The contributor's own label is **not** one of the two annotator labels. It is kept as a third
opinion and reported only as a rate of agreement with the adjudicated label — a contributor
labels their own inbox knowing the context, which is exactly the knowledge an annotator lacks.

## 2. The working file — what the author holds

`data/private/sms_working.csv`. The submission rows plus everything added afterwards.

| field | added by | meaning |
|---|---|---|
| `message_id` | ingest / import | `SMS_00001` in ingest order; `QAV_` plus the source corpus's id for imported rows |
| `participant_id` | ingest | `P001`. **The reason this file is private.** Empty on imported rows, which have no contributor. |
| `source` | ingest / import | `contributed`, or the imported corpus's tag (`qavn`) — PROTOCOL §1 |
| *(all submission fields)* | | carried through unchanged; an imported row fills only `text`, `capture` (`imported`) and `sender_type` (`unknown`) |
| `label_source` | import | imported rows only: the source corpus's own binary label, shown to the adjudicator and never to an annotator |
| `queued` | ingest / import | 1 if the row is in the annotation queue (PROTOCOL §5): every contributed row, every imported scam row, a seeded sample of imported benign rows. A 0 row is never labelled and never ships. |
| `label_ai` | pre-annotation | optional machine guess at the label, shown to the adjudicator as a third opinion, never to an annotator; not counted in kappa, not shipped (§5) |
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
source                                →  source
final_label                           →  final_label
label_annotator_1, label_annotator_2  →  (both, unchanged)
label_source                          →  (unchanged: already public, ships so the
                                          re-annotation disagreement is recomputable)
template_id, sender_type, split       →  (unchanged)
capture                               →  (unchanged)
has_url, has_phone, has_otp, has_money   derived from text
──────────────────────────────────────   ───────────────
participant_id                        ✗  pseudonymisation with few contributors
submission_token                      ✗  links a contributor's submissions to each other
sender                                ✗  a rare brandname narrows who receives it
received_month                        ✗  a month plus a sender still narrows it
label_contributor                     ✗  the contributor's own reading of their own inbox
adjudicated_by, adjudication_note     ✗  quotes messages, reasons about senders
redaction_reviewed                    ✗  a process flag, not data
queued                                ✗  a process flag too; its public trace is the count of
                                         rows the projection reports leaving out
label_ai                              ✗  a machine pre-annotation aid, never a shipped label
```

Four of the dropped columns are dropped for the same reason and it is worth saying once:
**with a handful of contributors, almost any column that varies per person is identifying.** The
question is not whether a field contains a name — none of them does — but whether somebody who
knows the group could use it to work out whose messages they are reading.

## 4. Example rows

Invented, as in `SCHEMA.md`. Nobody sent these. They are the same messages as
`examples/EXAMPLE_synthetic.csv`, one stage earlier: `examples/EXAMPLE_submission_synthetic.csv`
holds the six contributed ones as a submission file (the imported row never was a submission),
`examples/EXAMPLE_working_synthetic.csv` holds all seven as the working file, and the published
example is produced from it by `scripts/sms_publish.py`, not by hand.

**A submission file** (first two rows):

```
submission_token,text,capture,sender,sender_type,received_month,label_contributor,redaction_reviewed
s7f3a91c,Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay.,paste,VCB,brandname,2027-03,legitimate,1
s7f3a91c,Tai khoan cua quy khach se bi khoa. Xac minh tai http://vcb-xacminh.example/x7K9q,paste,VCB-Bank,brandname,2027-03,phishing,1
```

**The working file, after annotation and adjudication** (first two rows):

```
message_id,participant_id,source,submission_token,text,capture,sender,sender_type,received_month,label_contributor,redaction_reviewed,label_source,queued,label_ai,label_annotator_1,label_annotator_2,adjudicated_by,adjudication_note,final_label,template_id,split
SMS_00001,P001,contributed,s7f3a91c,Ma OTP giao dich cua quy khach la <OTP>. Khong chia se ma nay.,paste,VCB,brandname,2027-03,legitimate,1,,1,,legitimate,legitimate,,,legitimate,T001,train
SMS_00002,P001,contributed,s7f3a91c,Tai khoan cua quy khach se bi khoa. Xac minh tai http://vcb-xacminh.example/x7K9q,paste,VCB-Bank,brandname,2027-03,phishing,1,,1,,phishing,phishing,,,phishing,T017,test
```

Note the second row's sender: `VCB-Bank` against the real `VCB`. That is the kind of detail
`sender` carries and the published file drops — useful to the author while adjudicating, and a
narrowing field once it is public.

## 5. What happens to these files

The screenshots are deleted as soon as each transcription has been checked against its image, and
in any case before the publication date the consent form gives; they are never copied off the
machine they are transcribed on. The submission files are deleted once ingest is verified. The working file is kept by the author
for as long as the article is under review, so a reviewer's question about a label can be
answered, and is deleted when the article is published. Neither is deposited.
