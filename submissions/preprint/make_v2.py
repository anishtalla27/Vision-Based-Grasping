"""Build preprint_v2.tex from preprint.tex: reviewer-driven restructure.

HISTORICAL: preprint_v2.tex has since been edited directly (tone passes).
Re-running this script would overwrite those edits.
"""
import pathlib, sys

P = pathlib.Path("/Users/anishtalla/Vision Grasp Research/submissions/preprint")
t = (P / "preprint.tex").read_text()


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70])
    t = t.replace(old, new)


def cut(start, end):
    """Remove [start, end) and return it."""
    global t
    assert t.count(start) == 1, (t.count(start), start[:70])
    i = t.index(start)
    j = t.index(end, i)
    out = t[i:j]
    t = t[:i] + t[j:]
    return out


def insert_before(marker, new):
    global t
    assert t.count(marker) == 1, (t.count(marker), marker[:70])
    t = t.replace(marker, new + marker)


# ------------------------------------------------------------------ preamble
rep(r"\pgfplotsset{compat=1.18}",
    "\\pgfplotsset{compat=1.18}\n\\usetikzlibrary{positioning,arrows.meta,calc}")
rep("% Preprint version. Build: tectonic preprint.tex",
    "% Preprint version 2 (revised after reader feedback, Sept 2026).\n"
    "% Build: tectonic preprint_v2.tex")
rep("Preprint, September 2026.", "Preprint, version 2, September 2026.")

# ------------------------------------------------------------------ abstract
cut("A robot cannot pick anything up until something decides where on the",
    "\n\\section*{Keywords}")
insert_before("\n\\section*{Keywords}", r"""A robot cannot grasp an object until something decides where to place
the fingers and at what angle. That decision can come from hand-written
rules, from a network trained on labeled grasps, or from a
general-purpose vision-language model never trained on grasping, and
the three are rarely compared under one protocol. This paper scores
one system of each kind with a single implementation of the Cornell rectangle metric on the same
held-out split of 123 images of 35 unseen objects, with
object-clustered statistics and a shared failure taxonomy. A fine-tuned
ResNet34 passed on 84.0\% of test images (three-seed mean), a
detector-plus-lookup-table heuristic on a post-hoc-corrected 57.7\%,
and zero-shot GPT-4o on 12.4\%. The systems also failed in different
ways, and GPT-4o's errors suggested that it could identify a grasp but
not express it as pixel coordinates. A follow-up experiment tested that
account by asking the same model to choose among label-free candidate
grasps drawn on the image. Its accuracy stayed at the random floor on
three candidate menus, and it consistently preferred a pinch along the
object's long axis. Removing the coordinate output does not recover
performance, which points to the grasp choice itself, although
difficulty interpreting the drawn marks cannot yet be excluded.

""")

# -------------------------------------------------------------- introduction
rep("the thing telling it where to grip is wrong",
    "the component that tells it where to grip is wrong")
rep("""I ask two questions. Which approach works, and where does each one
break down? I treat the second question as equal to the first, because""",
    """This paper asks two questions: which approach works, and where does
each one break down? The second question is treated as equal to the
first, because""")
rep("""An earlier
design would have had me write the ground truth myself and then grade
my own rule-based system against it, which is close to circular.""",
    """An earlier
design, in which the author would have written the ground truth and
then graded a rule-based system against it, was rejected as close to
circular.""")
cut("What the paper does establish is the following.",
    "% ===============================================================\n\n\\subsection{What is borrowed")
insert_before("% ===============================================================\n\n\\subsection{What is borrowed",
r"""The contributions are as follows.
\begin{enumerate}
\item A same-metric comparison of a rule-based, a learned, and a
zero-shot vision-language grasp predictor, run on the same 123 held-out
images of unseen objects through one shared scoring path.
\item Uncertainty reported at the level of the object, not the image.
The ordering of the three systems survives an object-clustered
bootstrap and permutation test, and the learned system is reported over
three seeds under selection rules fixed before the test split was
reopened.
\item A failure taxonomy and a center-hull diagnostic that separate the
three families along lines a single accuracy number does not show.
\item A marked-candidate experiment (System D) with a floor and a
ceiling computed on its own menu. It shows that removing the coordinate
output is not sufficient to recover the vision-language model's
performance, which was the most natural explanation of its failure.
\item A public release of the code, the object-wise split, and every
raw model reply.
\end{enumerate}

""")

# ------------------------------------------------------------------- methods
rep(r"\section{Methods and discussion}", r"""\section{Methods}\label{sec:methods}

Fig.~\ref{fig:overview} summarizes the design. Every system receives the
same RGB test image and must return the same kind of output, a grasp
rectangle, which is scored by one function against the dataset's
labeled grasps. This section describes the design only. All numbers are
reported in Section~\ref{sec:results} and interpreted in
Section~\ref{sec:discussion}.

\begin{figure}[H]
\centering
\begin{tikzpicture}[
  font=\small,
  box/.style={draw, rounded corners=2pt, align=center, inner sep=4pt,
              text width=3.05cm, minimum height=2.5cm},
  wide/.style={draw, rounded corners=2pt, align=center, inner sep=5pt,
               text width=14.3cm},
  arr/.style={-{Stealth[length=2mm]}, thick},
]
\node[wide] (img) {Test image (RGB, $640\times480$), object absent from training};
\node[box, below=0.9cm of img, xshift=-5.67cm] (A)
  {\textbf{System A}\\COCO detector, grasp lookup table, geometric fallback};
\node[box, right=0.45cm of A] (B)
  {\textbf{System B}\\ResNet backbone, regression head, $\sin2\theta$, $\cos2\theta$};
\node[box, right=0.45cm of B] (C)
  {\textbf{System C}\\GPT-4o, zero-shot, two fingertip points and jaw width};
\node[box, right=0.45cm of C] (D)
  {\textbf{System D}\\GPT-4o picks one of the numbered candidates drawn on the image};
\node[wide, below=0.9cm of A.south west, anchor=north west] (rect)
  {One grasp rectangle per image (center, angle, opening, jaw width)};
\node[wide, below=0.6cm of rect] (score)
  {Shared scorer: angle within $30^\circ$ and IoU above 25\% against any labeled grasp};
\node[wide, below=0.6cm of score] (out)
  {Accuracy, failure taxonomy, center-hull diagnostic, object-clustered statistics};
\foreach \s in {A,B,C,D} {
  \draw[arr] (img.south -| \s.north) -- (\s.north);
  \draw[arr] (\s.south) -- (\s.south |- rect.north);
}
\draw[arr] (rect) -- (score);
\draw[arr] (score) -- (out);
\end{tikzpicture}
\caption{Overview of the comparison. The four systems differ only in how
the grasp rectangle is produced. Everything below the system row is
shared.}
\label{fig:overview}
\end{figure}""")

# System A: post-hoc disclosure without numbers
cut("One qualification belongs here and not in Results.",
    "A second limitation follows from the table's design.")
insert_before("A second limitation follows from the table's design.",
r"""One qualification concerns the test protocol. System A was scored once
before the detector was found to be boxing background clutter. The
guard that corrected this, a requirement that the detected box contain
the object's centroid together with one constant recalibrated on
training data, was added after those test predictions had been
inspected. The decision to add it was therefore prompted by test
behavior, and the corrected figure is post-hoc, not held-out. This
weakens the comparisons that rest on it, including the McNemar test
against System B and the interval comparison against System C. Both the
original and the corrected figure are reported wherever the result
appears (Section~\ref{sec:res-a}).

""")

# System B
rep("""Validation
accuracy on 140 images swings seven to twelve points between
consecutive epochs, so that maximum is a lottery and a single run
cannot separate one architecture from another.""",
    """Validation
accuracy on 140 images varies substantially between consecutive epochs
(Section~\\ref{sec:res-b}), so the maximum over epochs is a noisy
selection criterion and a single run cannot separate one architecture
from another.""")
M_B = cut("System B's accuracy can look low next to two published Cornell results,",
          "\\subsection{System C, zero-shot vision-language model}")

# System C
rep("rectangle parameter was supplied by me, and",
    "rectangle parameter was supplied by hand, and")
cut("System C's 12.4\\% does not mean vision-language models are bad at",
    "\\subsection{System D, marked-candidate selection}")
insert_before("\\subsection{System D, marked-candidate selection}",
r"""The design isolates one step that published systems usually avoid. In
several grasping systems built on the same kind of model, the model's
output is a choice, a label, an order of operations, or an image, and
the pose of the gripper comes from something else. FreeGrasp asks the
model to decide which object to grasp and in what order, using marks
placed on the image~\cite{jiao2025}. Lan-grasp asks the model which part
to grasp, then hands the pose to a conventional
planner~\cite{mirjalili2023}. ThinkGrasp uses the model to plan clutter
removal~\cite{qian2024}. Set-of-Mark asks the model to select one of
several labeled regions~\cite{yang2024}. VLAD-Grasp asks the model to
draw the grasp using a virtual gripper~\cite{kulshrestha2025}. In none
of them does the model emit the pose coordinates itself. System C asks
for exactly that, so that any gap can then be examined as a failure of
coordinate emission or as a failure to perceive the object.

""")

# System D
rep("It also yields a fourth non-learned baseline for free, the",
    "It also yields, as a by-product, a fourth non-learned baseline, the")
insert_before("Because the menu is fixed before the model sees it, the run comes with",
r"""\begin{figure}[H]
\centering
\begin{tikzpicture}[font=\small, scale=1.25]
\fill[gray!18] (0,0) ellipse (3.6 and 0.95);
\draw[gray!60] (0,0) ellipse (3.6 and 0.95);
\draw[densely dashed, gray!70] (-4.3,0) -- (4.3,0) node[right, black] {long axis};
\foreach \x in {-2.5,0,2.5} {
  \foreach \a in {90,45,0,135} {
    \draw[black!65, semithick] ($(\x,0)+(\a:1.2)$) -- ($(\x,0)+(\a+180:1.2)$);
    \fill[black!65] ($(\x,0)+(\a:1.2)$) circle (2pt);
    \fill[black!65] ($(\x,0)+(\a+180:1.2)$) circle (2pt);
  }
  \fill[black] (\x,0) circle (1.3pt);
}
% centroid, short axis
\draw[line width=2pt] (0,1.2) -- (0,-1.2);
\fill (0,1.2) circle (2.4pt); \fill (0,-1.2) circle (2.4pt);
\node[above] at (0,1.3) {centroid, across short axis};
% end, long axis
\draw[line width=2pt, densely dashed] (1.3,0) -- (3.7,0);
\fill (1.3,0) circle (2.4pt); \fill (3.7,0) circle (2.4pt);
\node[below] at (2.9,-1.3) {end, along long axis};
\draw[-{Stealth[length=1.6mm]}] (2.9,-1.3) -- (2.9,-0.12);
\end{tikzpicture}
\caption{Schematic of the twelve-candidate menu, not to scale. The
object mask (gray) gives a centroid and a long axis. Candidates are
three positions along that axis crossed with four jaw-travel
directions, and each line joins the two fingertip pads of one
candidate. The solid candidate is the label-free geometric rule. The
dashed candidate is the end pinch discussed in
Section~\ref{sec:discussion}. The model sees the candidates drawn in
color on the photograph with shuffled numbers, as in
Fig.~\ref{fig:som}.}
\label{fig:menu}
\end{figure}

""")
cut("The prompt was developed on the same 30 training images System C used,",
    "One confound remained after that run.")
insert_before("One confound remained after that run.",
r"""The prompt was developed on the same 30 training images System C used,
two repeats each, and judged on parse rate and on whether the model was
reading the glyph as intended. The first version drew each candidate as
a thin line with small end ticks. The model frequently chose the
candidate running along the object's long axis while describing a grasp
``across the narrowest part'', which could have meant it was reading the
line as the finger plates and not as the closing direction. The second
version drew explicit pads and arrowheads and described them in the
prompt. The behavior did not change (Section~\ref{sec:res-d}), which
supports reading the test result as the model's preference and not as
an artifact of that particular glyph. Accuracy on the development
images was not used to choose between the versions. The second version
was frozen, and the test split was called once, five times per image.

""")

# Orientation -> stratified analyses + statistics
rep("\\subsection{The orientation axis}", "\\subsection{Stratified analyses}")
cut("That is why System A scores 40.0\\% on the diagonal stratum",
    "\\subsection{What this means}")
insert_before("\\subsection{What this means}",
r"""Only System A's direction on this split was predicted before the
stratum was scored.

A second split, by the number of grasps labeled per image, was examined
as a difficulty proxy, on the expectation that more labeled grasps give
a prediction more chances to match.

\subsection{Diagnostics and statistical analysis}

Two diagnostics are computed for every system from the output of the
shared scorer. The failure taxonomy records whether a missed prediction
failed the angle criterion, the overlap criterion, or both, or whether
no prediction was produced. The center-hull check asks whether each
predicted center fell inside the convex hull of an image's labeled
grasp rectangles, the loosest spatial test a prediction can fail.

Per-system accuracies carry 95\% Wilson intervals, and the paired
comparison between Systems A and B uses McNemar's exact test. System C
is tested separately for each of its five runs and the least
significant result is reported. Because the 123 test images are grouped
within 35 objects, these image-level quantities understate the
uncertainty. The primary intervals therefore resample whole objects
with replacement, differences between systems are bootstrapped on the
same resamples, and an object-clustered permutation test accompanies
each difference.

""")

# ---------------------------------------------------- pull out old discussion
D_old = cut("\\subsection{What this means}",
            "% ===============================================================\n\\section{Limitations}")
LIM = cut("% ===============================================================\n\\section{Limitations}",
          "% ===============================================================\n\\section{Results}")

# ------------------------------------------------------------------- results
rep("\\section{Results}\n\n\\subsection{The data split}",
    "\\section{Results}\\label{sec:results}\n\n\\subsection{The data split}")
insert_before("\\begin{figure}[H]\n\\centering\n\\begin{tikzpicture}\n\\begin{axis}[\n  width=0.82\\textwidth, height=7.2cm,",
r"""\subsection{Overall accuracy}

\begin{table}[H]
\centering
\caption{Test accuracy of every system on the same 123 images, with 95\%
object-clustered intervals. Systems C and D are means over five calls
per image.}
\label{tab:summary}
\begin{tabular}{lrr}
\toprule
System & Accuracy & 95\% CI \\
\midrule
A, detector and lookup table (post-hoc corrected) & 57.7\% & [46.2, 68.2] \\
A, before the correction                          & 40.7\% & --- \\
B, ResNet18, round 1, one seed                    & 79.7\% & [70.8, 87.1] \\
B, ResNet34, round 2, three seeds                 & \textbf{84.0\%} & [73.9, 92.1] \\
C, GPT-4o coordinates, one call                   & 12.4\% & [8.0, 17.4] \\
C, best of five calls                             & 35.0\% & [24.6, 45.5] \\
D, GPT-4o choosing among 12 candidates            & 18.7\% & [9.5, 29.7] \\
Label-free short-axis rule                        & 55.3\% & [41.8, 68.0] \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:summary} collects the headline numbers, and
Fig.~\ref{fig:headline} shows the three main systems.

""")
rep("""The ordering in Fig.~\\ref{fig:headline} is the paper's main result, and
the per-system subsections below give the counts behind each bar.""",
    """The ordering in Fig.~\\ref{fig:headline} is the paper's main result. The
per-system subsections below give the counts behind each bar.""")
rep("\\subsection{System A}\n\nSystem A achieved", "\\subsection{System A}\\label{sec:res-a}\n\nSystem A achieved")

REDMON = cut("System B is compared with its closest published counterpart in\nTable~\\ref{tab:redmon}.",
             "It achieved 79.7\\% on the test split (98 of 123)")
rep("\\subsection{System B}\n\n", "\\subsection{System B}\\label{sec:res-b}\n\n")
rep("It achieved 79.7\\% on the test split (98 of 123)",
    "In round 1, System B's ResNet18 achieved 79.7\\% on the test split (98 of 123)")
rep("point swings seen between epochs during training, so it isn't evidence\nof overfitting.",
    "point swings seen between consecutive epochs during training, so it is\nnot evidence of overfitting.")
rep("sometimes passed and sometimes didn't.", "sometimes passed and sometimes did not.")

rep("\\subsection{System D}\n\nSystem D chose", "\\subsection{System D}\\label{sec:res-d}\n\nSystem D chose")
rep("""Table~\\ref{tab:som} sets that against the floor and ceiling of the
same menu, and Fig.~\\ref{fig:som} shows one test image with the marks
the model saw.""",
    """Table~\\ref{tab:som} sets that against the floor and ceiling of the
same menu, and Fig.~\\ref{fig:som} shows one test image with the marks
the model saw. The paired object-clustered difference between System D
and a random choice from the same menu is $-1.4$ points [$-6.6$,
$+4.0$]. System D's gain over System C's coordinate output, 6.3 points
[$-1.6$, $+15.0$], does not exclude zero either. The geometric rule in
the fourth row is statistically level with System A's post-hoc 57.7\\%
($-2.4$ points [$-10.1$, $+5.4$]).""")
rep("across the short axis passes on 60.7\\% and was chosen 34 times.",
    """across the short axis passes on 60.7\\% and was chosen 34 times. The
model's stated confidence was ``high'' on 556 of 560 calls, of which
21\\% were correct. The same preference had appeared during prompt
development on the 30 training images, in 34 of 58 calls with the first
glyph and 41 of 58 with the redesigned one.""")
rep("points higher, so the gain belongs to the menu and not to the model.",
    """points higher, so the gain belongs to the menu and not to the model.
On the uniform-size menu the model chose the long-axis direction in
45\\% of calls against a 25\\% chance rate, and the short-axis
candidate, which passes on 55\\% of images, in 17\\%.""")

FIGSTRATA = cut("\\begin{figure}[H]\n\\centering\n\\begin{tikzpicture}\n\\begin{axis}[\n  width=0.72\\textwidth, height=7.0cm,",
                "Systems A and B agreed on 74 of 123 images")
LABELPARA = cut("All three systems did worst on the images with the most labeled grasps\n(8 to 25)",
                "\\begin{figure}[H]\n\\centering\n\\includegraphics[width=0.8\\textwidth]{compare_0285.png}")

STRATA_SEC = r"""\subsection{Orientation and label-count strata}\label{sec:res-strata}

Fig.~\ref{fig:strata} splits the test set by orientation. Relative to
the 103 axis-aligned images, System A dropped 21.2 points on the 20
diagonal images, System B gained 12.3 points, and System C moved 2.0
points. System A does not fall to zero on the diagonal stratum because
the 15 degree stratum rule is tighter than the 30 degree scoring
tolerance, so some diagonal images remain reachable by an axis-aligned
rectangle.

""" + FIGSTRATA + LABELPARA

# -------------------------------------------------- new discussion section
i = D_old.index("The sine and cosine encoding dates to 2015")
D1, D2 = D_old[:i], D_old[i:]
D1 = D1.replace("\\subsection{What this means}\n\n", "")


def drep(s, old, new):
    assert s.count(old) == 1, (s.count(old), old[:70])
    return s.replace(old, new)


D1 = drep(D1, """System D ran that test, and the prediction failed. Given a menu of
twelve candidates with a 79.7\\% ceiling, GPT-4o chose a passing grasp
on 18.7\\% of calls, against 20.1\\% for a uniformly random choice from
the same menu, a paired object-clustered difference of $-1.4$ points
[$-6.6$, $+4.0$]. Its gain over its own coordinate output, 6.3 points
[$-1.6$, $+15.0$], does not exclude zero either. Two published results""",
          """System D ran that test, and the prediction failed. Given a menu of
twelve candidates, GPT-4o chose a passing grasp no more often than a
uniformly random choice from the same menu, and its gain over its own
coordinate output does not exclude zero (Table~\\ref{tab:som}). Two
published results""")
D1 = drep(D1, "designed as a test of it, and I keep them in view because\nthey show",
          "designed as a test of it. They remain relevant because\nthey show")
j = D1.index("Even with that caveat, the contrast between VLAD-Grasp and System D")
D1 = D1[:j] + r"""Even with that caveat, the contrast between VLAD-Grasp and System D
is informative in a way System C alone was not. Both remove the
coordinate output. One works and one does not, and the one that works
also adds depth, segmentation, and a geometric pose recovery, so much
of the work in that pipeline is done by the geometry and not by the
model's choice alone. System D's failure is specific. On the full menu
the model most often chose the candidate whose jaws travel along the
object's long axis near one end, a type of grasp that rarely passes the
metric, and seldom chose the centroid candidate closing across the
short axis, which passes most often (Section~\ref{sec:res-d}). Its
reasoning for the preferred choice was typically that it ``grips the
narrow top edge near the center of mass''. From a top-down photograph,
two pads straddling the end of an elongated object do look like they
pinch a narrow part. In three dimensions the second finger would land
on top of the object and not beside it. The model reported high
confidence on nearly every call, whether or not the choice was correct.
The failure that the center-hull diagnostic exposed in System C is
therefore not explained by the coordinate output alone, and it is more
consistent with a failure of grasp reasoning from a single 2-D view.
One rendering explanation, mark size, was tested and ruled out. With
four candidates at the centroid and every mark drawn at the same size,
the model still chose the long-axis direction well above the chance
rate and the short-axis candidate below it (Table~\ref{tab:menus}). The
preference is weaker without end-straddling candidates, so part of the
full-menu result was the end-pinch illusion specifically and part is a
plain preference for closing along the long axis.

These controls do not establish that the model reads the marks as
intended. The glyph redesign and the uniform-size menu address two
specific rendering confounds, but the model could still misjudge the
direction in which a drawn candidate closes, and its description of an
end pinch as a grip on a narrow part is compatible with that. A direct
control would ask the model a purely perceptual question about the same
marks, for example which candidate closes across the object's short
axis. That question has a known answer from the candidate generator and
needs no grasp label. High accuracy on it would place the failure in
the grasp choice, and low accuracy would place it in mark
interpretation. The control has not been run, so the claim made here is
the narrower one: removing the coordinate output is not sufficient to
recover performance. The single-view setting may also matter. Zhou et
al.\ study vision-language models that must combine several agents'
egocentric views into one spatial understanding, and improve that
ability with supervised and reinforcement fine-tuning~\cite{zhou2026}.
Whether a second viewpoint, or depth, would change the grasp that
GPT-4o chooses was not tested here.

"""

D2 = drep(D2, """adds. A side result came free with the menu: a rule that closes across
the segmented object's short axis at its centroid, with no learning and
no detector, scores 55.3\\%, statistically level with System A's
post-hoc 57.7\\% ($-2.4$ points [$-10.1$, $+5.4$]), and it is the first
label-free baseline in this study that can express a diagonal grasp.""",
          """adds. A side result of the menu is a rule that closes across the
segmented object's short axis at its centroid, with no learning and no
detector. It is statistically level with System A's post-hoc figure
(Table~\\ref{tab:som}), and it is the only label-free baseline in this
study that can express a diagonal grasp.""")
D2 = drep(D2, "evidence about architecture, and the explanation that fit it was\ninvented after the fact.",
          "evidence about architecture, and the explanation that fit it was\nconstructed after the fact.")
D2 = drep(D2, """sweep confirmed that wasn't a tuning artifact. It still beat GPT-4o
(System C) by 11 points, which I did not expect to see.""",
          """sweep confirmed that this was not a tuning artifact. It still exceeded
GPT-4o (System C) by 11 points, which was not anticipated.""")
D2 = drep(D2, """Three bugs in my own code were caught before any result was reported,
each of which would have produced a plausible but wrong number. All
three turned up the same way. An automated result didn't match an
independent calculation, and neither was trusted until the disagreement
was explained.""",
          """Three defects in the evaluation code were caught before any result was
reported, each of which would have produced a plausible but wrong
number. All three were found the same way. An automated result did not
match an independent calculation, and neither was trusted until the
disagreement was explained.""")

M_B = drep(M_B, "System B's accuracy can look low next to two published Cornell results,\nbut neither is an even comparison.",
           "System B's accuracy can appear low next to two published Cornell\nresults, but neither is an even comparison.")
M_B = drep(M_B, "every pixel in a single pass. System B does nothing of the kind. It\npools",
           "every pixel in a single pass. System B instead\npools")
REDMON = REDMON.replace("System B is compared with its closest published counterpart in\nTable~\\ref{tab:redmon}.\n\n", "")
REDMON = drep(REDMON, " & Redmon and Angelova (2015) & System B (ResNet18) \\\\",
              " & Redmon and Angelova (2015) & System B \\\\")
REDMON = drep(REDMON, "Object-wise accuracy & 84.9\\% & 79.7\\% (round 1), 84.0\\% (round 2) \\\\",
              "Backbone             & AlexNet & ResNet18, then ResNet34 \\\\\n"
              "Object-wise accuracy & 84.9\\% & 79.7\\% (round 1), 84.0\\% (round 2) \\\\")

DISCUSSION = r"""% ===============================================================
\section{Discussion}\label{sec:discussion}

\subsection{From the coordinate-binding hypothesis to System D}

System C's 12.4\% does not mean that vision-language models are poor at
spatial tasks in general. Its most distinctive feature is where its
predictions land. Most of its calls failed the angle and the overlap
criterion together (Table~\ref{tab:taxonomy}), and its predicted center
fell outside the convex hull of the labeled grasps far more often than
either other system's (Table~\ref{tab:hull}). The comparison is not
quite even, since System B was trained on this distribution and System
A's center comes from a detected box or a segmentation, so both are
close to guaranteed to land on the object. System C is the only one
free to place a center anywhere. In a sample of failures, the model's
written explanation frequently named a real part of the object while
the coordinates in the same reply landed somewhere unrelated. That
reading was informal and not a blinded coding study with a fixed
rubric, so it should be treated as the observation that motivated a
hypothesis, not as a measurement of how often the pattern holds. Wang
et al.~\cite{wang2025} document the same disconnect in an unrelated
domain, with models describing a correct solution to a visual puzzle in
text, then clicking hundreds of pixels away from it (their section
5.3.2). Together these suggested that GPT-4o could see where to grasp
but could not bind that choice to pixel coordinates.

""" + D1 + r"""\subsection{Comparison with published regression results}

""" + M_B + REDMON + r"""\subsection{Orientation and label count}

The orientation split produced the pattern each design predicts
(Section~\ref{sec:res-strata}). An axis-aligned box being unable to
represent a diagonal grasp follows from the representation alone, and a
rotation-invariant encoding handling rotation is the entire reason that
encoding exists, so neither point is a discovery on its own. No
precedent was found, however, for using this split as a diagnostic. It
checks whether each system's accuracy rises or falls along an axis
defined by the dataset's own grasp-angle annotations, instead of
reporting a single train and test generalization number.

The diagonal stratum holds only 20 images, and the 95\% intervals
around System B's and System C's per-stratum accuracies are wide enough
that their point changes there are not reliably distinguishable from
noise. Only System A's drop was predicted from its representation
before the stratum was scored. Predicting a direction in advance is not
the same as confirming an effect, and no interaction test between
system and stratum was run, so this analysis remains exploratory.
System C's near-flat response is what a system with no working
orientation signal would produce.

The label-count split did not behave as a difficulty proxy. All three
systems did worst on the images with the most labeled grasps. The
likely explanation is that annotators labeled more grasps on objects
that afford more of them, so the count tracks object complexity and not
how generous the metric is.

\subsection{What the comparison adds}

""" + D2

# ---------------------------------------------------------------- limitations
LIM = drep(LIM, """after development on 30 training images and never revised. Freezing it
protected test-set integrity and I would do it again, but prompt design
is the vision-language equivalent of architecture search, and I ran
architecture search for one system and not the other.""",
           """after development on 30 training images and never revised. Freezing it
protected test-set integrity, but prompt design is the vision-language
equivalent of architecture search, and architecture search was run for
one system and not the other.""")
LIM = drep(LIM, """A different mark style, or
marks placed by a segmentation the model itself produced, was not
tested.""",
           """A different mark style, or
marks placed by a segmentation the model itself produced, was not
tested. No control measured whether the model reads the closing
direction of a mark correctly, so mark interpretation remains a
possible contributor to System D's result.""")
LIM = drep(LIM, "I checked whether GPT-4o might have seen the dataset during training.",
           "Possible exposure of GPT-4o to the dataset during training was checked.")
LIM = drep(LIM, "Jacquard,\nwhich I considered as a second dataset, was not available to me during\nthis study,",
           "Jacquard,\nconsidered as a second dataset, was not available during\nthis study,")

# ----------------------------------------------------------------- conclusion
CONC_MARK = "% ===============================================================\n\\section{Conclusion}"
cut("System A's accuracy of 57.7\\% is lower than System B's 79.7\\%",
    "% ===============================================================\n\n\\newpage\n\\begin{thebibliography}")
insert_before("% ===============================================================\n\n\\newpage\n\\begin{thebibliography}",
r"""A grasp decision can be written as rules, learned from labeled data, or
requested from a general-purpose vision-language model. These options
differ greatly in what they cost to build, and they are seldom measured
side by side. This paper built one system of each kind and scored all
of them with one implementation of the Cornell rectangle metric, on the
same 123 held-out images of 35 objects that none of them had seen,
with uncertainty computed at the level of the object.

The ordering was clear and survived every change of analysis. A
fine-tuned ResNet34 reached 84.0\% averaged over three seeds (a
single-seed ResNet18 reached 79.7\% in the first round), a detector
with a lookup table reached a post-hoc-corrected 57.7\%, and zero-shot
GPT-4o reached 12.4\%. The accuracy numbers matter less than how each
system failed. The rule-based system usually finds the object but can
only place an axis-aligned rectangle, so it loses accuracy where the
labeled grasps run diagonally. The learned system orients well, to
within about eight degrees on the grasps it gets right, and most of its
remaining error is placement. GPT-4o fails earlier than either. More
than half of its predicted centers fall outside the region spanned by
all labeled grasps, often while its own text describes a sensible part
of the object.

That pattern suggested a model that sees the right grasp and cannot
express it in pixels. The marked-candidate experiment tested that
account and did not support it. Given numbered candidates to choose
from, with a ceiling of 79.7\%, the same model performed at the random
floor of the menu on three menus, and it consistently preferred a pinch
along the object's long axis, which resembles a grip on a narrow part
from above and is not one in three dimensions. Removing the coordinate
output is therefore not sufficient to recover performance. The evidence
points to the grasp choice itself, with the qualification that the
model's reading of the drawn marks has not been separately measured.

Three practical points follow. First, a hosted vision-language model
prompted once for a grasp pose is not yet a substitute for even a simple
heuristic, which is consistent with published systems that use such
models to choose an object or a part and leave the pose to geometry.
Second, a label-free rule that closes across the short axis of the
segmented object matched the detector-based baseline and can express
diagonal grasps, which makes it a stronger cheap baseline than a lookup
table. Third, small-benchmark results are fragile. A nine-point gap
between two architectures disappeared under three seeds, and every
interval widened once images were clustered by object, so both
practices are recommended for work at this scale. The next steps are a
perceptual control on the candidate marks, depth or multi-view input,
newer models, and a second dataset.

""")

insert_before(CONC_MARK, STRATA_SEC + DISCUSSION + LIM)

# --------------------------------------------------------------- bibliography
rep("\\end{thebibliography}",
    "\\bibitem{zhou2026} H. Zhou et al., ``Ego to World: Collaborative spatial reasoning in embodied systems via reinforcement learning,'' arXiv:2603.14811, 2026.\n\\end{thebibliography}")
rep("A five-page version of this work was submitted\nto the IEEE ICDM 2026 Teen Research Symposium.",
    "A five-page version of this work was submitted\nto the IEEE ICDM 2026 Teen Research Symposium. I thank Heng Zhou and\nManav Kulshrestha for comments on the first version of this preprint,\nwhich led to the reorganization and the narrower System D claim in this\nversion.")

(P / "preprint_v2.tex").write_text(t)
print("written", len(t))
