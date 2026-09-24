"""Build the Yau report from paper.tex: same body, Yau structure, numbered citations."""
import re, pathlib
src = pathlib.Path("../../paper.tex").read_text()
start = src.index("\\section*{Abstract}")
end = src.index("\\newpage\n\\begin{center}\nWorks Cited")
body = src[start:end]

reps = [
 ("the representation Jiang et al. introduced with the Cornell\nGrasping Dataset (3304).",
  "the representation Jiang et al.~\\cite{jiang2011} introduced with the Cornell\nGrasping Dataset."),
 ("the convention established by Lenz et al.\n(712).", "the convention established by Lenz et al.~\\cite{lenz2015}."),
 ("grasp rectangles (Jiang et al.).", "grasp rectangles~\\cite{jiang2011}."),
 ("convention established by Lenz et al. Cornell's", "convention established by Lenz et al.~\\cite{lenz2015}. Cornell's"),
 ("Redmon and Angelova\n(1316) and Morrison et al. both used this same encoding.",
  "Redmon and Angelova~\\cite{redmon2015} and Morrison et al.~\\cite{morrison2018} both used this same encoding."),
 ("(Kumra et al. 9626)", "\\cite{kumra2020}"),
 ("Redmon and Angelova report 84.9\\%\nobject-wise (1316).", "Redmon and Angelova report 84.9\\%\nobject-wise~\\cite{redmon2015}."),
 ("(Jiao et al.)", "\\cite{jiao2025}"),
 ("(Mirjalili et al.)", "\\cite{mirjalili2023}"),
 ("(Qian et al.)", "\\cite{qian2024}"),
 ("regions (Yang et al.).", "regions~\\cite{yang2024}."),
 ("virtual gripper (Kulshrestha et\nal.).", "virtual gripper~\\cite{kulshrestha2025}."),
 ("Wang et al. document the same disconnect", "Wang et al.~\\cite{wang2025} document the same disconnect"),
 ("away from it (Wang et al., sec. 5.3.2).", "away from it (their section 5.3.2)."),
 ("with region selection (Yang et al.).", "with region selection~\\cite{yang2024}."),
 ("grasp instead of stating it (Kulshrestha et al.).", "grasp instead of stating it~\\cite{kulshrestha2025}."),
 ("\\section*{Abstract}", "\\section*{Abstract}\\addcontentsline{toc}{section}{Abstract}"),
]
for a, b in reps:
    assert a in body, a[:60]
    body = body.replace(a, b)
body = re.sub(r"\\section\*\{(?!Abstract)", r"\\section{", body)
body = body.replace("\\subsection*{", "\\subsection{")

contrib = r"""
\subsection{What is borrowed and what is original}

The Yau guidelines ask that original content be separated clearly from
background material, so the division is stated here once. The following
are prior work and are used, not claimed: the Cornell Grasping Dataset
and its rectangle representation~\cite{jiang2011}, the 30-degree and
25\% IoU pass rule~\cite{lenz2015}, the ResNet architectures and
ImageNet weights~\cite{he2016}, Faster R-CNN and its COCO
weights~\cite{ren2015}, the sine and cosine encoding of twice the grasp
angle~\cite{redmon2015,morrison2018}, GPT-4o itself~\cite{openai2024},
and the idea of marked-candidate prompting~\cite{yang2024}. The
following were designed, built, and run for this study: the shared
evaluation pipeline that scores every system through one implementation
of the metric, the reconstruction of object identities and the
object-wise split with its asymmetric thresholds and audit, the
detector-plus-table baseline with its guard and the disclosure of its
post-hoc correction, the training recipe, best-match loss, and
pre-registered second round for the learned system, the frozen-prompt
five-repeat protocol for the zero-shot model, the failure taxonomy and
center-hull diagnostic, the object-clustered bootstrap and permutation
analysis, the orientation stratification, and the label-free
candidate generator, three menus, floor and ceiling construction, and
uniform-size control that make up System D. The hypothesis that the
vision-language model fails at binding text to coordinates, and the
experiment that refuted it, are also this study's own.

"""
body = body.replace("\\section{Methods and discussion}", contrib + "\\section{Methods and discussion}")

preamble = r"""% Yau High School Science Award 2026, Computer Award, North America
% Research report. Build: tectonic yau_report.tex
\documentclass[12pt,letterpaper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{newtxtext,newtxmath}
\usepackage[margin=1in]{geometry}
\usepackage{setspace}
\usepackage{graphicx}
\usepackage{float}
\usepackage{caption}
\usepackage{booktabs}
\usepackage{array}
\usepackage{pgfplots}
\usepackage[hidelinks]{hyperref}
\pgfplotsset{compat=1.18}
\graphicspath{{../../figures/}{../../data/interim/comparison_sheets/}}
\captionsetup[table]{name=Table,labelsep=period,justification=raggedright,singlelinecheck=false,skip=4pt}
\captionsetup[figure]{name=Fig.,labelsep=period,justification=raggedright,singlelinecheck=false,skip=6pt}
\setlength{\parindent}{0.5in}
\title{Three Ways to Miss a Grasp}
\begin{document}
\onehalfspacing

% ---------------- Cover page ----------------
\begin{titlepage}
\centering
\vspace*{1.2in}
{\Large\bfseries 2026 S.-T. Yau High School Science Award (North America)\par}
\vspace{0.3in}
{\large Computer Award\par}
\vspace{1.0in}
{\LARGE\bfseries Three Ways to Miss a Grasp:\par}
\vspace{0.15in}
{\Large A Same-Metric Comparison of Rule-Based, Learned, and Zero-Shot
Vision-Language Grasp Prediction, and a Test of Why the Language Model Fails\par}
\vspace{1.2in}
{\large
\begin{tabular}{rl}
Student & Anish Talla \\
School & [SCHOOL NAME] \\
State, Country & [STATE], United States \\
Instructor & [INSTRUCTOR NAME, TITLE, INSTITUTION] \\
\end{tabular}\par}
\vspace{1.2in}
{\large September 2026\par}
\vfill
{\small This research report was also submitted to the IEEE ICDM 2026 Teen
Research Symposium (30 August 2026, decision pending), as disclosed at
registration.\par}
\end{titlepage}

% ---------------- Title, author, abstract, keywords ----------------
\begin{center}
{\Large\bfseries Three Ways to Miss a Grasp: A Same-Metric Comparison of
Rule-Based, Learned, and Zero-Shot Vision-Language Grasp Prediction, and a
Test of Why the Language Model Fails\par}
\vspace{0.2in}
{\large Anish Talla\par}
{[SCHOOL NAME], [STATE], United States\par}
\end{center}
\vspace{0.2in}
"""
keywords = r"""
\section*{Keywords}\addcontentsline{toc}{section}{Keywords}
robotic grasping; Cornell Grasping Dataset; convolutional neural networks;
vision-language models; GPT-4o; Set-of-Mark prompting; zero-shot evaluation;
object-clustered bootstrap; failure analysis; spatial grounding

\newpage
\tableofcontents
\newpage
"""
# insert keywords after the abstract (before Introduction)
body = body.replace("% ===============================================================\n\\section{Introduction}", keywords + "\\section{Introduction}")

bib = r"""
\newpage
\begin{thebibliography}{99}\addcontentsline{toc}{section}{Bibliography}
\bibitem{jiang2011} Y. Jiang, S. Moseson, and A. Saxena, ``Efficient grasping from RGBD images: Learning using a new rectangle representation,'' in \emph{Proc. IEEE ICRA}, 2011, pp. 3304--3311.
\bibitem{lenz2015} I. Lenz, H. Lee, and A. Saxena, ``Deep learning for detecting robotic grasps,'' \emph{Int. J. Robot. Res.}, vol. 34, nos. 4--5, pp. 705--724, 2015.
\bibitem{redmon2015} J. Redmon and A. Angelova, ``Real-time grasp detection using convolutional neural networks,'' in \emph{Proc. IEEE ICRA}, 2015, pp. 1316--1322.
\bibitem{morrison2018} D. Morrison, P. Corke, and J. Leitner, ``Closing the loop for robotic grasping: A real-time, generative grasp synthesis approach,'' in \emph{Robotics: Science and Systems XIV}, 2018.
\bibitem{kumra2020} S. Kumra, S. Joshi, and F. Sahin, ``Antipodal robotic grasping using generative residual convolutional neural network,'' in \emph{Proc. IEEE/RSJ IROS}, 2020, pp. 9626--9633.
\bibitem{he2016} K. He, X. Zhang, S. Ren, and J. Sun, ``Deep residual learning for image recognition,'' in \emph{Proc. IEEE CVPR}, 2016, pp. 770--778.
\bibitem{ren2015} S. Ren, K. He, R. Girshick, and J. Sun, ``Faster R-CNN: Towards real-time object detection with region proposal networks,'' in \emph{Adv. Neural Inf. Process. Syst.}, vol. 28, 2015.
\bibitem{openai2024} OpenAI, ``GPT-4o system card,'' arXiv:2410.21276, 2024.
\bibitem{yang2024} J. Yang et al., ``Set-of-Mark prompting unleashes extraordinary visual grounding in GPT-4V,'' arXiv:2310.11441, 2023.
\bibitem{kulshrestha2025} M. Kulshrestha et al., ``VLAD-Grasp: Zero-shot grasp detection via vision-language models,'' arXiv:2511.05791, 2025.
\bibitem{jiao2025} R. Jiao et al., ``Free-form language-based robotic reasoning and grasping,'' arXiv:2503.13082, 2025.
\bibitem{mirjalili2023} R. Mirjalili et al., ``Lan-grasp: Using large language models for semantic object grasping and placement,'' arXiv:2310.05239, 2023.
\bibitem{qian2024} Y. Qian et al., ``ThinkGrasp: A vision-language system for strategic part grasping in clutter,'' arXiv:2407.11298, 2024.
\bibitem{wang2025} J. Wang et al., ``COGNITION: From evaluation to defense against multimodal LLM CAPTCHA solvers,'' arXiv:2512.02318, 2025.
\end{thebibliography}
"""
ack = pathlib.Path("acknowledgment.tex").read_text()
out = preamble + body + bib + "\n\\newpage\n" + ack + "\n\\end{document}\n"
pathlib.Path("yau_report.tex").write_text(out)
print("wrote yau_report.tex", len(out))
