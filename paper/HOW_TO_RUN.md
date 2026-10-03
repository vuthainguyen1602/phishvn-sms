# How to build: the data article (Data in Brief)

The manuscript is `main.tex` + `sections/*.tex`, laid out like `phishvn/papers/P1_dataset`.
`OUTLINE.md` is the plan it followed and `DRAFT.md` the prose it was typeset from; edit the
LaTeX, not those.

## 1. Build

```bash
cd paper/figures && pdflatex -interaction=nonstopmode pipeline.tex && cd ..   # figures/pipeline.pdf
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex                     # second pass: refs
```

Editorial Manager builds with pdflatex, so the preamble is pdflatex-safe; `xelatex` also works.

## 2. What is still a placeholder

Every number that depends on collection, annotation or ethics approval is a `\FILL{…}` and prints
**red**. Nothing is submitted while this prints anything:

```bash
grep -n 'FILL' sections/*.tex main.tex preamble.tex
```

Where each number comes from, once the data exist:

| placeholder | produced by |
|---|---|
| message / template counts, counts at τ = 0.7 / 0.9, per-split table | `python3 scripts/sms_templates.py data/private/sms_working.csv` and `python3 scripts/sms_split.py data/private/sms_working.csv` (report modes; write nothing) |
| Cohen's κ, disagreement per class pair, share adjudicated, `uncertain` count | `python3 scripts/sms_annotate.py report` |
| external benchmark template count, no-overlap check | `sms_templates.py` report, `source = qavn` rows |
| scheme-divergence shares (benign → spam, scam → legitimate) | the model-assisted pass + hand audit described in protocol §7; record the audit sample size |
| ethics approval, licence, DOI, release tag, authors, CRediT, funding | the ethics application and the deposit; set the DOI once in `preamble.tex` (`\datadoi`) |
| references `operator2017_sms`, `kitreuse_sms`; DOI of `uci_sms` | verify against Crossref before submission |

## 3. Submission

For the Editorial Manager upload, flatten: copy `main.tex`, `preamble.tex`, every
`sections/*.tex` and `figures/pipeline.pdf` into one directory. `\graphicspath` already searches
`./`, so no edit is needed. Put the flat set in `SUBMISSION/` with the cover letter and
highlights, as the sibling papers do.
