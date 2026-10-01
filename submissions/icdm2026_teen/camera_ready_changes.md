# ICDM 2026 Teen Track camera-ready: what changed and why (S30345)

Camera-ready source: `icdm2026_teen.tex`. Built PDF: `icdm2026_teen_camera_ready.pdf`
(5 pages including references, US letter, IEEE CS `compsoc` conference class,
all fonts embedded as Type 1, no page numbers). The originally submitted version is
kept as `icdm2026_teen_v1_submitted_2026-08-30.tex` and `final_submission/icdm2026_teen.pdf`.

Build: `cd submissions/icdm2026_teen && pdflatex icdm2026_teen.tex` (run twice).

## New numbers computed for this revision

All from `scripts/object_clustered_stats_clean_a.py`, output saved in
`data/interim/object_clustered_clean_a_results.md`.

- **Clean System A per-image predictions.** Recovered by re-running the frozen table from
  commit `afcd99a` with that commit's own scripts and the committed
  `system_a_detections.csv`. It reproduces 50/123 = 40.7% exactly, matching the `afcd99a`
  commit message. The current scripts on the same data reproduce the committed
  `system_a_predictions.csv` (71/123) row for row, so the two files differ only by
  amendment 1. Saved as `data/interim/system_a_v1_predictions.csv`.
- **Clean A, object-clustered:** 40.7% [28.0, 53.2]; object-balanced 38.5%.
- **Paired tests on clean A** (20,000 bootstrap, 20,000 permutations, seed 0):
  - B (round 1) minus A: +39.0 [+25.2, +52.9], p < 0.0001
  - B (round 2) minus A: +43.4 [+29.9, +56.7], p < 0.0001
  - A minus C one-call: +28.3 [+16.9, +40.0], p = 0.0001
  - A minus C best-of-5: +5.7 [-6.1, +18.0], p = 0.45. **Does not exclude zero.** The
    old "heuristic beats GPT-4o's best-of-five ceiling" claim only held with the post-hoc
    57.7%, so the paper now says it is not a supported result.
- **Clean A failure taxonomy:** correct 50, angle only 15, overlap only 16, both 34,
  no prediction 8. Center outside labeled-grasp hull on 28/115 (24.3%), against 7.0%
  after the fix. The clutter boxes put predictions off the object.
- **System A orientation ceiling (Reviewer 4):** 103/123 (83.7%) test images have a
  labeled grasp within 15 deg of 0 or 90; 118/123 (95.9%) have one within the metric's
  30 deg, so the two-angle design rules out only 5 images by construction.

## Reviewer comment to change

| Reviewer | Comment | What the camera-ready does |
|---|---|---|
| R1.1 | Systems not on equal footing; compares pipelines | New Table 1 lists labels, scaffolding, development budget, and test runs per system. Intro says "unified" means same input, output, metric, not equal footing, and that the paper compares complete pipelines. |
| R1.2 | Coordinate-binding is speculative | System D (already run) tests it directly; Discussion 5.1 lays out three candidate explanations and what D rules out. |
| R1.3 | Object IDs depend on manual decisions, 40% agreement | Sec. 3.1 now gives 884 boundaries, 251 ambiguous, 139 decided by hand (all uncertain calls included), 112 auto-accepted only in the merge direction, and notes that 234 groups vs 240 objects fits merge-biased thresholds. |
| R2.1 | Motivation, explicit comparison with prior work | Intro rewritten around a practitioner's choice, with GR-ConvNet, Redmon and Angelova, and VLAD-Grasp numbers or protocols named, plus a contribution statement. |
| R2.2 | Too many variables; focus on one or two | Intro names the two questions the paper answers (source of grasp knowledge; choice vs. coordinate output). Table 1 makes the other differences explicit. |
| R2.3 | Practical applications | New Sec. 5.2 "Practical Implications". |
| R3.1 | Contribution is modest | Intro states plainly that the contribution is a measurement, not a new method, and lists what it is. |
| R3.2 | Stats still used post-hoc 57.7% | Every paired test now uses the clean 40.7%. 57.7% is a marked (dagger) row and column only. Taxonomy table shows both. |
| R3.3 | Narrow evaluation | Limitations rewritten (Sec. 5.3); conclusion scoped to "on this benchmark". |
| R3.4 | Different development budgets | Table 1 plus Limitations. |
| R3.5 | Acknowledgment duplicated and badly typeset; state student vs AI division | Rewritten as two labeled paragraphs, "Author's work" and "AI assistance". The broken "Section III-C" reference (compsoc numbers sections 3.3, not III-C) is gone. |
| R4.1 | Title overreach | Title now reads "...Zero-Shot Vision-Language (GPT-4o) Grasp Prediction..." and GPT-4o is in the abstract's first sentence. |
| R4.2 | Coordinate binding one of several explanations | Sec. 5.1 lists coordinate binding, coordinate-frame or scale misreading, and poor grasp choice, and says which ones D tests. |
| R4.3 | Two-orientation limit; share within 15 deg | Sec. 4.2 gives 83.7% within 15 deg, 95.9% within 30 deg, and A's accuracy on the 20 diagonal images. |
| R4.4 | 79.7% competitive with literature | Sec. 4.1: within 5.2 points of Redmon and Angelova's RGB-D single-rectangle 84.9% (0.9 in round 2), with the caveat that splits differ. |
| R4.5 | Sample size | Limitations say 35 objects and wide intervals; calls for a fresh split, cross-validation, or a second dataset. |
| R4 minor | Why 2 images dropped | Sec. 3.1: two boundaries with no lean after review; dropped pcd0435 and pcd0782 rather than guess; identity question, not annotation error. |
| R4 minor | Number of uncertain calls | 139 hand-decided boundaries, covering every uncertain call. (The exact uncertain-only count lives in `review_tracking.csv`, which is not in the repo; add it if you have it.) |
| R4 minor | Acknowledgment fragment | Fixed (see R3.5). |
| Notice | Author block format | Now: name, *High School Student*, school, location, email. |

## Things to check yourself before uploading

1. **Author block.** I used the school and email from the BigData HS submission
   (Lightridge High School and Academies of Loudoun; anish.talla99@gmail.com). The ICDM
   instructions ask for "City, Country" and the email you used on the original ICDM
   submission. Change line 17 to your city and line 18 to that email if they differ.
2. **Title.** The title now includes "(GPT-4o)". The Author Kit makes you confirm the title
   matches the portal record, so update it there too, or revert line 13 if you would
   rather keep the original title (Reviewer 4 said the abstract alone was acceptable).
3. **Acknowledgment.** Read the "Author's work" and "AI assistance" paragraphs and make sure
   every sentence is exactly true. The track requires you to be the primary contributor,
   and the chairs will read this.
4. **New citation use.** The "240 objects" figure is cited to Redmon and Angelova [3].
   Check that their dataset description says 885 images of 240 objects, the same way you
   verified the other citations.
5. **Copyright notice.** Check the Author Kit for whether you must add an IEEE copyright
   line to page 1 or whether CPS stamps it. Nothing is added now.
6. Run the PDF through PDF eXpress (Conference ID 70920X) before final upload.
