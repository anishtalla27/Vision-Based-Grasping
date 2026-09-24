from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Inches as PI, Pt as PPt

TITLE = "Three Ways to Miss a Grasp: Rule-Based, Learned, and Zero-Shot Vision-Language Grasp Prediction Under One Metric"
AUTHOR = "Anish Talla"
AFFIL = "[SCHOOL NAME], [CITY, STATE]. Correspondence: [EMAIL]"

ABSTRACT = ("A robot cannot pick anything up until something decides where the fingers land and at what angle. "
"That decision can come from hand-written rules, from a network trained on labeled grasps, or from a general-purpose "
"vision-language model never trained on grasping. I built one of each and scored all three on the same 123 held-out "
"images of 35 unseen objects from the Cornell Grasping Dataset with one implementation of the standard rectangle metric [1, 2]. "
"A fine-tuned ResNet passed on 84.0% of images averaged over three seeds, a detector-plus-table heuristic on 57.7%, and "
"GPT-4o on 12.4% of 615 calls. The three failed differently: the heuristic could not express diagonal grasps, the network "
"usually got the angle and missed the placement, and GPT-4o placed its grasp center outside the region spanned by all "
"labeled grasps on 53.4% of calls against about 7% for the others. A fourth experiment showed the same model label-free "
"candidate grasps drawn on the image and asked it to pick one by number. Its accuracy stayed at the random floor on three "
"menus, and it kept choosing an end pinch along the object's long axis even when every mark was drawn the same size. "
"The failure is in the grasp choice, not in emitting coordinates.")

INTRO = [
"Before a gripper closes, something must choose a contact point, an approach angle, and an opening width. Three broadly "
"different methods can make that choice. A programmer can write the rule directly. A model can be trained on labeled "
"examples until it maps pixels to grasp rectangles. Or a vision-language model (VLM), trained on web text and images and "
"never shown a grasping dataset, can be asked in plain language where to grip. The three demand very different resources, "
"and prompting a hosted VLM needs almost none, which is exactly why it should be measured rather than assumed.",
"Published grasp-detection work mostly benchmarks within one family, and VLMs usually appear inside larger systems where "
"their own contribution cannot be isolated [3, 4]. This study puts all three families on the same test images, the same "
"output representation, and the same scoring code, and asks two questions: which approach works, and where does each "
"break down. A fourth experiment then tests the most natural explanation of the VLM's failure."]

METHODS = [
"Dataset and metric. The Cornell Grasping Dataset has 885 RGB-D images of household objects with several hand-labeled "
"grasp rectangles each [1]. Only RGB was used. A prediction passes when its angle is within 30 degrees of some labeled "
"grasp and its intersection over union (IoU) with that grasp exceeds 25% [2]. Cornell has no object identities, so I "
"reconstructed them by segmenting each frame against the photography platform and comparing consecutive masks, with "
"thresholds biased toward merging objects rather than splitting one, and a blind 30-boundary audit of the automated first "
"pass. The result is 234 objects across 883 images: 620 training, 140 validation, and 123 test images, with no object in "
"two splits. Because the 123 test images are repeated views of 35 objects, every confidence interval reported here comes "
"from 20,000 object-clustered bootstrap resamples, and paired differences use the same resamples and object-level "
"permutation tests.",
"System A, rule-based. A COCO-pretrained Faster R-CNN detects the object and a fixed table maps the category to a "
"center, upper, or end grasp; a platform-segmentation fallback supplies a box when the detector fails. It can output only "
"0 or 90 degrees. Its first test score was 40.7%. Inspecting those predictions showed detections on background clutter, "
"so a guard was added and one constant recalibrated on training data, giving 57.7%. Because test output prompted the "
"change, 57.7% is post-hoc and both numbers are reported.",
"System B, learned. ResNet18 and ResNet34 with ImageNet weights [5] were given heads for center, orientation as "
"(cos 2θ, sin 2θ), and size, with the loss taken against the best-matching label on each image. Round 1 trained each once "
"at one seed and kept the best validation checkpoint. Round 2 kept everything but the recipe: cosine decay over a fixed "
"100 epochs, an exponential moving average of weights, three seeds per architecture, no checkpoint selection, and "
"eight-view test-time augmentation. Four selection rules were written down before the test split was opened a second time.",
"System C, zero-shot VLM. GPT-4o was sent the native 640 by 480 image and asked for two fingertip coordinates and a jaw "
"width in JSON, which fix the rectangle. The prompt was developed on 30 training images and frozen. Each test image was "
"called five independent times at the provider's default temperature; replies that failed to parse were not retried.",
"System D, marked candidates. If the model can see where to grasp but cannot express it as coordinates, removing the "
"coordinate output should recover its choice [3]. Candidate grasps were generated from the segmentation mask alone: "
"principal-component analysis gives the centroid, long axis, and extent, and candidates are positions along the long axis "
"crossed with four directions 45 degrees apart, so every grasp angle is within the metric's tolerance of some candidate. "
"Marks were drawn on a zoomed crop with per-call shuffled numbers and the model returned a number. Each menu carries its "
"own floor (a uniformly random choice) and ceiling (any candidate passes). Three menus were run: twelve marks at three "
"positions; four marks at the centroid at real size; and the same four drawn at one uniform length with the prompt saying "
"length is not to scale."]

RESULTS = [
"Table 1 and Figure 1 give the headline accuracies. ResNet18 (round 1) passed 98 of 123 images; round 2's three ResNet34 "
"seeds scored 84.6, 83.7, and 83.7%, and ResNet18 under the same recipe averaged 82.6%, so round 1's nine-point gap "
"between the two architectures was run-to-run noise. The corrected heuristic passed 71 images and GPT-4o 76 of 615 "
"calls, with a best-of-five ceiling of 35.0%. Round 2 leads A by 26.3 points [14.8, 38.3] (permutation p = 0.0002), and "
"A leads C's one-call score by 45.4 points [33.8, 55.6], p < 0.0001. Weighting objects equally instead of images changed "
"the gaps but not the order.",
"The systems failed differently. Of A's 52 misses, 13 had enough overlap and missed only the angle, as expected for a "
"system limited to two orientations. B had 4 angle-only and 15 overlap-only misses, so placement was its larger problem. "
"C failed both criteria on 365 of 615 calls (59.3%). Its predicted center fell outside the convex hull of all labeled "
"grasp corners on 53.4% of parsed calls, against 7.0% for A and 6.5% for B (Figure 2). Its five calls on identical pixels "
"agreed with one another on only 22.0% of pairs.",
"System D (Table 2, Figure 3) did not recover the choice. On none of the three menus did one-call accuracy differ from a "
"random choice among the same candidates (paired differences -1.4 [-6.6, +4.0], +1.9 [-2.2, +6.3], and -2.3 [-6.3, +1.7]), "
"while the ceilings were 79.7% and 65.9%. Its choices were consistent rather than random: on the full menu it chose the "
"end pinch whose jaws travel along the object's long axis in 61% of calls, a grasp that passes 17% of the time, and with "
"four equal-size marks at the centroid it still chose the long-axis direction in 45% of calls against 25% chance. The "
"label-free centroid candidate closing across the short axis, with no model at all, scored 55.3% [41.8, 68.0], level with A."]

DISCUSSION = [
"Asking GPT-4o for raw coordinates worked poorly, and the center-hull result together with rationales that named a "
"plausible part of the object suggested a coordinate-binding failure: the model sees a region and loses it while mapping "
"the answer into pixels. System D tested that hypothesis and it failed. Taking the coordinates away and offering a menu "
"with a 79.7% ceiling did not help, and the preference for closing along the long axis survived a menu with no "
"end-straddling candidates and every mark the same size. From a top-down photograph two pads straddling the end of an "
"elongated object look like they pinch a narrow part; in three dimensions the second finger lands on top of the object. "
"The failure is better described as grasp reasoning from a single 2-D view than as text failing to bind to coordinates. "
"This does not extend to VLM grasping methods that hand the geometry to other machinery [3, 4].",
"Limits: one object-wise split of a small benchmark, RGB without depth, no robot trials, one frozen prompt for C and D "
"against a tuned learned system, a test split opened twice for B under pre-registered rules, and a post-hoc correction to "
"A. What remains untested is whether depth input or a model with a stronger three-dimensional prior changes the choice."]

ACK = ("Anthropic Claude Code (Claude 4.x models and Claude Fable 5.1, July to September 2026) assisted with code "
"development, made the first-pass calls on ambiguous object boundaries that were then audited by hand, implemented the "
"second training round and System D under my design, and helped edit this text. OpenAI Codex helped shorten an earlier "
"conference version. GPT-4o (openai/gpt-4o via OpenRouter, default temperature) is the model studied as Systems C and D; "
"its full prompts are given in the Supplement. I designed the study, made every research decision, ran and checked the "
"experiments, and approved the final text.")

REFS = [
"Y. Jiang, S. Moseson, and A. Saxena, \"Efficient grasping from RGBD images: Learning using a new rectangle representation,\" in Proc. IEEE ICRA, 2011, pp. 3304-3311.",
"I. Lenz, H. Lee, and A. Saxena, \"Deep learning for detecting robotic grasps,\" Int. J. Robot. Res., vol. 34, no. 4-5, pp. 705-724, 2015.",
"J. Yang et al., \"Set-of-Mark prompting unleashes extraordinary visual grounding in GPT-4V,\" arXiv:2310.11441, 2023.",
"M. Kulshrestha et al., \"VLAD-Grasp: Zero-shot grasp detection via vision-language models,\" arXiv:2511.05791, 2025.",
"K. He, X. Zhang, S. Ren, and J. Sun, \"Deep residual learning for image recognition,\" in Proc. IEEE CVPR, 2016, pp. 770-778.",
"J. Redmon and A. Angelova, \"Real-time grasp detection using convolutional neural networks,\" in Proc. IEEE ICRA, 2015, pp. 1316-1322.",
]

CAP1 = ("Figure 1. Test accuracy with 95% object-clustered confidence intervals. The horizontal rule on the System A bar marks its "
"40.7% pre-correction score. 'B: round 2' is the three-seed ResNet34 mean; 'C: best of 5' needs five calls and an oracle.")
CAP2 = ("Figure 2. One test image in the shared coordinate frame. Labeled grasps are green, System A red, System B blue, and "
"System C's five repeats orange.")
CAP3 = ("Figure 3. The marked image for one test object as System D saw it on the twelve-mark menu. The model chose mark 6, "
"the end pinch along the bean, on all five repeats. Mark 10 crosses the bean at its center and passes the metric.")

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
for s in doc.sections:
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(1)
def para(text, bold=False, italic=False, align=None, size=None, space_after=6):
    p = doc.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p
def heading(t):
    p = para(t, bold=True, space_after=3); p.paragraph_format.space_before = Pt(8)
para(TITLE, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=14)
para(AUTHOR, align=WD_ALIGN_PARAGRAPH.CENTER)
para(AFFIL, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=10)
heading("Abstract"); para(ABSTRACT)
heading("Introduction"); [para(x) for x in INTRO]
heading("Methods")
for x in METHODS:
    lead, rest = x.split(". ", 1); p = doc.add_paragraph(); r = p.add_run(lead + ". "); r.italic = True; p.add_run(rest); p.paragraph_format.space_after = Pt(6)
heading("Results"); [para(x) for x in RESULTS]

def table(caption, header, rows):
    para(caption, italic=True, size=10, space_after=2)
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Light Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = h; c.paragraphs[0].runs[0].bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row): cells[i].text = v
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs: r.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
table("Table 1. Test accuracy with object-clustered 95% confidence intervals.", ["System", "Accuracy", "95% CI"],
      [["A: heuristic, corrected (pre-correction 40.7%)", "57.7%", "[46.2, 68.2]"],
       ["B: ResNet18, round 1", "79.7%", "[70.8, 87.1]"],
       ["B: ResNet34, round 2, mean of 3 seeds", "84.0%", "[73.9, 92.1]"],
       ["C: GPT-4o, one call", "12.4%", "[8.0, 17.4]"],
       ["C: best of five calls", "35.0%", "[24.6, 45.5]"]])
table("Table 2. System D on three candidate menus, same model and test images, five repeats each. 'Long axis' is the share of calls choosing the orientation whose jaws travel along the object's long axis (chance 25% on four-mark menus).",
      ["Menu", "Marks", "Accuracy", "Random floor", "Ceiling", "Long axis"],
      [["Full, three positions", "12", "18.7%", "20.1%", "79.7%", "70%"],
       ["Centroid only, real size", "4", "26.5%", "24.6%", "65.9%", "41%"],
       ["Centroid only, uniform size", "4", "22.3%", "24.6%", "65.9%", "45%"]])

heading("Discussion"); [para(x) for x in DISCUSSION]
heading("Acknowledgments"); para(ACK, size=10)
heading("References")
for i, r in enumerate(REFS, 1): para(f"[{i}] {r}", size=10, space_after=2)
doc.add_page_break()
heading("Figures")
for img, cap, w in [("fig_accuracy.png", CAP1, 5.5), ("compare_0285.png", CAP2, 5.0), ("som_0129.png", CAP3, 4.5)]:
    doc.add_picture(img, width=Inches(w)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    para(cap, size=10)
doc.save("TallaAnish_paper.docx")

body_words = sum(len(x.split()) for x in [ABSTRACT] + INTRO + METHODS + RESULTS + DISCUSSION)
print("body words", body_words)

prs = Presentation(); prs.slide_width = PI(10); prs.slide_height = PI(7.5)
for img, cap, w in [("fig_accuracy.png", CAP1, 7), ("compare_0285.png", CAP2, 7), ("som_0129.png", CAP3, 5.5)]:
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_picture(img, PI((10 - w) / 2), PI(0.4), width=PI(w))
    tb = s.shapes.add_textbox(PI(0.5), PI(6.0), PI(9), PI(1.2)); tf = tb.text_frame; tf.word_wrap = True
    tf.text = cap; tf.paragraphs[0].runs[0].font.size = PPt(12)
prs.save("TallaAnish_figures.pptx")
print("saved docx and pptx")
