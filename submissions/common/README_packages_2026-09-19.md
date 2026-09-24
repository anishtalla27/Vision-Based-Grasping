# Ready-to-submit packages, 19 Sept 2026

Only two venues are active now: IEEE BigData 2026 High School Symposium and the Columbia Junior Science Journal. Yau, AIAS+, and the REU Symposium folders are kept but not being submitted.

## IEEE BigData HS Symposium (due 20 Sept 2026)
- Upload `bigdata2026_hs/bigdata_hs.pdf`. Five pages, US letter, IEEE Computer Society format, fonts embedded, "High School Student" plus school in the author block.
- Source: `bigdata_hs.tex`. The text before the humanizing pass is `bigdata_hs_pre_humanize.tex`.
- Portal: https://wi-lab.com/cyberchair/2026/bigdata26/scripts/submit.php?subarea=SP19&undisplay_detail=1&wh=/cyberchair/2026/bigdata26/scripts/ws_submit.php
- Do not submit if the ICDM Teen paper (decision was due 18 Sept) is still under review or was accepted. The symposium forbids concurrent submission of the same paper.

## CJSJ (due 30 Sept 2026)
- `cjsj2026/TallaAnish_paper.docx`: built inside the official CJSJ Original Research template. Four pages in total, with the text alone inside the 2 to 3 page limit. `TallaAnish_paper_preview.pdf` is a Pages render for checking only.
- `cjsj2026/TallaAnish_figures.pptx`: built inside the official figures template (3 figures, 2 tables).
- `cjsj2026/TallaAnish_form_TO_SIGN.pdf`: official Permission to Publish form with the student section typed in. Print, sign (parent too if under 18, mentor if any), scan, save as `TallaAnish_form.pdf`.
- `cjsj2026/TallaAnish_cover_letter.md`: two bracketed notes to resolve (ICDM decision, mentor).
- Submit at https://columbiajuniorsciencejournal.org/submit
- Rebuild with `python3 build_cjsj_template.py` and `python3 build_cjsj_figures.py`; the text lives in `cjsj_text.py`.
