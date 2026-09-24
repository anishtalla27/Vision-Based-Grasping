# Submission packages built 13 Sept 2026

One folder per open venue. Every file is derived from the sealed results in
`data/interim/` and the text in `paper.tex` / `icdm2026_teen.tex`; no number
was changed. Square-bracket placeholders ([SCHOOL NAME], [INSTRUCTOR ...],
[EMAIL], [GRADE], [DATE]) must be filled in before submitting.

| Venue | Folder | Main file | Length | Deadline |
|---|---|---|---|---|
| Yau Computer Award | `yau2026/` | `yau_report.pdf` (from `yau_report.tex`, built by `build_yau.py` + `acknowledgment.tex`) | 31 pages: cover, title, abstract, keywords, TOC, body, bibliography on its own page, acknowledgment | 15 Sept 23:59 UTC |
| AIAS+ poster showcase | `aiasplus2026/` | `aiasplus_submission.md` (title, 250-word abstract, statement, form fields, poster plan) | abstract exactly 250 words | 18 Sept |
| UMBC/NSF REU Symposium | `bigdata2026_reu/` | `bigdata_reu.pdf` (IEEE conference template) | 5 pages, limit 6 for short paper | 18 Sept |
| IEEE BigData HS Symposium | `bigdata2026_hs/` | `bigdata_hs.pdf` (IEEE CS compsoc template, "High School Student" in affiliation) | 5 pages, limit 5 | 20 Sept, only if ICDM rejects on 18 Sept |
| Columbia Junior Science Journal | `cjsj2026/` | `TallaAnish_paper.docx`, `TallaAnish_figures.pptx`, `TallaAnish_cover_letter.md`, `TallaAnish_supplement_prompts.md` | body about 1,440 words, three figures, two tables, six references | 30 Sept |

## Per-venue notes

Yau. Fill the cover page (school, state, instructor) and the two bracketed
sentences in the Acknowledgment (instructor role; exact Claude model names).
Still needed from you, not producible here: the signed Declaration of
Academic Integrity (their form), a plagiarism-check report on the final
PDF (under 10% similarity), exported Claude Code transcripts and the raw
GPT-4o log as "Other Materials", and the prior-submission disclosure at
registration (ICDM Teen, 30 Aug 2026). Source code and a short pipeline
video are optional but recommended.

AIAS+. Paste the title, abstract, and statement into the form; add the
chaperone. The poster is only built if accepted on 5 Oct; the plan is in the
file.

BigData HS. Do not submit while ICDM Teen is under review. If ICDM rejects
on 18 Sept, submit this on 19 or 20 Sept through the CyberChair link in
`venue_requirements_2026-09-13.md`. If ICDM accepts, do not submit.

REU Symposium. Same proceedings as the HS symposium; pick one. This version
has fuller methods (identity reconstruction, System C configuration,
orientation strata) and results (round-2 table, repeat consistency,
McNemar, System D agreement) than the HS version. Fill school, city, email.

CJSJ. The paper is in CJSJ's structure (title, author, abstract,
introduction, methods, results, discussion, acknowledgments, numbered IEEE
references, figures on a separate page and again in the pptx). Their
official .docx template was not downloaded (that needs your go-ahead), so
before submitting, paste the sections into
`CJSJ-Original-Research-Template-1-faxy.docx` from their guidelines page,
sign the Permission to Publish form as `TallaAnish_form.pdf` (mentor
signature if you have one), and check the body fits their 2-3 page count in
the template's font. Rename the pptx to `.ppt` if their portal insists.
